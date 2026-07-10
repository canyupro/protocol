# 02 — Serial Conversation: Round 3 to Round 5 and the Launch Gate

> Specification Formulation → Database Design + Memory Architecture → Framework Construction + SSE Dual-Track + Crisis Short-Circuit → Freeze Audit → Multi-Agent Launch Gate.
> The complete templates for all 6 Core Documents are inlined in this file and can be copied directly.
> Every round must begin with a Declaration Card (§4.4) and end with an Inheritance Snapshot update (§4.12).

---

## Round 3: Specification Formulation

This is the most critical round in this procedure — it determines "whether the AI can consistently execute tasks."

**Inputs**: Directory structure + chain todo + Acceptance Criteria + tech stack + Contract Freeze document.

**Outputs** (all 6 Core Documents are here):

- `docs/03-agent/AGENTS.md` (Core Document 1)
- `docs/03-agent/Agent 职责划分.md` (Core Document 2)
- `docs/03-agent/Prompt 设计规范.md` (Core Document 3)
- `docs/03-agent/AI Agent Prompt 规范.md` (Core Document 4, §4.17, mandatory when Agent chains are present)
- `docs/05-ai-coding/开发规则.md` (5 non-removable rules + executable check items for each)
- `docs/05-ai-coding/代码规范.md` (naming / comments / error handling / logging / testing)
- `docs/05-ai-coding/CLAUDE.md` + `docs/05-ai-coding/CODEX.md`
- `docs/03-agent/AI Agent 安全边界规范.md` (§4.14, mandatory when Agent chains are present)
- `docs/05-ai-coding/前端规范.md` (§4.5, mandatory when a frontend is present)

**Agenda Checklist**:

- AGENTS.md: team structure / responsibilities / collaboration workflow / evaluation criteria
- Agent 职责划分: Coordinator / Coding Agent / Audit Agent Do / Don't Do
- Prompt 设计规范: task template / context format / output format / prohibitions
- **AI Agent Prompt 规范** (§4.17): versioning / structured output / security constraints / fallback / anti-prohibition checklist
- **AI Agent 安全边界规范** (§4.14): sensitive-field tiering / zero exposure to student side / RAG knowledge boundary / severity-based rating escalation
- **前端规范** (§4.5): Definition of Done / perspective convergence / single-source View (See File 08)
- 5 development rules (non-removable) + executable check items for each
- Code standards discussion (naming / comments / error handling / logging / testing)
- **Declaration Card protocol** (§4.4): bidirectional calibration as the first line of every round
- Trigger checks

---

### AGENTS.md Template (copy directly)

```markdown
# AGENTS.md

## 1. Team Structure
- AI Coordinator: dispatches tasks / acceptance / integration, does NOT write business code
- Coding Agent A (Chain 1): [chain name, e.g. customer]
- Coding Agent B (Chain 2): [chain name, e.g. student]
- Coding Agent C (Chain 3): [chain name, e.g. ai_chat] [Agent]
- Coding Agent D (Chain 4): [chain name, e.g. mental_health] [Agent]

## 2. Responsibility Division
- Coordinator: does NOT write business code; modifies shared files
- Coding Agent: writes code + self-tests + writes chain documentation
- Audit: Coordinator doubles as Auditor

## 3. Collaboration Workflow
- Phases 1–7: Coordinator works independently
- Phase 8: Coordinator erects the skeleton
- Phase 9: Agents work in parallel (each on their own branch)
- Phase 10: Coordinator merges in isolation zone
- Phase 11: Coordinator releases

## 4. Evaluation Criteria (5 Dimensions)
- Code standards (ruff)
- Dynamic testing (pytest, actually run)
- Contract consistency (API vs. design documents)
- Documentation completeness (all 7 layers present)
- Real-world postmortem (pitfall checklist)

## 5. Failure Handling
- Single Agent failure → isolate and debug, do NOT damage the skeleton
- Integration conflict → resolve in isolation zone, do NOT touch the main branch
- Overall failure → rollback + re-integrate
```

---

### Agent 职责划分.md Template (copy directly)

```markdown
# Agent 职责划分

## Coordinator (AI 协调员)
### Do
- Dispatch tasks (allocate chain tasks)
- Acceptance (5-dimension audit)
- Integration (merge in isolation zone)
- Modify shared files (core/ router.py)
- Write the shared layer of the 7-layer docs
- Write meeting minutes

### Don't Do
- Write business code
- Modify files outside Chain Agent Whitelist
- Release without authorization (must be approved by canyu)

## Coding Agent (one per chain)
### Do
- Write business code (models / schemas / services / api)
- Write tests
- Write intra-chain documentation (_chains/chainN-xxx/)
- Self-test + run pytest
- Must include test output in commit message

### Don't Do
- Modify shared files like core/ router.py
- Modify files belonging to other chains
- Directly modify top-level directory docs (must go through _chains/)
- Mock critical paths (LangChain / SSE / cross-chain HTTP)
- Commit without test output in commit message

## Audit Agent (Coordinator doubles as)
### Do
- 5-dimension audit
- Red/Yellow/Green evaluation
- Real-world postmortem

## Test Agent (Coordinator doubles as)
### Do
- E2E testing
- Coverage checks
- Performance testing (optional)
```

---

### Prompt 设计规范.md Template (copy directly)

```markdown
# Prompt 设计规范

## Task Template
[Background]
[Objective]
[Input / Output]
[Constraints]
[Definition of Done]

## Context Format
- Referenced documents: path is mandatory
- Referenced code: file:line is mandatory
- "Guessing" is not allowed

## Output Format
- Change list (file + line count)
- Test results (pytest output)
- Known issues
- Suggested improvements

## Prohibited
- Do NOT "incidentally" modify unrelated code
- Do NOT use "I think" — cite the document
- Do NOT use "should be fine" — provide evidence
```

---

### AI Agent Prompt 规范.md Template (§4.17, mandatory when Agent chains are present)

```markdown
# AI Agent Prompt 规范

## Versioning
- All prompts must be written in ai/chains/* files, tracked by git
- PROMPT_VERSION is mandatory (e.g. k12-supervisor-v1)
- Scattering prompts across the service layer is prohibited

## Structured Output
- PydanticOutputParser enforces structured output
- Fallback on failure + logging
- structured_response is the ultimate source of truth (rating / alert_reason do NOT travel via token)

## Security Constraints
- Do NOT label (see §4.5 empathy red line)
- Do NOT expose internal fields such as confidence / direction to students
- alert_reason is mandatory and must be explainable
- Response ≤ 250 characters

## Fallback
- LLM failure → fallback text (gentle prompt, do NOT throw 500)
- RAG retrieval failure → "No relevant content found", do NOT block the main flow
- All tools must have fallback

## Anti-Prohibition Checklist
- Do NOT concatenate unrelated history
- Do NOT expose structured fields to students
- Do NOT let Supervisor downgrade a rating triggered by keyword hit

## Few-shot
- Key scenarios must include Few-shot examples
```

---

### AI Agent 安全边界规范.md Template (§4.14, mandatory when Agent chains are present)

```markdown
# AI Agent 安全边界规范

## Sensitive Field Tiered Filtering
| Field | Teacher Side | Student Side |
|---|---|---|
| Psychological rating (level) | ✅ Visible | ❌ Zero exposure |
| Alert reason (alert_reason) | ✅ Visible | ❌ Zero exposure |
| Keyword hit information | ✅ Visible | ❌ Zero exposure |

## Student-Side Zero Exposure
- Student-side SSE tokens must NOT contain rating / alert_reason / keyword hit information
- Student-side UI displays only supportive text
- Exposing rating information to the student side in any form = red line

## RAG Knowledge Boundary
- RAG indexes only institutional knowledge (Policy), NOT student data
- Student history resides in a separate collection with strong user_id isolation
- Student A must NOT be able to recall Student B's data

## Psychological Rating Escalation (Severity-Based)
- Keyword-based safeguard takes precedence over LLM judgment
- red forces escalate_to_teacher=True
- LLM must NOT downgrade a red triggered by keyword hit
- merge_with_supervisor_level always takes the more severe rating

## Fact Profile Retraction
- agent_known_facts includes a retracted_at field
- Retraction does NOT delete; it marks the record as invalid
- After retraction, the fact is no longer used as a decision basis
```

---

### 开发规则.md (5 non-removable rules, each with executable check items)

```markdown
# 开发规则

## Rule 1: Complete only one task at a time
Single-commit granularity; do NOT cross tasks.
Check: "Task ID" is mandatory in the commit message.

## Rule 2: Do NOT modify unrelated code
Only modify files specified by the task.
Check: all files appearing in git diff must be within the Whitelist.

## Rule 3: New interfaces must include interface documentation
Documentation goes in _chains/chainN-xxx/接口设计.md.
Check: the number of interfaces documented in 接口设计.md must equal the actual route count.

## Rule 4: Database changes must provide a migration
Alembic up + down must be written.
Check: a corresponding migration file exists in alembic/versions/.

## Rule 5: Provide a test plan
Layered unit / integration / E2E.
Check: commit message includes pytest output.
```

---

### 代码规范.md — Basic Requirements

```markdown
# 代码规范

## Naming
- Variables / functions: snake_case
- Classes: PascalCase
- Table names: plural (customers / students)
- Model names: singular (Customer / Student)
- Files: snake_case

## Comments
- Public interfaces must be commented
- Complex logic must be commented
- Do NOT comment "the obvious"

## Error Handling
- Unified exception handling at the API layer
- Service layer throws business exceptions
- Do NOT log sensitive information

## Testing (the Dynamic Testing Specification section is mandatory)
- Coverage no less than 70%
- Mock is prohibited on critical paths (LangChain / SSE / cross-chain HTTP)
- Commit message must include pytest output
```

---

### Triggers

| No. | Condition | Judgment |
|------|------|------|
| T6.1 | Any AI collaboration rule lacks a corresponding executable check item | Flag Red |
| T6.2 | AGENTS.md is missing any of the 4 essential elements (team structure / responsibilities / workflow / evaluation) | Flag Red |
| T6.3 | 代码规范.md is missing the "Dynamic Testing Specification" subsection | Flag Red |
| T6.4 | Any of the 5 standard rules in 开发规则.md has been altered or removed | Flag Red |
| T6.5 | Agent 职责划分.md does not specify Do / Don't Do | Flag Red |
| T6.6 | Prompt 设计规范.md is missing the "Task Template" | Flag Red |
| T6.7 | Agent chains are present but AI Agent Prompt 规范.md is missing | Flag Red |
| T6.8 | Agent chains are present but AI Agent 安全边界规范.md is missing | Flag Red |
| T6.9 | A frontend is present but 前端规范.md is missing | Flag Red |

**Freeze Determination**:

- 6 Core Documents: Hard-Freeze (basis for multi-Agent collaboration)
- 5 development rules: Hard-Freeze (non-removable)
- Code standards: Soft-Freeze (supplementable but not reducible)

**Decision Point**: canyu decides "are the specifications correct?"

**Rollback Procedure**: If specifications cannot be executed, do NOT redesign; record as an exception and revisit in Round 8 postmortem.

**Red/Yellow/Green**:

- Green: all 6 Core Documents complete + coding + AI rules complete + every rule verifiable + Agent security boundary + frontend specification
- Yellow: rules exist but verification mechanisms are incomplete
- Red: rules are verbalized and unverifiable

---

## Round 4a: Database Design

**Inputs**: Design specifications + chain todo + Acceptance Criteria.

**Outputs**: `docs/04-technical/数据库设计.md` + `建表语句.sql` + `alembic/versions/`.

**§4.18 Memory Architecture Design** (mandatory when Agent chains are present):

If the project includes AI Agent chains, the database design must include Memory Architecture design:

| Tier | Storage Medium | Schema Key Points |
|---|---|---|
| L1 Short-term | DB (conversation_messages) | role / content / created_at, most recent N messages |
| L2 Mid-term | DB (conversation.summary field) | Session-level summary |
| L3 Structured Fact Profile | DB (JSONB agent_known_facts) | weight / trend / retracted_at / score deduction calculation |
| L4 Cross-session | Vector store (independent collection) | user_id strong isolation / top_k / degradation-friendly |

Design points:
- **user_id isolation**: Student A must NOT be able to recall Student B's data (vector store expr filtering + result secondary verification)
- **Only role=user messages are ingested**: assistant replies are NOT stored in the vector store (to avoid the AI's own words being recalled as "student history")
- **retracted_at retraction**: retraction does NOT delete; marks the record as invalid
- **Overly long message truncation**: leave headroom (e.g. schema max 1000, truncate at 1500)

**Agenda Checklist**:

- List all tables (one set per chain + shared tables)
- Field naming calibration (snake_case / plural table names / singular model names)
- Soft-delete field (is_deleted) + timestamps (created_at / updated_at)
- Foreign keys + indexes
- Alembic migration scripts (up + down)
- **Memory Architecture design** (§4.18: 4-tier memory schema / vector store collection planning / user_id isolation)

**Key Steps**:

1. List all tables: one set of tables per chain, plus shared tables (users / roles / permissions)
2. Field naming: snake_case, plural table names, singular model names
3. Every table must include: is_deleted BOOLEAN DEFAULT FALSE, created_at TIMESTAMP, updated_at TIMESTAMP
4. Foreign keys are mandatory; indexes cover where / order by / join fields
5. Alembic migration: one migration per change, write up + down, run against a test DB
6. **Memory Architecture** (when Agent chains are present): design 4-tier memory table structure + vector store collection + user_id isolation

**Triggers**:

| No. | Condition | Judgment |
|------|------|------|
| T7.1 | Table / field names are inconsistent with code | Flag Red |
| T7.2 | is_deleted field missing | Flag Red |
| T7.3 | created_at / updated_at missing | Flag Red |
| T7.4 | No Alembic migration | Flag Red |
| T7.5 | Missing foreign keys / missing indexes | Flag Yellow |
| T7.6 | Agent chains present but no Memory Architecture design | Flag Red |
| T7.7 | Memory Architecture has no user_id isolation scheme | Flag Red |

**Freeze Determination**:

- Table structure: Soft-Freeze (fields may be fine-tuned during coding, without rollback)
- Naming conventions (tables / fields): Hard-Freeze
- Memory Architecture schema: Hard-Freeze

**Decision Point**: None (derived from specifications).

**Rollback Procedure**: If table structure does not align with specifications, realign.

**Red/Yellow/Green**:

- Green: naming consistent + soft-delete / timestamps complete + Alembic complete + Memory Architecture design complete
- Yellow: naming consistent but fields incomplete
- Red: naming inconsistent / no Alembic / no Memory Architecture

---

## Round 4b: Overall Framework Construction

**Inputs**: Database design + design specifications + Memory Architecture design.

**Outputs**:

- `backend/app/` shared modules (config / main / core / router left blank)
- Business route stubs (customer.py / student.py / ai_chat.py / mental.py)
- **Agent framework** (when Agent chains are present: ai/agents/ + ai/chains/ + ai/guards/)
- **SSE protocol skeleton** (§4.20, when Agent chains are present)
- **Crisis Short-Circuit module** (§4.16, when Agent chains are present)
- `scripts/env_check.py` (environment rehearsal)
- `tests/test_health.py` (smoke test)
- `docs/04-technical/模块划分.md`

**§4.20 True-Streaming SSE Dual-Track Design** (mandatory when Agent chains are present):

| Key Point | Detail |
|---|---|
| Main track | `astream_events("v2")` listening on `on_chat_model_stream` |
| Secondary track | Pseudo-streaming `pseudo_stream_chunks` fallback, split every 12 characters |
| Trigger condition | `streamed_visible_chars == 0` (mutually exclusive, no duplicate delivery) |
| Visibility filtering | `is_visible_token` filters JSON control characters / field headers / whitespace; structured schema must NOT leak to the user side |
| Source of truth | structured_response is the ultimate source of truth (rating / alert_reason do NOT travel via token) |
| TTFT | ≤ 2s; placeholder tokens may be added for degradation |

SSE event protocol (defined during Round 2b Contract Freeze; implement the skeleton here):
- `conversation_created`: session created
- `token`: streaming token
- `meta`: meta information (e.g. mental_health_update)
- `done`: completion (includes plan_update_hint / history_rag_hits / tools_used)
- `error`: error (includes code + fallback token)

**§4.16 Crisis Response Short-Circuit** (mandatory when Agent chains are present):

AI Agent chains must perform crisis keyword short-circuiting before any LLM call:
- Keyword matching (e.g. HIGH_RISK_KEYWORDS) → return a safety template (e.g. 12355 psychological assistance hotline), **do NOT call the LLM**
- Crisis Short-Circuit executes before all tools / LLM
- Crisis Short-Circuit tests are strict-class (100% pass rate required before release; see File 03 §4.19)

**Agenda Checklist**:

- config.py — extra="ignore" must be added
- main.py + core/ (database / security / middleware / response / exceptions)
- router.py (shared only; business routes left blank)
- Business route stubs (one empty file per chain)
- **Agent framework construction** (when Agent chains are present: agents/supervisor + context + response_format + guards/keyword_alert + tools/)
- **SSE protocol skeleton + True-Streaming Dual-Track** (§4.20)
- **Crisis Short-Circuit module** (§4.16)
- Environment rehearsal script (all green, including Docker / vector store)
- Smoke test (health check passing)
- Trigger checks

**config.py Critical Constraint** (pydantic v2 real-world lessons):

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    # ... other fields

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"  # Must be added — pydantic defaults to forbid otherwise, and all pytest will fail to start
    )

settings = Settings()
```

Must use `model_config = SettingsConfigDict(...)` rather than the legacy `class Config`.

**Environment Rehearsal Checklist**:

- config.py includes model_config + extra="ignore"
- requirements.txt locks versions; "latest" is prohibited
- Dockerfile locks base image version
- Database is reachable, vector store is reachable (if present), LLM Provider is reachable (if present)
- .env.example is complete
- scripts/env_check.py runs all green
- pytest tests/test_health.py all pass

**router.py Blank-Slate Rule**:

```python
from fastapi import APIRouter
# Business routes left blank; Chain Agents add them on their branches during the parallel phase
router = APIRouter()
```

router.py is a shared file; only the Coordinator may modify it; Chain Agents are prohibited from modifying it.

**Triggers**:

| No. | Condition | Judgment |
|------|------|------|
| T8.1 | Environment rehearsal failed | Block |
| T8.2 | Smoke test failed | Block |
| T8.3 | Config missing extra="ignore" | Block |
| T8.4 | router.py contains business routes | Flag Red |
| T8.5 | _chains/ not yet created | Block |
| T8.6 | Agent chains present but Agent framework not constructed | Flag Red |
| T8.7 | Agent chains present but SSE protocol skeleton not implemented | Flag Red |
| T8.8 | Agent chains present but Crisis Short-Circuit not implemented | Flag Red (Block release) |
| T8.9 | Agent chains present but vector store unreachable with no degradation | Flag Yellow |

**Freeze Determination**:

- Shared module code (config / core / main): Hard-Freeze (Chain Agents prohibited from modifying)
- router.py blank-slate rule: Hard-Freeze
- SSE event protocol: Hard-Freeze (already set during Round 2b Contract Freeze)
- Agent framework interfaces: Hard-Freeze

**Decision Point**: canyu decides "is the skeleton correct?"

**Rollback Procedure**: If the skeleton cannot run, troubleshoot config / dependencies / versions; do NOT rewrite the architecture.

**Red/Yellow/Green**:

- Green: environment rehearsal passes + smoke test passes + route framework blank + Agent framework complete + SSE skeleton complete + Crisis Short-Circuit complete
- Yellow: environment rehearsal passes but with warnings
- Red: environment rehearsal failed / Agent framework missing / Crisis Short-Circuit missing

---

## Round 5: Freeze Audit

**Inputs**: All Hard-Freeze / Soft-Freeze / Draft items from prior rounds + PPM + Contract Freeze document.

**Outputs**: Freeze audit report + Integrity Scan report + confirmation of all Soft-Freeze → Hard-Freeze upgrades.

**Audit Content**:

A. **Cross-Round Dependency Consistency Check**: Compile all Hard-Freeze items into a single freeze checklist and verify cross-round dependency consistency.

B. **Soft-Freeze → Hard-Freeze Upgrade**: Key Soft-Freeze items are decided here whether to upgrade to Hard-Freeze. Default strategy: when ambiguous, lean soft; but upgrade if the Coordinator assesses high risk.

C. **PPM Integrity Scan**:
- Directories marked as "Required This Round" in the 7-layer docs must not contain empty files
- Any of the 6 Core Documents missing → Block
- Every chain's interface design must include path / method / input params / output params / error codes
- Every chain's todo must annotate test points for each organ
- All in-progress items in PPM must be transitioned to done
- Any document containing a 待补充 (to-be-supplemented) marker that involves mandatory Round content → Block

D. **Agent Contract Freeze** (when Agent chains are present):
- SSE event protocol frozen (event names / fields / order)
- Prompt version frozen (PROMPT_VERSION finalized)
- Memory schema frozen (4-tier memory table structure / vector store collection)
- Security boundary frozen (sensitive field tiering / severity-based rating escalation rules)

E. **Frontend Definition of Done Freeze** (when a frontend is present):
- Role matrix frozen (which roles / page entry points per role)
- Single-source View directory structure frozen
- Perspective convergence plan frozen (which features belong to which role / convergence time points)

**Decision Point**: canyu confirms "the gate can be opened."

---

## Multi-Agent Launch Gate (8 Hard Conditions — all must be met to pass)

```
Condition 1: Architecture Frozen
  Directory structure finalized + tech stack versions locked + shared modules written

Condition 2: Contract Frozen
  Every chain's 接口设计.md is written (path / method / input params / output params / error codes)
  SSE event protocol frozen (when Agent chains are present)
  Enum values / frontend-backend field mapping frozen

Condition 3: Environment Rehearsal Passed
  scripts/env_check.py all green
  Docker / vector store reachable (when Agent chains are present)

Condition 4: Smoke Test Passed
  pytest tests/test_health.py all pass

Condition 5: 6 Core Documents Complete
  AGENTS.md / Agent 职责划分 / Prompt 设计规范
  / AI Agent Prompt 规范 (when Agent is present) / 任务拆分规范 / Acceptance Criteria

Condition 6: Every Chain's todo.md is Decomposed
  Includes organ + test point annotations + cross-chain dependency annotations
  Agent chain todo includes Agent-specific organ annotations

Condition 7: Whitelist Is Explicit
  Which files each Agent can / cannot modify

Condition 8: Contract Is Frozen
  Interface schema / enums / SSE events / frontend-backend field mapping
  Contract document precedes code, not retrofitted after a crash
```

All passed → the gate opens. Any not passed → Block; return to the corresponding round to fill the gaps.

---

> Round 3–5 complete. After the Launch Gate is passed, proceed to 03 — Parallel Development and Wrap-Up — Round 6 to Round 8.
> Every round must end with an Inheritance Snapshot update (§4.12).
