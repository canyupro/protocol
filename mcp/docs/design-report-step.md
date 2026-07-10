# MCP report_step 详细设计（Phase 3 / 可施工级）

> 分支：feature/protocol-mcp
> 调度方：ZCode（主会话）| 执行方：DeepSeek（分叉会话）
> 日期：2026-07-03
> 状态：S1 产出，待执行方施工
> 上游规格：`docs/_sop-snapshot/v3.0/MCP服务器设计建议.md` §3.2 tool 3

---

## 0. 执行方读这里

你是执行方。读继承快照 `docs/_handoff/mcp-experiment-snapshot.md` 的 `workflow_state` 段确认角色后，按本文件施工。

**施工范围**：
1. 修改 `mcp_server/models.py`（追加模型）+ `mcp_server/store.py`（追加表/函数）+ `mcp_server/server.py`（追加 1 tool）
2. 新建 `tests/test_mcp_report_step.py`（≥8 单测）
3. **清理 Phase 2 遗留小问题**（见 §8）

**验收标准**：§7 的 AC-1 ~ AC-8 全部通过 + 全量回归 36 passed。

---

## 1. 设计要点（已冻结）

### 核心目标：把冗长报告压缩为结构化记录（对应 D5 决策成本转嫁）

v2.0 的决策记录/§8 模板让 AI 每轮堆「自我证明在按规程做事」的噪声，有效信号比 < 10%。report_step 把报告压缩为 4 个必填字段（phase / content / artifacts / step_seq），强制 ≤ 500 字，削减噪声。

### step_seq 自动递增

每次调用 report_step，step_seq 从 SQLite 自增。这样：
- 步骤有全局序号，可追溯。
- 「不调用不能 commit」可校验：commit 前必须有对应 step_seq 的 report_step 记录。

### artifacts 校验

artifacts 是产出文件路径列表。校验每个路径存在——防止 AI 报告了不存在的文件（对应 D5 噪声）。

---

## 2. 数据模型（models.py 追加）

```python
class ReportPhase(str, Enum):
    """报告阶段枚举。"""
    READ = "read"        # 阅读
    PLAN = "plan"        # 方案
    IMPLEMENT = "implement"  # 实现
    TEST = "test"        # 测试
    WRAP_UP = "wrap_up"  # 收尾


class ReportStepRequest(BaseModel):
    """report_step tool 的入参。"""
    phase: ReportPhase = Field(..., description="阶段: read/plan/implement/test/wrap_up")
    content: str = Field(..., description="本步骤实际产出摘要，≤500 字")
    artifacts: list[str] = Field(..., description="产出文件路径列表")


class ReportStepResult(BaseModel):
    """report_step tool 的返回。"""
    step_seq: int           # 自增步骤序号
    phase: ReportPhase
    content: str
    artifacts: list[str]
    reported_at: str        # ISO8601 时间戳
    accepted: bool
    message: str
```

**注意**：ReportPhase / ReportStepRequest / ReportStepResult 追加到 models.py 现有所有模型之后，不删不改现有模型。

---

## 3. 存储层（store.py 追加）

新增 `step_log` 表：

```python
# 文件顶部追加 import（清理 Phase 2 遗留：把 json/datetime 从函数内提到顶部）
import json
from datetime import datetime, timezone


def init_step_db() -> None:
    """初始化 step_log 表。幂等。"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS step_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phase TEXT NOT NULL,
            content TEXT NOT NULL,
            artifacts_json TEXT NOT NULL,
            reported_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def log_step(req: ReportStepRequest) -> int:
    """记录一次步骤报告，返回 step_seq。"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.execute(
        "INSERT INTO step_log (phase, content, artifacts_json, reported_at) VALUES (?, ?, ?, ?)",
        (req.phase.value, req.content,
         json.dumps(req.artifacts, ensure_ascii=False),
         datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    step_seq = cursor.lastrowid
    conn.close()
    return step_seq


def get_step(step_seq: int) -> dict[str, object] | None:
    """查询单条步骤记录。"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM step_log WHERE id=?", (step_seq,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_step_count() -> int:
    """查询步骤总数。"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.execute("SELECT COUNT(*) FROM step_log")
    count = cursor.fetchone()[0]
    conn.close()
    return count
```

**注意**：
- `init_db()` 里追加 `step_log` 建表（合并到一次 init，和 Phase 2 合并 pause_log 一样的方式）。
- `log_pause` / `log_resume` 里的 `import json` / `from datetime import ...` 删掉（改为用文件顶部的 import）——这是 Phase 2 遗留清理。
- `server.py` 的 `resume_from_pause` 里的 `import json` 也删掉，改用顶部 import。

---

## 4. Server tool（server.py 追加）

```python
@mcp.tool()
def report_step(
    phase: str,
    content: str,
    artifacts: list[str],
) -> dict[str, object]:
    """
    报告一个规程步骤的完成。不调用本 tool 不允许进入下一步 / 不允许 commit。
    把「自我证明在按规程做事」的噪声压缩为结构化记录。

    Args:
        phase: 阶段，可选值: read / plan / implement / test / wrap_up
        content: 本步骤实际产出摘要，≤500 字
        artifacts: 产出文件路径列表

    Returns:
        dict: {step_seq, phase, content, artifacts, reported_at, accepted, message}
    """
    # 校验 phase
    try:
        report_phase = ReportPhase(phase)
    except ValueError:
        valid = [p.value for p in ReportPhase]
        return ReportStepResult(
            step_seq=-1,
            phase=ReportPhase.READ,
            content=content,
            artifacts=artifacts,
            reported_at=datetime.now(timezone.utc).isoformat(),
            accepted=False,
            message=f"phase 无效: {phase}，可选: {valid}",
        ).model_dump()

    # 校验 content 非空
    if not content.strip():
        return ReportStepResult(
            step_seq=-1,
            phase=report_phase,
            content=content,
            artifacts=artifacts,
            reported_at=datetime.now(timezone.utc).isoformat(),
            accepted=False,
            message="content 不能为空",
        ).model_dump()

    # 校验 content ≤ 500 字
    if len(content) > 500:
        return ReportStepResult(
            step_seq=-1,
            phase=report_phase,
            content=content,
            artifacts=artifacts,
            reported_at=datetime.now(timezone.utc).isoformat(),
            accepted=False,
            message=f"content 超过 500 字（实际 {len(content)} 字），请压缩",
        ).model_dump()

    # 校验 artifacts 非空
    if not artifacts:
        return ReportStepResult(
            step_seq=-1,
            phase=report_phase,
            content=content,
            artifacts=artifacts,
            reported_at=datetime.now(timezone.utc).isoformat(),
            accepted=False,
            message="artifacts 不能为空，至少 1 个产出文件",
        ).model_dump()

    # 校验 artifacts 路径存在
    from .checker import PROJECT_ROOT  # 复用已有的 PROJECT_ROOT
    missing = []
    for art in artifacts:
        if not (PROJECT_ROOT / art).exists():
            missing.append(art)
    if missing:
        return ReportStepResult(
            step_seq=-1,
            phase=report_phase,
            content=content,
            artifacts=artifacts,
            reported_at=datetime.now(timezone.utc).isoformat(),
            accepted=False,
            message=f"artifacts 路径不存在: {missing}",
        ).model_dump()

    req = ReportStepRequest(phase=report_phase, content=content, artifacts=artifacts)

    # 记录
    step_seq = log_step(req)

    return ReportStepResult(
        step_seq=step_seq,
        phase=report_phase,
        content=content,
        artifacts=artifacts,
        reported_at=datetime.now(timezone.utc).isoformat(),
        accepted=True,
        message=f"步骤 {step_seq} 已记录（phase={report_phase.value}）",
    ).model_dump()
```

**注意**：
- report_step 追加到 server.py 现有 `resume_from_pause` 之后。
- 需要追加 import：`ReportPhase` / `ReportStepRequest` / `ReportStepResult` / `log_step`。
- `server.py` 顶部追加 `import json`（清理 Phase 2 遗留），`resume_from_pause` 里的 `import json` 删掉。

---

## 5. 校验逻辑要点

| 校验点 | 规则 | 失败返回 |
|---|---|---|
| phase 在枚举内 | read/plan/implement/test/wrap_up | accepted=False, step_seq=-1 |
| content 非空 | `not content.strip()` | accepted=False |
| content ≤ 500 字 | `len(content) > 500` | accepted=False |
| artifacts 非空 | `not artifacts` | accepted=False |
| artifacts 路径存在 | 每个路径在 PROJECT_ROOT 下存在 | accepted=False |

---

## 6. 测试要求（tests/test_mcp_report_step.py）

**最低 8 个单测**：

```python
import os
import pytest
from mcp_server.models import ReportPhase
from mcp_server.server import report_step
from mcp_server.store import DB_PATH, get_step, get_step_count, init_db


@pytest.fixture(autouse=True)
def clean_state_db():
    if DB_PATH.exists():
        os.remove(DB_PATH)
    init_db()
    yield
    if DB_PATH.exists():
        os.remove(DB_PATH)


class TestReportStep:
    def test_valid_report(self):
        """AC-1: 合法报告 → accepted=True, step_seq>0"""
        # phase=implement, content="实现 mark_checked", artifacts=["mcp_server/server.py"]
        ...

    def test_step_seq_auto_increments(self):
        """AC-2: 连续报告 → step_seq 递增"""
        # 调用 3 次，验证 step_seq 递增
        ...

    def test_invalid_phase_rejected(self):
        """AC-3: phase 不在枚举 → accepted=False"""
        # phase="invalid_phase"
        ...

    def test_empty_content_rejected(self):
        """AC-4: content 为空 → accepted=False"""
        ...

    def test_content_over_500_chars_rejected(self):
        """AC-5: content >500 字 → accepted=False"""
        # content = "x" * 501
        ...

    def test_empty_artifacts_rejected(self):
        """AC-6: artifacts 为空 → accepted=False"""
        ...

    def test_nonexistent_artifact_rejected(self):
        """AC-7: artifact 路径不存在 → accepted=False"""
        # artifacts=["nonexistent/file.py"]
        ...

    def test_step_logged_to_sqlite(self):
        """AC-8: 调用后 SQLite 有记录"""
        # 调用 report_step，然后 get_step(step_seq) 验证记录存在
        ...

    def test_get_step_count(self):
        """AC-9(加分): get_step_count 返回正确数量"""
        # 调用 3 次，验证 count=3
        ...

    def test_all_phases_accepted(self):
        """AC-10(加分): 5 种 phase 都 accepted=True"""
        # read/plan/implement/test/wrap_up 各调一次
        ...
```

---

## 7. 验收标准（AC）

| AC | 内容 | 验证方式 |
|---|---|---|
| AC-1 | 合法报告 → accepted=True, step_seq>0 | test_valid_report |
| AC-2 | 连续报告 → step_seq 递增 | test_step_seq_auto_increments |
| AC-3 | phase 不在枚举 → accepted=False | test_invalid_phase_rejected |
| AC-4 | content 为空 → accepted=False | test_empty_content_rejected |
| AC-5 | content >500 字 → accepted=False | test_content_over_500_chars_rejected |
| AC-6 | artifacts 为空 → accepted=False | test_empty_artifacts_rejected |
| AC-7 | artifact 路径不存在 → accepted=False | test_nonexistent_artifact_rejected |
| AC-8 | 调用后 SQLite 有记录 | test_step_logged_to_sqlite |

**验收命令**（执行方施工完跑，粘到交付报告）：

```powershell
python -B -m pytest tests/test_mcp_report_step.py -v
python -B -m pytest tests/test_mcp_mark_checked.py tests/test_mcp_pause_for_user.py tests/test_mcp_report_step.py -v
python -m uv run ruff check mcp_server/ tests/
git log -1 --oneline
```

第二条命令是全量回归——确保 Phase 3 清理 + 追加不破坏 Phase 1/2。

---

## 8. Phase 2 遗留清理（本次必做）

Phase 2 终验发现的小问题，本次施工一并清理：

| 问题 | 文件 | 清理方式 |
|---|---|---|
| `log_pause` 函数内 `import json` + `from datetime import ...` | store.py | 删函数内 import，用文件顶部 import |
| `log_resume` 函数内 `from datetime import ...` | store.py | 同上 |
| `resume_from_pause` 函数内 `import json` | server.py | 删函数内 import，用文件顶部 import |
| `init_pause_db()` 定义了但未被调用（死代码） | store.py | 删除 `init_pause_db()` 函数（`init_db()` 已内联建表） |

**清理后 store.py 顶部应有**：
```python
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .models import MarkCheckedRequest, MarkCheckedResult, PauseRequest, ReportStepRequest
```

**清理后 server.py 顶部应有**：
```python
import json  # 新增（Phase 3 清理）
from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP
# ... 其他现有 import
```

**清理约束**：清理后 Phase 1 + Phase 2 测试必须仍然全绿（25 passed）。

---

## 9. 施工约束（不可越边界）

| 约束 | 说明 |
|---|---|
| ❌ 不改 backend/ frontend/ docs/ scripts/ alembic/ 既有文件 | |
| ❌ 不改 pyproject.toml | 不加依赖 |
| ❌ 不删 mark_checked / pause_for_user / resume_from_pause 相关代码 | 追加 + 清理，不替换 |
| ❌ 不碰 §4.4 项 | |
| ✅ 修改 mcp_server/models.py | 追加 3 个模型 |
| ✅ 修改 mcp_server/store.py | 追加 step_log 表 + 3 函数 + 清理 Phase 2 import |
| ✅ 修改 mcp_server/server.py | 追加 1 tool + 清理 Phase 2 import |
| ✅ 新建 tests/test_mcp_report_step.py | ≥8 单测 |
| ✅ git commit 到 feature/protocol-mcp | |

---

## 10. 完工后执行方必做

1. 跑验收命令（含全量回归），确保全绿。
2. 更新继承快照 `docs/_handoff/mcp-experiment-snapshot.md`：
   - `施工方已完成: 是`
   - `最近 commit: {hash}`
   - `任务阶段: 待验收`
   - 粘贴验收命令输出（含全量回归 36 passed）
3. 告知调度方（ZCode 主会话）可以终验了。
