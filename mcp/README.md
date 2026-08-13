# Protocol MCP Server

> MCP (Model Context Protocol) tools implementing L2 hard constraints for the Parallel Development Protocol v3.0.
>
> 规程 MCP 服务器：实现 v3.0 规程 L2 工具层约束的 MCP server。

## What It Does

Nine tools (7 function groups) that enforce protocol rules that weak models tend to skip at the text layer:

| Tool | Rule Enforced | Mechanism |
|---|---|---|
| `mark_checked` | Evidence-gated AC completion (Acceptance Lock V7/V9) | No evidence or unreachable evidence → reject |
| `pause_for_user` + `resume_from_pause` | Strategy fork pause (§4.6) | Forks ≥ 2, records PAUSED state in SQLite |
| `report_step` | Step report compression + commit gate (§4.12) | content ≤ 500 chars, artifacts must exist |
| `start_timebox` + `check_timebox` | Timebox red-light escalation | Timer per step_id, `check_timebox` flags exceed |
| `validate_coverage` | Coverage gate | Parses `pytest --cov` TOTAL line, rejects below threshold |
| `verify_freeze` | Hard-freeze protection | Intersects frozen files with `git diff --relative HEAD` |
| `snapshot_check` | Inheritance snapshot completeness | All required fields (bilingual) must exist |

See protocol File 06 (`zh/06-约束介质与MCP.md` / `en/06-Constraint-Media-and-MCP.md`) for the full L0/L1/L2 design rationale.

## Quick Start

```bash
# Install dependencies (editable, so `cwd` is not required at client config)
pip install -e .

# Run the server (stdio mode)
python -B -m mcp_server.server
```

### Client Configuration (ZCode / similar)

```json
{
  "protocol-mcp": {
    "command": "<python_path>",
    "args": ["-B", "-m", "mcp_server.server"],
    "cwd": "<this_directory>"
  }
}
```

## Run Tests

```bash
cd mcp/
python -B -m pytest tests/ -v
# 70 tests across 7 files (14 + 11 + 11 + 10 + 8 + 8 + 8)
```

## Directory Structure

```
mcp/
├── README.md                          # This file
├── pyproject.toml                     # Dependency lock (mcp>=2,<3 / pydantic>=2,<3)
├── mcp_server/                        # Server source code
│   ├── __init__.py
│   ├── server.py                      # MCPServer, 9 tool definitions
│   ├── store.py                       # SQLite persistence layer (7 tables)
│   ├── checker.py                     # Evidence / coverage / freeze / snapshot validation
│   └── models.py                      # Pydantic request/result models
├── tests/                             # 70 unit tests across 7 files
│   ├── test_mcp_mark_checked.py       # 14 tests
│   ├── test_mcp_pause_for_user.py     # 11 tests
│   ├── test_mcp_report_step.py        # 11 tests
│   ├── test_mcp_timebox.py            # 10 tests
│   ├── test_mcp_coverage.py           # 8 tests
│   ├── test_mcp_freeze.py             # 8 tests
│   └── test_mcp_snapshot.py           # 8 tests
└── docs/                              # Design docs + experiment records
    ├── server-design-suggestion.md    # MCP necessity analysis + 3-phase design
    ├── design-mark-checked.md         # Construction-ready design for mark_checked
    ├── design-pause-for-user.md       # Construction-ready design for pause_for_user
    ├── design-report-step.md          # Construction-ready design for report_step
    ├── design-tool-expansion.md       # Phase 4 tool expansion design
    ├── experiment-snapshot.md         # Inheritance snapshot for experiment
    ├── experiment-report.md           # State machine experiment report
    └── integration-guide.md           # MCP integration documentation
```

## Tool API Reference

### mark_checked

```python
mark_checked(
    item_id: str,           # AC number / task ID, e.g. "AC-F20-1"
    evidence_url: str,      # Evidence path, e.g. "tests/test_k12_facts.py::TestHistoryRecallIntent"
    evidence_type: str,     # pytest | ruff | git_log | screenshot | review
) -> dict:
    # Returns: {item_id, accepted, reason, checked_at, evidence_type, evidence_url}
```

### pause_for_user + resume_from_pause

```python
pause_for_user(
    forks: list[dict],      # [{"option": "...", "risk": "LOW|MEDIUM|HIGH"}, ...] - at least 2
    context: str,           # Why pause is needed
) -> dict:
    # Returns: {paused, forks, context, message, pause_id}

resume_from_pause(
    pause_id: int,          # From pause_for_user return
    choice: str,            # User's chosen option text (must be in forks)
) -> dict:
    # Returns: {resumed, pause_id, choice, message}
```

### report_step

```python
report_step(
    phase: str,             # read | plan | implement | test | wrap_up
    content: str,           # Output summary, ≤500 chars
    artifacts: list[str],   # Output file paths (must exist)
) -> dict:
    # Returns: {step_seq, phase, content, artifacts, reported_at, accepted, message}
```

### start_timebox + check_timebox

```python
start_timebox(
    step_id: str,           # Step identifier, e.g. "R6-chain1-task-001"
    max_minutes: int,       # Timeout threshold (minutes)
    risk_level: str,        # normal | high (determines red-light rounds: normal=5, high=2)
) -> dict:
    # Returns: {timer_id, step_id, max_minutes, risk_level, started_at, started, message}

check_timebox(
    step_id: str,           # Step identifier to check
) -> dict:
    # Returns: {timer_id, step_id, max_minutes, elapsed_minutes, exceeded, risk_level, message}
```

### validate_coverage

```python
validate_coverage(
    cov_output: str,        # Full output of `pytest --cov-report=term`
    threshold: float = 70.0,# Coverage threshold (percent)
) -> dict:
    # Returns: {accepted, coverage_percent, threshold, total_line, message}
```

### verify_freeze

```python
verify_freeze(
    frozen_files: list[str],# Hard-frozen file paths (relative to project root)
) -> dict:
    # Returns: {accepted, frozen_count, changed_count, violated_files, message}
```

### snapshot_check

```python
snapshot_check(
    snapshot_path: str,     # Inheritance snapshot file path (relative to project root)
) -> dict:
    # Returns: {accepted, snapshot_path, total_fields, found_fields, missing_fields, message}
    # Required fields (bilingual search):
    #   workflow_state / 当前角色 / 任务阶段 / 已冻结决策 / 待定项 / 下一步
```

## State Persistence

All tool calls are recorded in SQLite (`mcp_server/state.db`):

- `mark_checked_log` - AC completion records
- `pause_log` - Pause/resume records
- `step_log` - Step report records
- `timebox_log` - Timebox start/check records
- `coverage_log` - Coverage validation records
- `freeze_check_log` - Freeze violation check records
- `snapshot_check_log` - Snapshot completeness records

## Known Limitations

| Limitation | Mitigation |
|---|---|
| Tool doesn't force blocking (pause returns, AI may continue) | Client-side / protocol-layer enforcement |
| No forced-call mechanism (AI can skip tools) | Hooks or middleware at client level |
| stdio single-process, concurrent write risk (low) | SQLite WAL mode if needed |

## Provenance

Battle-tested on the [UpgradeES](https://github.com/canyupro/UpgradeES) project through a 4-phase experiment:
1. **Phase 1**: `mark_checked` - evidence-gated AC completion (14 tests)
2. **Phase 2**: `pause_for_user` + `resume_from_pause` - fork pause (11 tests)
3. **Phase 3**: `report_step` - step compression (11 tests)
4. **Phase 4**: `start_timebox` / `check_timebox` / `validate_coverage` / `verify_freeze` / `snapshot_check` - tool expansion (34 tests)

All 4 phases passed on ZCode platform. 70 tests green. No regressions.
