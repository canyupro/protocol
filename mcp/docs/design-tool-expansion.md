# MCP Tool 扩展施工设计

> 状态：施工就绪
> 目标：在现有 3 个 MCP tool 基础上，新增 4 个 L2 tool
> 施工目录：F:\docs\SOP\mcp\

---

## 现有架构概览

```
mcp/
├── mcp_server/
│   ├── __init__.py
│   ├── server.py      # FastMCP tool 定义（现有 4 个 tool）
│   ├── store.py       # SQLite 持久化（3 张表 + CRUD 函数）
│   ├── checker.py     # 证据校验逻辑
│   └── models.py      # Pydantic 模型 + 枚举
├── tests/             # 3 个测试文件，36 个测试
└── docs/
```

现有模式：
- `models.py` 定义 Request/Result Pydantic 模型 + 枚举
- `checker.py` 放校验逻辑函数，返回 `tuple[bool, str]`
- `store.py` 放 SQLite CRUD，每张表有 `log_xxx` + `get_xxx`
- `server.py` 注册 `@mcp.tool()` 函数，构造 Request -> 校验 -> 记录 -> 返回 Result

---

## 新增 4 个 Tool

### Tool 1: enforce_timebox（时间盒硬约束）

**规则对应**: §4.6 时间盒 + 红灯分级

**两段式语义**（与 pause/resume 模式一致）：

#### start_timebox

```python
@mcp.tool()
def start_timebox(
    step_id: str,        # 步骤标识，如 "R6-chain1-task-001"
    max_minutes: int,    # 超时阈值
    risk_level: str,     # "normal" | "high"
) -> dict[str, object]:
    """启动一个时间盒计时器。同一 step_id 重复调用 -> 报错。"""
```

校验逻辑：
- step_id 非空
- max_minutes > 0
- risk_level in {"normal", "high"}
- step_id 不已存在于 timebox_log 且 status=ACTIVE

返回：`{timer_id, step_id, max_minutes, risk_level, started_at, started, message}`

#### check_timebox

```python
@mcp.tool()
def check_timebox(
    step_id: str,    # 要检查的步骤标识
) -> dict[str, object]:
    """检查时间盒是否超时。计算 elapsed = now - started_at。"""
```

校验逻辑：
- step_id 存在且 status=ACTIVE
- 计算 elapsed_minutes
- exceeded = elapsed_minutes > max_minutes
- 更新 SQLite 记录 checked_at + exceeded + status

返回：`{timer_id, step_id, max_minutes, elapsed_minutes, exceeded, risk_level, message}`

risk_level 决定红灯轮数（normal=5 轮, high=2 轮），但轮数由协议层管，tool 只记录 risk_level。

#### SQLite 表

```sql
CREATE TABLE IF NOT EXISTS timebox_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    step_id TEXT NOT NULL,
    max_minutes INTEGER NOT NULL,
    risk_level TEXT NOT NULL,
    started_at TEXT NOT NULL,
    checked_at TEXT,
    elapsed_minutes REAL,
    exceeded INTEGER,
    status TEXT NOT NULL DEFAULT 'ACTIVE'  -- ACTIVE | CHECKED
)
```

#### models.py 新增

```python
class RiskLevel(str, Enum):
    NORMAL = "normal"
    HIGH = "high"

class StartTimeboxRequest(BaseModel):
    step_id: str
    max_minutes: int
    risk_level: RiskLevel

class StartTimeboxResult(BaseModel):
    timer_id: int
    step_id: str
    max_minutes: int
    risk_level: RiskLevel
    started_at: str
    started: bool
    message: str

class CheckTimeboxResult(BaseModel):
    timer_id: int
    step_id: str
    max_minutes: int
    elapsed_minutes: float
    exceeded: bool
    risk_level: RiskLevel
    message: str
```

#### store.py 新增

```python
def log_timebox_start(step_id, max_minutes, risk_level) -> int
def get_active_timebox(step_id) -> dict | None
def log_timebox_check(timer_id, elapsed_minutes, exceeded) -> None
```

---

### Tool 2: validate_coverage（覆盖率硬校验）

**规则对应**: T9.3 "覆盖率低于 70% -> 标红" + 验收锁 V7

#### 单次调用

```python
@mcp.tool()
def validate_coverage(
    cov_output: str,        # pytest --cov-report=term 的完整输出
    threshold: float = 70.0,
) -> dict[str, object]:
    """解析 pytest 覆盖率输出，校验 TOTAL 行 ≥ threshold。"""
```

校验逻辑：
- cov_output 非空
- 正则提取 `TOTAL` 行的覆盖率百分比：`r"TOTAL\s+\d+\s+\d+\s+(\d+(?:\.\d+)?)%"`
- 找不到 TOTAL 行 -> reject
- coverage_percent < threshold -> accepted=False
- coverage_percent >= threshold -> accepted=True

返回：`{accepted, coverage_percent, threshold, total_line, message}`

#### SQLite 表

```sql
CREATE TABLE IF NOT EXISTS coverage_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    coverage_percent REAL,
    threshold REAL,
    accepted INTEGER NOT NULL,
    checked_at TEXT NOT NULL
)
```

#### models.py 新增

```python
class ValidateCoverageResult(BaseModel):
    accepted: bool
    coverage_percent: float
    threshold: float
    total_line: str
    message: str
```

#### checker.py 新增

```python
def parse_coverage(cov_output: str) -> tuple[float, str] | None:
    """解析 pytest --cov-report=term 输出，返回 (coverage_percent, total_line)。失败返回 None。"""
```

---

### Tool 3: verify_freeze（冻结项变更检测）

**规则对应**: T9.6 "链路 Agent 修改了 core/ router.py 等公共文件 -> 标红"

#### 单次调用

```python
@mcp.tool()
def verify_freeze(
    frozen_files: list[str],   # 硬冻结文件路径列表（相对路径）
) -> dict[str, object]:
    """校验当前 git 改动是否触及硬冻结文件。"""
```

校验逻辑：
- frozen_files 非空
- 执行 `git diff --name-only HEAD` 获取当前改动文件列表
- 检查 frozen_files 中是否有文件出现在改动列表中
- 违规文件列表 -> violated_files

返回：`{accepted, frozen_count, changed_count, violated_files, message}`

accepted = (len(violated_files) == 0)

#### SQLite 表

```sql
CREATE TABLE IF NOT EXISTS freeze_check_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    frozen_count INTEGER,
    changed_count INTEGER,
    violated_files_json TEXT,
    accepted INTEGER NOT NULL,
    checked_at TEXT NOT NULL
)
```

#### models.py 新增

```python
class VerifyFreezeResult(BaseModel):
    accepted: bool
    frozen_count: int
    changed_count: int
    violated_files: list[str]
    message: str
```

#### checker.py 新增

```python
def get_changed_files() -> list[str]:
    """执行 git diff --name-only HEAD，返回改动文件列表。"""

def check_freeze_violation(frozen_files: list[str], changed_files: list[str]) -> list[str]:
    """返回 frozen_files 中出现在 changed_files 里的文件列表。"""
```

---

### Tool 4: snapshot_check（继承快照完整性校验）

**规则对应**: §4.12 继承快照 + 07 号文件 §三

#### 单次调用

```python
@mcp.tool()
def snapshot_check(
    snapshot_path: str,    # 继承快照文件路径（相对 PROJECT_ROOT）
) -> dict[str, object]:
    """校验继承快照是否包含所有必填字段。"""
```

必填字段（在快照 markdown 中搜索）：
1. `workflow_state` - 工作流状态段
2. `当前角色` 或 `Current role` - 角色字段
3. `任务阶段` 或 `Task stage` - 阶段字段
4. `已冻结决策` 或 `Frozen Decision` - 冻结决策段
5. `待定项` 或 `Pending` - 待定项段
6. `下一步` 或 `Next Step` - 下一步段

校验逻辑：
- snapshot_path 非空
- 文件存在
- 逐个检查必填字段是否存在（字符串搜索）
- 返回缺失字段列表

返回：`{accepted, snapshot_path, total_fields, found_fields, missing_fields, message}`

accepted = (len(missing_fields) == 0)

#### SQLite 表

```sql
CREATE TABLE IF NOT EXISTS snapshot_check_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_path TEXT NOT NULL,
    total_fields INTEGER,
    found_fields INTEGER,
    missing_fields_json TEXT,
    accepted INTEGER NOT NULL,
    checked_at TEXT NOT NULL
)
```

#### models.py 新增

```python
class SnapshotCheckResult(BaseModel):
    accepted: bool
    snapshot_path: str
    total_fields: int
    found_fields: int
    missing_fields: list[str]
    message: str
```

#### checker.py 新增

```python
REQUIRED_SNAPSHOT_FIELDS = [
    "workflow_state",
    ("当前角色", "Current role"),
    ("任务阶段", "Task stage"),
    ("已冻结决策", "Frozen Decision"),
    ("待定项", "Pending"),
    ("下一步", "Next Step"),
]

def check_snapshot_completeness(snapshot_path: Path) -> tuple[list[str], list[str]]:
    """返回 (found_fields, missing_fields)。"""
```

---

## 施工约束

### 可修改文件

- `mcp/mcp_server/models.py` - 新增 4 组 Request/Result 模型 + RiskLevel 枚举
- `mcp/mcp_server/server.py` - 新增 5 个 @mcp.tool() 函数
- `mcp/mcp_server/store.py` - 新增 4 张表 + CRUD 函数
- `mcp/mcp_server/checker.py` - 新增校验逻辑函数
- `mcp/tests/test_mcp_timebox.py` - 新建测试文件
- `mcp/tests/test_mcp_coverage.py` - 新建测试文件
- `mcp/tests/test_mcp_freeze.py` - 新建测试文件
- `mcp/tests/test_mcp_snapshot.py` - 新建测试文件

### 不可修改

- `mcp/mcp_server/__init__.py`
- `mcp/tests/test_mcp_mark_checked.py`
- `mcp/tests/test_mcp_pause_for_user.py`
- `mcp/tests/test_mcp_report_step.py`
- `mcp/docs/` 下所有文件

### 编码规范

- 与现有代码风格一致：`from __future__ import annotations`，类型注解，docstring
- Pydantic v2 BaseModel
- SQLite 用 `sqlite3` 标准库，`conn.row_factory = sqlite3.Row`
- 时间戳用 `datetime.now(timezone.utc).isoformat()`
- PROJECT_ROOT = `Path(__file__).resolve().parent.parent`（checker.py 已有）

### 测试要求

每个 tool 至少 8 个测试，覆盖：
1. 正常调用 -> accepted=True
2. 参数缺失/空 -> accepted=False
3. 边界值（threshold 刚好等于、刚好不等于）
4. 异常输入（格式错误、文件不存在）
5. SQLite 记录验证

测试文件头加 `@pytest.fixture(autouse=True)` 清空 DB（与现有测试一致）。

### init_db 更新

`store.py` 的 `init_db()` 函数需要加 4 张新表的 `CREATE TABLE IF NOT EXISTS`。

---

## 施工顺序

1. `models.py` - 先加模型（其他文件依赖）
2. `checker.py` - 加校验逻辑
3. `store.py` - 加表 + CRUD
4. `server.py` - 加 tool 函数
5. 4 个测试文件
6. `python -B -m pytest mcp/tests/ -v` 全绿
