# Protocol MCP Server

> MCP (Model Context Protocol) tools implementing L2 hard constraints for the Parallel Development Protocol v3.0.
>
> 规程 MCP 服务器：实现 v3.0 规程 L2 工具层约束的 MCP server。

## What It Does

Three tools that enforce protocol rules that weak models tend to skip at the text layer:

| Tool | Rule Enforced | Mechanism |
|---|---|---|
| `mark_checked` | Evidence-gated AC completion (Acceptance Lock V7/V9) | No evidence or unreachable evidence → reject |
| `pause_for_user` + `resume_from_pause` | Strategy fork pause (§4.6) | Forks ≥ 2, records PAUSED state in SQLite |
| `report_step` | Step report compression + commit gate (§4.12) | content ≤ 500 chars, artifacts must exist |

See protocol File 06 (`zh/06-约束介质与MCP.md` / `en/06-Constraint-Media-and-MCP.md`) for the full L0/L1/L2 design rationale.

## Quick Start

```bash
# Install dependencies
pip install mcp pydantic

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

Or install as editable package to remove `cwd` dependency:

```bash
pip install -e .
```

## Run Tests

```bash
cd mcp/
python -B -m pytest tests/ -v
# 36 tests across 3 files (14 + 11 + 11)
```

## Directory Structure

```
mcp/
├── README.md                          # This file
├── mcp_server/                        # Server source code
│   ├── __init__.py
│   ├── server.py                      # FastMCP server, 4 tool definitions
│   ├── store.py                       # SQLite persistence layer
│   ├── checker.py                     # Evidence validation logic
│   └── models.py                      # Pydantic request/result models
├── tests/                             # 36 unit tests
│   ├── test_mcp_mark_checked.py       # 14 tests
│   ├── test_mcp_pause_for_user.py     # 11 tests
│   └── test_mcp_report_step.py        # 11 tests
└── docs/                              # Design docs + experiment records
    ├── server-design-suggestion.md    # MCP necessity analysis + 3-phase design
    ├── design-mark-checked.md         # Construction-ready design for mark_checked
    ├── design-pause-for-user.md       # Construction-ready design for pause_for_user
    ├── design-report-step.md          # Construction-ready design for report_step
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
    forks: list[dict],      # [{"option": "...", "risk": "MEDIUM"}, ...] - at least 2
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

## State Persistence

All tool calls are recorded in SQLite (`mcp_server/state.db`):

- `mark_checked_log` - AC completion records
- `pause_log` - Pause/resume records
- `step_log` - Step report records

## Known Limitations

| Limitation | Mitigation |
|---|---|
| Tool doesn't force blocking (pause returns, AI may continue) | Client-side / protocol-layer enforcement |
| No forced-call mechanism (AI can skip tools) | Hooks or middleware at client level |
| stdio single-process, concurrent write risk (low) | SQLite WAL mode if needed |
| `cwd` config dependency | `pip install -e .` to make globally importable |

## Provenance

Battle-tested on the [UpgradeES](https://github.com/canyupro/UpgradeES) project through a 3-phase experiment:
1. **Phase 1**: `mark_checked` - evidence-gated AC completion (14 tests)
2. **Phase 2**: `pause_for_user` + `resume_from_pause` - fork pause (11 tests)
3. **Phase 3**: `report_step` - step compression (11 tests)

All 3 phases passed on ZCode platform. 36 tests green. No regressions.
