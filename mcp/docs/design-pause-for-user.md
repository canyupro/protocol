# MCP pause_for_user 详细设计（Phase 2 / 可施工级）

> 分支：feature/protocol-mcp
> 调度方：ZCode（主会话）| 执行方：DeepSeek（分叉会话）
> 日期：2026-07-03
> 状态：S1 产出，待执行方施工
> 上游规格：`docs/_sop-snapshot/v3.0/MCP服务器设计建议.md` §3.2 tool 2

---

## 0. 执行方读这里

你是执行方。读继承快照 `docs/_handoff/mcp-experiment-snapshot.md` 的 `workflow_state` 段确认角色后，按本文件施工。

**施工范围**：仅修改 `mcp_server/server.py`（加 tool）+ `mcp_server/models.py`（加模型）+ `mcp_server/store.py`（加表）+ 新建 `tests/test_mcp_pause_for_user.py`。不动 `backend/` `frontend/` `docs/` 既有文件。

**验收标准**：§7 的 AC-1 ~ AC-8 全部通过。

---

## 1. 设计难点与决策（已冻结）

### 难点：MCP stdio tool 调用是同步的，不能阻塞等用户回复

MCP tool 在 stdio 传输下是「调用 → 返回」的同步模式。`pause_for_user` 不能真的阻塞线程等用户输入——那样会卡死 MCP server 进程。

### 决策：两段式语义

`pause_for_user` 不做「暂停并阻塞」，而是做「记录暂停请求 + 返回分叉选项」：

```
AI 调用 pause_for_user(forks, context)
  → tool 校验 forks 合法性
  → 记录到 SQLite（状态=PAUSED）
  → 返回 {paused: True, forks: [...], message: "请用户在分叉选项中选择"}
  → AI 客户端收到返回值，应停止产出，把 forks 展示给用户
  → 用户做出选择后，AI 用选择结果调用 resume_from_pause(choice)
  → resume_from_pause 校验 choice 在 forks 内
  → 更新 SQLite（状态=RESUMED + 记录选择）
  → 返回 {resumed: True, choice: "..."}
  → AI 继续产出
```

**关键**：tool 不强制阻塞——它返回 `paused=True` 后，**约束 AI 不继续产出**这件事靠客户端/规程层保证，不靠 tool 阻塞线程。这和 mark_checked 一样：tool 做校验和记录，不做强制拦截（强制拦截需要客户端配合）。

### 为什么不阻塞

1. MCP stdio server 是单线程的，阻塞会卡死整个 server。
2. 「AI 不继续产出」是行为约束，应该在客户端/规程层实现（如客户端收到 `paused=True` 后停止向模型发送请求）。
3. tool 的职责是「记录 + 校验 + 返回结构化结果」，不是「控制线程」。

---

## 2. 数据模型（models.py 追加）

```python
class ForkOption(BaseModel):
    """分叉选项。"""
    option: str = Field(..., description="选项描述，如 '继续修复'")
    risk: str = Field(..., description="风险等级: LOW / MEDIUM / HIGH")


class PauseRequest(BaseModel):
    """pause_for_user tool 的入参。"""
    forks: list[ForkOption] = Field(..., description="分叉选项列表，至少 2 项")
    context: str = Field(..., description="为什么需要暂停")


class PauseResult(BaseModel):
    """pause_for_user tool 的返回。"""
    paused: bool
    forks: list[ForkOption]
    context: str
    message: str
    pause_id: int  # SQLite 记录 ID，供 resume 引用


class ResumeRequest(BaseModel):
    """resume_from_pause tool 的入参。"""
    pause_id: int = Field(..., description="pause_for_user 返回的 pause_id")
    choice: str = Field(..., description="用户选择的 option 文本")


class ResumeResult(BaseModel):
    """resume_from_pause tool 的返回。"""
    resumed: bool
    pause_id: int
    choice: str
    message: str
```

**注意**：ForkOption / PauseRequest / PauseResult / ResumeRequest / ResumeResult 追加到 models.py 现有 EvidenceType / MarkCheckedRequest / MarkCheckedResult 之后，不删不改现有模型。

---

## 3. 存储层（store.py 追加）

新增 `pause_log` 表：

```python
def init_pause_db() -> None:
    """初始化 pause_log 表。幂等。"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pause_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            context TEXT NOT NULL,
            forks_json TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'PAUSED',
            choice TEXT,
            paused_at TEXT NOT NULL,
            resumed_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def log_pause(req: PauseRequest) -> int:
    """记录一次暂停请求，返回 pause_id。"""
    import json
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.execute(
        "INSERT INTO pause_log (context, forks_json, status, paused_at) VALUES (?, ?, 'PAUSED', ?)",
        (req.context, json.dumps([f.model_dump() for f in req.forks], ensure_ascii=False),
         datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    pause_id = cursor.lastrowid
    conn.close()
    return pause_id


def log_resume(pause_id: int, choice: str) -> bool:
    """记录用户的选择，更新状态为 RESUMED。返回是否成功。"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.execute(
        "UPDATE pause_log SET status='RESUMED', choice=?, resumed_at=? WHERE id=? AND status='PAUSED'",
        (choice, datetime.now(timezone.utc).isoformat(), pause_id),
    )
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


def get_pause(pause_id: int) -> dict[str, object] | None:
    """查询单条暂停记录。"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM pause_log WHERE id=?", (pause_id,)).fetchone()
    conn.close()
    return dict(row) if row else None
```

**注意**：`init_db()` 函数里追加调用 `init_pause_db()`，或在 server.py 启动时追加调用。不删现有 `mark_checked_log` 表逻辑。

---

## 4. Server tool（server.py 追加）

```python
@mcp.tool()
def pause_for_user(
    forks: list[dict],
    context: str,
) -> dict[str, object]:
    """
    在策略分叉点强制暂停，把决策权交还用户。
    AI 不能自行选择分叉，必须调用本 tool 后等待用户拍板。

    调用后 AI 应停止产出，把 forks 展示给用户。
    用户做出选择后，调用 resume_from_pause(pause_id, choice) 恢复。

    Args:
        forks: 分叉选项列表，每项含 option(描述) 和 risk(LOW/MEDIUM/HIGH)，至少 2 项
        context: 为什么需要暂停

    Returns:
        dict: {paused, forks, context, message, pause_id}
    """
    # 校验 forks
    if not forks or len(forks) < 2:
        return PauseResult(
            paused=False,
            forks=[],
            context=context,
            message="分叉选项至少需要 2 项，否则不是分叉",
            pause_id=-1,
        ).model_dump()

    # 构造 ForkOption 列表
    try:
        fork_options = [ForkOption(**f) for f in forks]
    except Exception as e:
        return PauseResult(
            paused=False,
            forks=[],
            context=context,
            message=f"分叉选项格式错误: {e}",
            pause_id=-1,
        ).model_dump()

    # 校验 risk 值
    valid_risks = {"LOW", "MEDIUM", "HIGH"}
    for fo in fork_options:
        if fo.risk not in valid_risks:
            return PauseResult(
                paused=False,
                forks=fork_options,
                context=context,
                message=f"risk 必须是 LOW/MEDIUM/HIGH，实际: {fo.risk}",
                pause_id=-1,
            ).model_dump()

    req = PauseRequest(forks=fork_options, context=context)

    # 记录
    pause_id = log_pause(req)

    return PauseResult(
        paused=True,
        forks=fork_options,
        context=context,
        message="已暂停。请用户在分叉选项中选择，然后调用 resume_from_pause",
        pause_id=pause_id,
    ).model_dump()


@mcp.tool()
def resume_from_pause(
    pause_id: int,
    choice: str,
) -> dict[str, object]:
    """
    用户做出分叉选择后恢复执行。

    Args:
        pause_id: pause_for_user 返回的 pause_id
        choice: 用户选择的 option 文本

    Returns:
        dict: {resumed, pause_id, choice, message}
    """
    # 校验 pause_id 存在且处于 PAUSED 状态
    record = get_pause(pause_id)
    if record is None:
        return ResumeResult(
            resumed=False,
            pause_id=pause_id,
            choice=choice,
            message=f"pause_id={pause_id} 不存在",
        ).model_dump()

    if record["status"] != "PAUSED":
        return ResumeResult(
            resumed=False,
            pause_id=pause_id,
            choice=choice,
            message=f"pause_id={pause_id} 状态为 {record['status']}，非 PAUSED，不可重复恢复",
        ).model_dump()

    # 校验 choice 在原 forks 内
    import json
    forks_data = json.loads(record["forks_json"])
    valid_options = [f["option"] for f in forks_data]
    if choice not in valid_options:
        return ResumeResult(
            resumed=False,
            pause_id=pause_id,
            choice=choice,
            message=f"choice '{choice}' 不在分叉选项内: {valid_options}",
        ).model_dump()

    # 记录恢复
    success = log_resume(pause_id, choice)

    return ResumeResult(
        resumed=success,
        pause_id=pause_id,
        choice=choice,
        message="已恢复执行" if success else "恢复失败",
    ).model_dump()
```

**注意**：两个 tool 追加到 server.py 现有 `mark_checked` 之后。需要 import 新模型（ForkOption / PauseRequest / PauseResult / ResumeRequest / ResumeResult）和新 store 函数（log_pause / log_resume / get_pause）。不删不改现有 mark_checked tool。

---

## 5. 校验逻辑要点

| 校验点 | 规则 | 失败返回 |
|---|---|---|
| forks 至少 2 项 | `len(forks) < 2` | paused=False |
| forks 格式 | 每项含 option + risk 字段 | paused=False |
| risk 值合法 | 必须是 LOW/MEDIUM/HIGH | paused=False |
| context 非空 | `not context.strip()` | paused=False |
| pause_id 存在 | get_pause 返回 None | resumed=False |
| pause_id 状态 | 必须是 PAUSED | resumed=False |
| choice 在 forks 内 | choice 必须匹配某个 option 文本 | resumed=False |

---

## 6. 测试要求（tests/test_mcp_pause_for_user.py）

**最低 8 个单测**：

```python
import pytest
from mcp_server.models import ForkOption, PauseRequest
from mcp_server.server import pause_for_user, resume_from_pause
from mcp_server.store import DB_PATH, init_db, get_pause


@pytest.fixture(autouse=True)
def clean_state_db():
    if DB_PATH.exists():
        os.remove(DB_PATH)
    init_db()
    yield
    if DB_PATH.exists():
        os.remove(DB_PATH)


class TestPauseForUser:
    def test_valid_pause_with_two_forks(self):
        """AC-1: 2 个合法分叉 → paused=True"""
        ...

    def test_pause_with_three_forks(self):
        """AC-2: 3 个分叉 → paused=True"""
        ...

    def test_pause_rejects_single_fork(self):
        """AC-3: 只有 1 个分叉 → paused=False"""
        ...

    def test_pause_rejects_empty_forks(self):
        """AC-4: forks 为空 → paused=False"""
        ...

    def test_pause_rejects_invalid_risk(self):
        """AC-5: risk 不是 LOW/MEDIUM/HIGH → paused=False"""
        ...


class TestResumeFromPause:
    def test_valid_resume(self):
        """AC-6: 合法 choice 恢复 → resumed=True"""
        # 先 pause_for_user 拿 pause_id，再 resume
        ...

    def test_resume_rejects_invalid_choice(self):
        """AC-7: choice 不在 forks 内 → resumed=False"""
        ...

    def test_resume_rejects_nonexistent_pause_id(self):
        """AC-8: pause_id 不存在 → resumed=False"""
        ...

    def test_resume_rejects_double_resume(self):
):        """AC-9(加分): 同一 pause_id 恢复两次 → 第二次 resumed=False"""
        ...

    def test_pause_returns_pause_id(self):
        """AC-10(加分): pause_for_user 返回 pause_id 且 > 0"""
        ...
```

---

## 7. 验收标准（AC）

| AC | 内容 | 验证方式 |
|---|---|---|
| AC-1 | 2 个合法分叉 → paused=True | test_valid_pause_with_two_forks |
| AC-2 | 3 个分叉 → paused=True | test_pause_with_three_forks |
| AC-3 | 只有 1 个分叉 → paused=False | test_pause_rejects_single_fork |
| AC-4 | forks 为空 → paused=False | test_pause_rejects_empty_forks |
| AC-5 | risk 非法 → paused=False | test_pause_rejects_invalid_risk |
| AC-6 | 合法 choice 恢复 → resumed=True | test_valid_resume |
| AC-7 | choice 不在 forks 内 → resumed=False | test_resume_rejects_invalid_choice |
| AC-8 | pause_id 不存在 → resumed=False | test_resume_rejects_nonexistent_pause_id |

**验收命令**（执行方施工完跑，粘到交付报告）：

```powershell
python -B -m pytest tests/test_mcp_pause_for_user.py -v
python -m uv run ruff check mcp_server/ tests/test_mcp_pause_for_user.py
git log -1 --oneline
```

---

## 8. 施工约束（不可越边界）

| 约束 | 说明 |
|---|---|
| ❌ 不改 backend/ frontend/ docs/ scripts/ alembic/ 既有文件 | |
| ❌ 不改 pyproject.toml | 不加依赖 |
| ❌ 不删 mark_checked 相关代码 | 追加，不替换 |
| ❌ 不碰 §4.4 项 | |
| ✅ 修改 mcp_server/models.py | 追加 5 个模型 |
| ✅ 修改 mcp_server/store.py | 追加 pause_log 表 + 3 个函数 |
| ✅ 修改 mcp_server/server.py | 追加 2 个 tool |
| ✅ 新建 tests/test_mcp_pause_for_user.py | ≥8 单测 |
| ✅ git commit 到 feature/protocol-mcp | |

---

## 9. 完工后执行方必做

1. 跑验收命令，确保全绿。
2. 更新继承快照 `docs/_handoff/mcp-experiment-snapshot.md`：
   - `施工方已完成: 是`
   - `最近 commit: {hash}`
   - `任务阶段: 待验收`
   - 粘贴验收命令输出
3. 告知调度方（ZCode 主会话）可以终验了。
