# 06 — Constraint Media & MCP

> The protocol's constraints are stratified by enforcement strength into three layers. This document defines the three layers, migration criteria, MCP tool specifications, the Declaration Card, and the Acceptance Lock.

---

## I. Constraint Media Stratification

### 1.1 Why Stratify

Text-based rules fail as soft constraints against weak models — models can skip reading them, read but not follow them, or follow but softly violate them. By stratifying by enforcement strength and migrating rules with "severe violation consequences + repeated text-layer failure" to the tool layer, we achieve hard constraints decoupled from model strength.

### 1.2 Three-Layer Definitions

| Layer | Medium | Applicable Rules | Enforcement Strength |
|---|---|---|---|
| L0 Text | Rule docs / Triggers / Templates | Process-specific, project-specific, low-risk | Low (soft constraint) |
| L1 Protocol | Declaration Card / Output Contract / Acceptance Checklist | Cross-round behavioral constraints | Medium |
| L2 Tool | MCP tool (cannot produce output without calling) | Checks-and-balances, evidence, pause | Very High (hard constraint) |

### 1.3 Migration Criteria

- If a rule has **severe violation consequences + repeated text-layer failure** → migrate to L2
- If **moderate violation consequences + needs cross-round constraint** → migrate to L1
- Everything else stays at L0

---

## II. L0 — Text Layer

### 2.1 Scope

- Process rules: Round 0–8 deliverables, per-round inputs/outputs
- Project-specific rules: Mandatory confirmation items (§4.4), business object naming
- Low-risk rules: naming conventions, document structure, formatting

### 2.2 L0 Rule Inventory

| Rule | Content |
|---|---|
| 65+ Triggers | Rounds 1b–8 complete set (see 04-Appendix A) |
| 5-Dimension Audit | Dimension 2 (dynamic testing) mandatory, no skipping allowed |
| Launch Gate (8 items) | Hard threshold (see File 02) |
| Three-Tier Freeze | Hard-freeze / Soft-freeze / Draft + decision rules (see 00-Overview §VII) |
| Anti-omission (3 layers) | Skeleton-first / PPM / Integrity scan (see 00-Overview §VIII) |
| Core Rules | pytest output / critical path no-mock / version pinning / 7-layer docs / business-object naming / 70% coverage |
| 21 Clauses | §4.1–§4.21 (see 00-Overview §X index) |

### 2.3 L0 Limitations

Weak models can skip reading, read but not follow, or follow but softly violate. No hard enforcement against weak models. Requires L1/L2 supplementation.

---

## III. L1 — Protocol Layer

### 3.1 Declaration Card (§4.4)

**Rule**: Every round, the AI's first line of output MUST be:

```
[Mode] caveman={ON|OFF} | §8={ON|OFF} | timebox={N}min | risk={LOW|MEDIUM|HIGH}
```

**Retained on ALL platforms.** The Declaration Card and Inheritance Media (File 07) are orthogonal and complementary:

| Mechanism | Scope | Direction | What It Solves |
|---|---|---|---|
| Inheritance Media | Cross-session | One-way state read | "Who am I, where am I" — initial positioning on handoff |
| Declaration Card | Within-session, every round | Bidirectional (model declares → user can reject → model re-answers) | "This round I plan to do X — is that right?" — continuous per-round calibration |

**Why it cannot be omitted**:
- Forks are one-way; the main session cannot perform mid-course bidirectional calibration
- Sub-agents have independent context, don't inherit main session history, still need per-round calibration
- The Declaration Card is the only mechanism providing "per-round interactive confirmation"

**User judgment criteria**:
- See Declaration Card → model is online
- No declaration → user can immediately flag "mode not declared", AI must re-answer
- Declaration doesn't match reality → user can reject the output

### 3.2 Output Contract

Instead of declaring what mode one is in, the output itself must satisfy verifiable structural constraints (first-line format, character limit, mandatory fields) — compliance is inferred from the output.

Applicable scenario: Supplement to the Declaration Card — the Card is model self-declaration (softly violable), while the Output Contract is structural constraint on the output itself (machine-verifiable).

### 3.3 Delivery Consistency Acceptance Lock (§4.2)

Any milestone delivery report MUST pass the V1–V10 acceptance checklist:

| # | Check Item | Pass Criteria |
|---|---|---|
| V1 | First-line Declaration Card | Present with all four fields |
| V2 | Commit hash real | `git log --oneline` can find it |
| V3 | Commit order reasonable | Code commits before report commit |
| V4 | Commit message standard | `feat/fix/docs/chore: <scope> <subject>` |
| V5 | Modified files outside forbidden zones | Check against entry card's forbidden list |
| V6 | Key code locations grep-able | Spot-check 3–5 core function names |
| V7 | pytest output genuine | Reported line count = actual test function count |
| V8 | ruff All checks passed | Failures must be explicitly stated in遗留issues |
| V9 | AC with evidence per item | "Should pass" / "Looks OK" not accepted |
| V10 |遗留issues section present | "None" counts as present |

**Core principle**: The delivery report is the object being verified, not a unilateral declaration. The dispatcher trusts only `git log` + actual command output.

**Common口径drift anti-patterns**:

| Anti-pattern | Correction |
|---|---|
| Commit hash not updated | The last step of writing the report MUST re-run `git rev-parse HEAD` |
| pytest not run before claiming done | Test-class tasks marked ✅ MUST have paste-able command output |
| Confusing implementation-done with user-verified | AC can only be ✅ after tests actually pass green or review passes |
| Screenshots not version-controlled | All evidence must be in-repo |
| SSE event fields "shouldn't have changed" | Must add assertion tests |
| Backward-compat claimed verbally | Must be proven by prior milestone tests all still green |

### 3.4 L1 Limitations

L1 is still "model-softly-violable" — the Declaration Card can be written but not followed, the Output Contract can be bypassed. L1 is stronger than L0 (machine-verifiable), but weaker than L2 (L2: cannot produce without calling).

---

## IV. L2 — Tool Layer (MCP)

### 4.1 Design Principles

1. **Minimal**: Only absorb rules that repeatedly fail at the text layer; don't tool-ify everything
2. **Verifiable**: Every tool parameter must be machine-verifiable (URL reachable, field non-empty, enum valid)
3. **Non-judgmental**: Tools do mechanical verification only, never business judgment. Judgment remains human.
4. **Model-agnostic**: Tools are MCP protocol; any model supporting tool calling can use them

### 4.2 L2 Rule Inventory

| Rule | Corresponding Tool | Enforcement Point | Status |
|---|---|---|---|
| [x] Evidence required | `mark_checked` | Reject without evidence | ✅ Implemented |
| Fork-pause | `pause_for_user` + `resume_from_pause` | Default decision prohibited | ✅ Implemented |
| Report template | `report_step` | Cannot commit without calling | ✅ Implemented |

### 4.3 Tool Specifications

#### mark_checked

```python
@mcp.tool()
def mark_checked(
    item_id: str,           # AC number / task number
    evidence_url: str,      # Evidence path
    evidence_type: str,     # pytest | ruff | git_log | screenshot | review
) -> dict:
    """Mark an AC / task as complete. Evidence required. No evidence or unreachable evidence → reject."""
```

Validation logic:
- `pytest`: Verify test function exists in file
- `git_log`: Verify commit hash is real (`git rev-parse --verify`)
- `ruff`: Verify file exists
- `screenshot`: Verify file is under docs/
- `review`: No machine verification (human review cannot be machine-verified)

Corresponding protocol: Acceptance Lock V7/V9 automation.

#### pause_for_user + resume_from_pause

```python
@mcp.tool()
def pause_for_user(
    forks: list[dict],      # [{"option": "continue fixing", "risk": "MEDIUM"}, ...] at least 2
    context: str,           # Why pause is needed
) -> dict:
    """Force pause at strategy fork point, returning decision authority to user."""

@mcp.tool()
def resume_from_pause(
    pause_id: int,          # pause_id returned by pause_for_user
    choice: str,            # User's chosen option text
) -> dict:
    """Resume execution after user makes a fork choice."""
```

Two-phase semantics (non-blocking):
- pause: Validate forks ≥ 2 + risk is valid → record to SQLite (PAUSED) → return fork options
- resume: Validate pause_id exists and is PAUSED + choice is in forks → update SQLite (RESUMED)

Why not truly block: MCP stdio server is single-threaded; blocking would deadlock. The tool does validation and recording, not forced interception — "AI stops producing" is enforced at the client/protocol layer.

Corresponding protocol: §4.6 Timebox fork-pause tool-ification.

#### report_step

```python
@mcp.tool()
def report_step(
    phase: str,             # read | plan | implement | test | wrap_up
    content: str,           # Summary of actual output this step, ≤500 chars
    artifacts: list[str],   # List of output file paths
) -> dict:
    """Report protocol step completion. Cannot proceed to next step / cannot commit without calling this tool."""
```

Validation logic:
- phase is in enum
- content non-empty + ≤500 chars (prevents decision-cost shifting)
- artifacts non-empty + paths exist

Corresponding protocol: Report template compression, noise reduction.

### 4.4 Integration

MCP server configuration (ZCode example):

```json
{
  "protocol-mcp": {
    "command": "<python_path>",
    "args": ["-B", "-m", "mcp_server.server"],
    "cwd": "<project_root>"
  }
}
```

Takes effect after restarting the AI client. Tool call history is recorded in SQLite (`mcp_server/state.db`).

### 4.5 Known Limitations

| Limitation | Notes |
|---|---|
| Tool doesn't force blocking | After pause_for_user returns paused=True, whether AI actually stops depends on client/protocol layer |
| No forced-call mechanism | AI can skip calling the tool and directly mark complete; requires client-layer enforcement |
| stdio single-process | Multiple conversations share one server; SQLite concurrent writes may conflict (low risk) |
| cwd hardcoded | Config's cwd is hardcoded to project path; changing projects requires config change |

---

## V. Relationship Between Declaration Card and Inheritance Media

### 5.1 Orthogonal Complementarity

The Declaration Card (L1) and Inheritance Media (File 07) solve different problems and cannot substitute for each other:

| Dimension | Declaration Card | Inheritance Media |
|---|---|---|
| Scope | Within-session, every round | Cross-session / cross-agent |
| Direction | Bidirectional (model declares → user can reject → re-answer) | One-way state read |
| What it solves | "This round I plan to do X — is that right?" | "Who am I, where am I" |
| Interactive | Yes | No (fork is one-way / sub-agent has independent context) |

### 5.2 Why Not Migrate Declaration Card to L2

The Declaration Card's essence is "model self-declaration + user bidirectional confirmation" — it requires a human in the loop to reject/re-answer. L2 tools do mechanical verification (is evidence complete / are we at a fork point), not "is this round's direction correct" judgment. Judgment remains human, so the Declaration Card stays at L1.

---

## Version

- v3.0 / 2026-07-03 / 06 Constraint Media & MCP
  - L0/L1/L2 three-layer definitions + migration criteria
  - MCP three-tool specifications (mark_checked / pause_for_user / report_step)
  - Declaration Card retained on all platforms (orthogonal complement to Inheritance Media)
  - Acceptance Lock V1–V10
