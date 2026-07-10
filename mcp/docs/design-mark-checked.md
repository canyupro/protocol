# MCP mark_checked 详细设计（Phase 1 / 可施工级）

> 分支：feature/protocol-mcp
> 调度方：ZCode（主会话）| 执行方：DeepSeek（分叉会话）
> 日期：2026-07-03
> 状态：S1 产出，待执行方施工
> 上游规格：`docs/_sop-snapshot/v3.0/MCP服务器设计建议.md` §3.2

---

## 0. 执行方读这里

你是执行方。读继承快照 `docs/_handoff/mcp-experiment-snapshot.md` 的 `workflow_state` 段确认角色后，按本文件施工。

**施工范围**：仅 `mcp_server/` 新目录 + `tests/test_mcp_mark_checked.py`。不动 `backend/` `frontend/` `docs/` 既有文件。

**验收标准**：§5 的 AC-1 ~ AC-8 全部通过。

---

## 1. 技术栈确认（已冻结）

| 项 | 值 | 来源 |
|---|---|---|
| MCP SDK | `mcp==1.28.1`（已装） | 实测 `import mcp` 通过 |
| Server 框架 | `FastMCP`（`from mcp.server.fastmcp import FastMCP`） | 实测可用 |
| Python | 3.10+ | pyproject.toml |
| 传输 | stdio | MCP 设计建议 §3.3 |
| 存储 | SQLite（`mcp_server/state.db`，记录调用历史） | MCP 设计建议 §3.3 |
| 测试 | pytest + pytest-asyncio | 项目已有 |

**禁止新增依赖**：mcp 已在环境里，不需要改 pyproject.toml。若施工中发现缺包，先报调度方，不自行 `pip install`。

---

## 2. 目录结构

```
mcp_server/
├── __init__.py
├── server.py              # FastMCP 实例 + tool 注册 + 启动入口
├── checker.py             # 证据校验逻辑（纯函数，可单测）
├── store.py               # SQLite 调用历史存储
└── models.py              # Pydantic 数据模型
tests/
└── test_mcp_mark_checked.py  # 单测（校验逻辑 + tool 行为）
```

**禁止改动**：`backend/` `frontend/` `docs/` `scripts/` `alembic/` 下任何既有文件。

---

## 3. 数据模型（models.py）

```python
from pydantic import BaseModel, Field
from enum import Enum


class EvidenceType(str, Enum):
    """证据类型，决定校验方式。"""
    PYTEST = "pytest"
    RUFF = "ruff"
    GIT_LOG = "git_log"
    SCREENSHOT = "screenshot"
    REVIEW = "review"


class MarkCheckedRequest(BaseModel):
    """mark_checked tool 的入参。"""
    item_id: str = Field(..., description="AC 编号或任务编号，如 AC-F20-1")
    evidence_url: str = Field(..., description="证据路径，如 tests/test_k12_facts.py::TestHistoryRecallIntent")
    evidence_type: EvidenceType = Field(..., description="证据类型")


class MarkCheckedResult(BaseModel):
    """mark_checked tool 的返回。"""
    item_id: str
    accepted: bool
    reason: str
    checked_at: str  # ISO8601 时间戳
    evidence_type: EvidenceType
    evidence_url: str
```

---

## 4. 证据校验逻辑（checker.py）

这是核心。**纯函数，无副作用，可单测**。

```python
from pathlib import Path
from .models import EvidenceType, MarkCheckedRequest
import subprocess
import re


# 项目根目录（mcp_server/ 的父目录）
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def validate_evidence(req: MarkCheckedRequest) -> tuple[bool, str]:
    """
    校验证据是否有效。返回 (accepted, reason)。

    校验规则按 evidence_type 分发：
    - PYTEST: 校验 evidence_url 里的 test 函数在文件中存在（grep）
    - RUFF: 校验 evidence_url 指向的文件存在
    - GIT_LOG: 校验 commit hash 真实（git rev-parse --verify）
    - SCREENSHOT: 校验文件存在于 docs/ 下
    - REVIEW: 不做机器校验，accepted=True（人工 review 无法机器验证）
    """
    if not req.item_id.strip():
        return False, "item_id 不能为空"

    if not req.evidence_url.strip():
        return False, "evidence_url 不能为空"

    if req.evidence_type == EvidenceType.PYTEST:
        return _validate_pytest(req.evidence_url)
    elif req.evidence_type == EvidenceType.RUFF:
        return _validate_ruff(req.evidence_url)
    elif req.evidence_type == EvidenceType.GIT_LOG:
        return _validate_git_log(req.evidence_url)
    elif req.evidence_type == EvidenceType.SCREENSHOT:
        return _validate_screenshot(req.evidence_url)
    elif req.evidence_type == EvidenceType.REVIEW:
        return True, "人工 review 类型，不做机器校验"
    else:
        return False, f"未知 evidence_type: {req.evidence_type}"


def _validate_pytest(evidence_url: str) -> tuple[bool, str]:
    """
    校验格式：path/to/test_xxx.py::TestClassName 或 path/to/test_xxx.py::test_func_name
    校验逻辑：文件存在 + 测试目标（类名或函数名）在文件中 grep 到。
    """
    # 解析 file::target
    match = re.match(r"^(.+\.py)::(.+)$", evidence_url)
    if not match:
        return False, f"PYTEST 证据格式应为 path/file.py::TestName，实际: {evidence_url}"

    file_rel, target = match.group(1), match.group(2)
    file_path = PROJECT_ROOT / file_rel

    if not file_path.exists():
        return False, f"测试文件不存在: {file_path}"

    # grep target 在文件中
    content = file_path.read_text(encoding="utf-8")
    # 匹配 "class TestName" 或 "def test_func"
    if target.startswith("Test"):
        pattern = rf"class\s+{re.escape(target)}\b"
    else:
        pattern = rf"def\s+{re.escape(target)}\b"

    if re.search(pattern, content):
        return True, f"PYTEST 证据有效: {file_rel}::{target}"
    else:
        return False, f"在 {file_rel} 中未找到测试目标: {target}"


def _validate_ruff(evidence_url: str) -> tuple[bool, str]:
    """校验 evidence_url 指向的文件存在。"""
    file_path = PROJECT_ROOT / evidence_url
    if file_path.exists():
        return True, f"RUFF 证据有效: {evidence_url}"
    return False, f"文件不存在: {file_path}"


def _validate_git_log(evidence_url: str) -> tuple[bool, str]:
    """校验 commit hash 真实。evidence_url 是 commit hash（7 或 40 位）。"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--verify", evidence_url],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return True, f"GIT_LOG 证据有效: {evidence_url}"
        return False, f"commit hash 无效: {evidence_url}"
    except subprocess.TimeoutExpired:
        return False, "git rev-parse 超时"
    except FileNotFoundError:
        return False, "git 命令不可用"


def _validate_screenshot(evidence_url: str) -> tuple[bool, str]:
    """校验截图文件存在于 docs/ 下。"""
    file_path = PROJECT_ROOT / evidence_url
    if file_path.exists() and "docs/" in str(file_path):
        return True, f"SCREENSHOT 证据有效: {evidence_url}"
    return False, f"截图文件不存在或不在 docs/ 下: {file_path}"
```

---

## 5. 存储层（store.py）

SQLite 记录每次 mark_checked 调用，用于复盘。

```python
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from .models import MarkCheckedRequest, MarkCheckedResult

DB_PATH = Path(__file__).resolve().parent / "state.db"


def init_db() -> None:
    """初始化 SQLite 表。幂等。"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS mark_checked_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id TEXT NOT NULL,
            evidence_url TEXT NOT NULL,
            evidence_type TEXT NOT NULL,
            accepted INTEGER NOT NULL,
            reason TEXT NOT NULL,
            checked_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def log_call(req: MarkCheckedRequest, result: MarkCheckedResult) -> None:
    """记录一次 mark_checked 调用。"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO mark_checked_log (item_id, evidence_url, evidence_type, accepted, reason, checked_at) VALUES (?, ?, ?, ?, ?, ?)",
        (req.item_id, req.evidence_url, req.evidence_type.value, int(result.accepted), result.reason, result.checked_at),
    )
    conn.commit()
    conn.close()


def get_history(item_id: str | None = None) -> list[dict]:
    """查询调用历史。item_id 为 None 时返回全部。"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    if item_id:
        rows = conn.execute("SELECT * FROM mark_checked_log WHERE item_id = ? ORDER BY id DESC", (item_id,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM mark_checked_log ORDER BY id DESC LIMIT 100").fetchall()
    conn.close()
    return [dict(r) for r in rows]
```

---

## 6. Server 入口（server.py）

```python
from datetime import datetime, timezone
from mcp.server.fastmcp import FastMCP
from .models import EvidenceType, MarkCheckedRequest, MarkCheckedResult
from .checker import validate_evidence
from .store import init_db, log_call

# 初始化 MCP server
mcp = FastMCP("protocol-mcp")


@mcp.tool()
def mark_checked(
    item_id: str,
    evidence_url: str,
    evidence_type: str,
) -> dict:
    """
    标记一个 AC / 任务为完成。必须附带证据。
    无证据或证据不可达 → reject，不允许标完成。

    Args:
        item_id: AC 编号或任务编号，如 "AC-F20-1"
        evidence_url: 证据路径，如 "tests/test_k12_facts.py::TestHistoryRecallIntent"
        evidence_type: 证据类型，可选值: pytest / ruff / git_log / screenshot / review

    Returns:
        dict: {item_id, accepted, reason, checked_at, evidence_type, evidence_url}
    """
    # 构造请求
    try:
        req = MarkCheckedRequest(
            item_id=item_id,
            evidence_url=evidence_url,
            evidence_type=EvidenceType(evidence_type),
        )
    except ValueError as e:
        return MarkCheckedResult(
            item_id=item_id,
            accepted=False,
            reason=f"evidence_type 无效: {evidence_type}，可选: {[e.value for e in EvidenceType]}",
            checked_at=datetime.now(timezone.utc).isoformat(),
            evidence_type=EvidenceType.REVIEW,
            evidence_url=evidence_url,
        ).model_dump()

    # 校验
    accepted, reason = validate_evidence(req)

    # 记录
    result = MarkCheckedResult(
        item_id=item_id,
        accepted=accepted,
        reason=reason,
        checked_at=datetime.now(timezone.utc).isoformat(),
        evidence_type=req.evidence_type,
        evidence_url=evidence_url,
    )
    log_call(req, result)

    return result.model_dump()


if __name__ == "__main__":
    init_db()
    mcp.run(transport="stdio")
```

---

## 7. 测试要求（tests/test_mcp_mark_checked.py）

**最低 8 个单测**，覆盖以下场景。执行方可以加更多但不能少于 8。

```python
# 测试文件骨架，执行方填充实现

import pytest
from mcp_server.models import EvidenceType, MarkCheckedRequest
from mcp_server.checker import validate_evidence
from mcp_server.store import init_db, log_call, get_history
from mcp_server.server import mark_checked


class TestValidatePytest:
    def test_valid_pytest_class_target(self):
        """AC-1: PYTEST 证据，类目标存在 → accepted=True"""
        # 用项目内真实测试文件，如 tests/test_k12_facts.py::TestNormalizeSubject
        ...

    def test_valid_pytest_func_target(self):
        """AC-2: PYTEST 证据，函数目标存在 → accepted=True"""
        ...

    def test_invalid_pytest_file_not_exist(self):
        """AC-3: PYTEST 证据，文件不存在 → accepted=False"""
        ...

    def test_invalid_pytest_target_not_found(self):
        """AC-4: PYTEST 证据，目标在文件中找不到 → accepted=False"""
        ...


class TestValidateGitLog:
    def test_valid_git_commit_short(self):
        """AC-5: GIT_LOG 证据，7位 hash 真实 → accepted=True"""
        # 用 git log 拿一个真实 hash
        ...

    def test_invalid_git_commit(self):
        """AC-6: GIT_LOG 证据，假 hash → accepted=False"""
        ...


class TestValidateOther:
    def test_review_type_always_accepted(self):
        """AC-7: REVIEW 类型不做机器校验 → accepted=True"""
        ...

    def test_empty_item_id_rejected(self):
        """AC-8: item_id 为空 → accepted=False"""
        ...


class TestServerTool:
    def test_mark_checked_tool_returns_dict(self):
        """AC-9(加分): tool 调用返回 dict 且含 accepted 字段"""
        ...

    def test_mark_checked_logs_to_sqlite(self):
        """AC-10(加分): 调用后 SQLite 有记录"""
        ...
```

---

## 8. 验收标准（AC）

| AC | 内容 | 验证方式 |
|---|---|---|
| AC-1 | PYTEST 证据，类目标存在 → accepted=True | test_valid_pytest_class_target |
| AC-2 | PYTEST 证据，函数目标存在 → accepted=True | test_valid_pytest_func_target |
| AC-3 | PYTEST 证据，文件不存在 → accepted=False | test_invalid_pytest_file_not_exist |
| AC-4 | PYTEST 证据，目标找不到 → accepted=False | test_invalid_pytest_target_not_found |
| AC-5 | GIT_LOG 真实 hash → accepted=True | test_valid_git_commit_short |
| AC-6 | GIT_LOG 假 hash → accepted=False | test_invalid_git_commit |
| AC-7 | REVIEW 类型 → accepted=True | test_review_type_always_accepted |
| AC-8 | item_id 为空 → accepted=False | test_empty_item_id_rejected |

**验收命令**（执行方施工完跑，粘到交付报告）：

```powershell
python -B -m pytest tests/test_mcp_mark_checked.py -v
python -m uv run ruff check mcp_server/ tests/test_mcp_mark_checked.py
git log -1 --oneline
```

---

## 9. 施工约束（不可越边界）

| 约束 | 说明 |
|---|---|
| ❌ 不改 backend/ | MCP 是独立模块 |
| ❌ 不改 frontend/ | 无关 |
| ❌ 不改 docs/ 既有文件 | 规程文档不动 |
| ❌ 不改 pyproject.toml | mcp 已装，不加依赖 |
| ❌ 不碰 §4.4 项 | 无 DB 结构/RBAC/心理健康/政策来源变更 |
| ✅ 新建 mcp_server/ 目录 | 4 个文件 |
| ✅ 新建 tests/test_mcp_mark_checked.py | ≥8 单测 |
| ✅ git commit 到 feature/protocol-mcp | 每个可验证产出 commit 一次 |

---

## 10. 完工后执行方必做

1. 跑验收命令，确保全绿。
2. 更新继承快照 `docs/_handoff/mcp-experiment-snapshot.md`：
   - `施工方已完成: 是`
   - `最近 commit: {hash}`
   - `任务阶段: 待验收`
3. 在快照里粘贴验收命令输出（pytest 尾部 + ruff 输出 + git log）。
4. 告知调度方（ZCode 主会话）可以终验了。
