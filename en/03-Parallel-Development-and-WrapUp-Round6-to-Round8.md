# 03 — Parallel Development and Wrap-Up: Round 6 to Round 8

> After the launch gate passes: chain parallel coding (including Agent Degradation / frontend Perspective Convergence) → multi-chain integration (including Evaluation Grading) → testing and release (including Scenario Regression / Acceptance Lock).
> 5-Dimension Audit complete SOP, dynamic test specifications, and Agent prompt templates are all inlined.
> Each round must output a Declaration Card (§4.4) at the first sentence, and each round must update the Inheritance Snapshot (§4.12) upon completion.

---

## Context Transfer Package (after launch gate passes, Coordinator distributes to each Chain Agent)

Materials provided to each Chain Agent:

| Material | Path | Reason It Must Be Read |
|------|------|---------|
| AGENTS.md | docs/03-agent/AGENTS.md | Team structure + collaboration process |
| Agent Responsibility Division.md | docs/03-agent/Agent Responsibility Division.md | Do / Don't |
| Development Rules.md | docs/05-ai-coding/Development Rules.md | 5 rules + check items |
| Code Standards.md | docs/05-ai-coding/Code Standards.md | Naming / comments / testing |
| Acceptance Criteria.md | docs/03-agent/Acceptance Criteria.md | Verification method for each interface |
| Module Division.md | docs/04-technical/Module Division.md | Whitelist boundaries |
| ChainN-todo.md | docs/03-agent/ | Exclusive task list |
| Interface Design Draft | _chains/chainN-xxx/Interface Design.md | Which interfaces to implement |
| Architecture Freeze Snapshot | Extracted from decision records | Tech stack / directory structure immutable |
| Contract Snapshot | Extracted from interface design | Input params / output params / error codes unchanged |

**§4.12 Inheritance Snapshot Alternative**: On platforms that support session forking (such as ZCode), the Inheritance Snapshot can replace part of the Context Transfer Package — the executor reads the snapshot to locate roles and tasks without needing the full transfer package. See File 07.

---

## Chain Agent Whitelist Template

```markdown
## Chain N Whitelist

### Modifiable
- app/models/[chain_name].py
- app/schemas/[chain_name].py
- app/services/[chain_name]_svc.py
- app/api/v1/[chain_name].py
- app/ai/chains/[chain_name]_chain.py (when Agent chain is included)
- app/ai/agents/tools/[chain_name]_tool.py (when Agent chain is included)
- tests/test_chainN_[chain_name].py
- docs/04-technical/_chains/chainN-[chain_name]/Interface Design.md
- docs/04-technical/_chains/chainN-[chain_name]/Database Changes.sql

### Non-Modifiable
- app/core/config.py / database.py / security.py
- app/core/middleware.py / response.py / exceptions.py
- app/api/v1/router.py
- app/ai/agents/supervisor.py (when Agent chain is included, shared Agent orchestration)
- app/ai/agents/guards/ (when Agent chain is included, security guards)
- app/ai/llm_factory.py / embeddings.py / vectorstore.py (shared AI modules)
- app/models/[other_chain_name].py / app/schemas/[other_chain_name].py
- app/services/[other_chain_name]_svc.py / app/api/v1/[other_chain_name].py
- tests/test_chain[other_chain]_*.py
- docs/04-technical/Interface Design.md (main directory, only Coordinator modifies)
```

---

## Round 6: Chain Parallel Development

**Input**: Skeleton + launch gate passed + Context Transfer Package (or Inheritance Snapshot).

**Outputs**: Each chain's code + single-chain tests + _chains/ interface design draft.

**§4.15 Agent Degradation Strategy** (when Agent chain is included):

Every Agent chain must implement a degradation path:

| Degradation Point | Rule |
|---|---|
| LLM failure | SSE error event + fallback token (gentle prompt) + done still sent |
| Tool failure | All tools have fallback text, no exception thrown |
| RAG retrieval failure | Return "No relevant content found", do not block main flow |
| Vector store unavailable | Main flow still proceeds (degradation-friendly) |

Degradation tests are checked during the Round 7 5-Dimension Audit.

**§4.6 Timebox + Red-Light Tiering**:

| Rule | Content |
|---|---|
| Todo granularity | Corresponds to verifiable output, not shell commands; recommended 5-10 minutes |
| Normal Red Light | Pause after 5 rounds (small tests / scripts / path issues do not interrupt user frequently) |
| High-Risk Red Light | Pause after 2 rounds (architecture / permissions / mental health / RBAC / policy source) |
| Single-step timeout | Must report if exceeding 10min; for long commands exceeding 3min, notify before starting |
| Auto-advance | Within user-confirmed strategy, auto-advance by default; only pause at strategy forks / timeouts / mandatory confirmation items |

**§4.21 Dependency Addition Process**:

1. Chain Agent discovers need for a new package → reports to Coordinator (issue / decision record)
2. Coordinator evaluates: version compatibility + security + necessity
3. Approved → write pyproject.toml + `uv sync`
4. Rejected → find alternative approach
5. **Forbidden**: Chain Agent self-executing `pip install`

**Frontend Parallel** (when frontend is included):

Frontend development initiates Perspective Convergence preparation in late Round 6:
- Each role's single-source-of-truth View is written in `_shared/views/`
- Route shell `page.tsx` is created
- `/dev` aggregation entry is set up (testing period)
- Perspective Convergence is formally executed in Round 7 (see File 08 §II)

**Process**: Coordinator distributes Context Transfer Package (or executor reads Inheritance Snapshot), N Agents write code simultaneously on their own branches, user confirms chain by chain.

**Coding Agent Prompt Template** (Coordinator sends to each Chain Agent):

```
You are Coding Agent Chain N. Implement Chain N based on the following materials:

[Required reading: AGENTS.md / Agent Responsibility Division / Development Rules / Code Standards / Acceptance Criteria / Module Division / ChainN-todo / Interface Design Draft]

Output:
- app/models/N.py
- app/schemas/N.py
- app/services/N_svc.py
- app/api/v1/N.py
- tests/test_chainN_N.py (unit tests + integration)
- docs/04-technical/_chains/chainN-xxx/Interface Design.md (draft)

Hard Constraints (must follow):
1. Single commit granularity, each commit completes 1 task
2. Forbidden to modify unrelated code
3. Forbidden to modify core/ router.py (outside Whitelist)
4. Forbidden to modify files of other chains
5. Every interface must include interface documentation (draft placed in _chains/)
6. Database changes must provide migration
7. Output test plan (unit + integration + E2E)
8. Forbidden to mock LangChain / SSE / cross-chain HTTP
9. Must run pytest (real run, with output)
10. Coverage no less than 70%
11. Forbidden to self-execute pip install (report to Coordinator)
12. Agent chain must include degradation path (LLM failure fallback / RAG failure does not block)

Forbidden (must explicitly follow):
- Forbidden to mock LangChain / SSE / cross-chain HTTP
- Forbidden to modify core/ router.py / ai/agents/supervisor.py / ai/agents/guards/
- Forbidden to claim pass (must include test output)

Output Format:
- Change list (file + line count)
- Test results (last 5 lines of pytest output)
- Known issues
```

---

### Dynamic Test Specification

**Coverage threshold**: No less than 70%, no relaxation allowed, no missing coverage reports.

**Mock prohibition principle** (mock disabled on Critical Path):

Forbidden to mock:
- LangChain LLM calls
- SSE streaming
- Cross-chain HTTP calls
- Core business logic

Allowed to mock:
- Database (in-memory SQLite or dedicated test_db schema)
- Third-party HTTP (e.g. OpenAI, unit tests only; integration must run real)
- Time (simulate specific time points)
- Random numbers

**Agent Chain Test Supplement**:
- Crisis short-circuit test: keyword hit → security template returned, no LLM invoked
- Degradation test: LLM failure → error event + fallback
- Security boundary test: student-side zero exposure / user_id isolation / strictest rating
- Degradation tests may use mock (to avoid real LLM taking 9 minutes), but crisis short-circuit and real LLM chain integrity are ensured by a small number of "real runs"

**Test Layers**:

- Unit test: 1 function, 1 file, no dependencies
- Integration test: multiple modules, 1 API endpoint
- E2E: complete business flow, across multiple endpoints

**Commit message must include pytest output** (last 5 lines):

```
[Chain 1] Implement customer registration API

- model: Customer / schema: CustomerCreate / service: create_customer
- api: POST /api/v1/customers

## pytest output
tests/test_chain1_customer.py::test_create_customer_normal PASSED
tests/test_chain1_customer.py::test_post_customers_201 PASSED
3 passed in 0.42s
```

---

### Triggers

| Number | Condition | Judgment |
|------|------|------|
| T9.1 | Team member says "tests pass" but does not attach pytest output | Flag Red |
| T9.2 | Team member mocked LangChain / SSE / cross-chain HTTP | Flag Red |
| T9.3 | Coverage below 70% | Flag Red |
| T9.4 | Interface design misses a new interface | Flag Red |
| T9.5 | Cross-chain call not marked in interface design | Flag Red |
| T9.6 | Chain Agent modified core/ router.py or other shared files | Flag Red |
| T9.7 | Commit message does not include test output | Flag Red |
| T9.8 | Chain Agent self-executed pip install | Flag Red |
| T9.9 | Agent chain lacks degradation path (LLM failure returns 500) | Flag Red |
| T9.10 | Agent chain lacks crisis short-circuit (keyword goes directly to LLM) | Flag Red |

**Decision Point**: canyu confirms chain by chain: "Is this chain correct?"

**Rollback Procedure**: Single chain failure — isolate that chain for debugging, do not break the skeleton; pytest failure — fix code, do not change standards.

**Red/Yellow/Green**:

- Green: pytest all pass + Critical Path real + coverage no less than 70% + interface design complete + commit must include test output + Agent degradation complete
- Yellow: pytest passes but Critical Path uses mock
- Red: pytest failed / coverage insufficient / interface design missing / no degradation / no crisis short-circuit

---

## Round 7: Multi-Chain Integration

**Input**: N chains each completed + each chain's interface design.

**Outputs**: Merged code + Integration Rehearsal + 5-Dimension Audit (1 per chain) + frontend Perspective Convergence acceptance + meeting minutes.

**Key Steps**:

1. Conflict prevention (shared file splitting plan already decided, naming standards already decided, cross-chain call standards already decided)
2. Isolation zone merge: `git checkout -b t2 origin/main`, merge chain by chain
3. Integration Rehearsal: cross-chain HTTP real calls (no mock), run 1 complete end-to-end business flow
4. Conflict handling: no forced overwrite allowed, no leaving TODOs to fix later
5. **Frontend Perspective Convergence** (when frontend is included): Execute per File 08 §II — role splitting / `/dev` takedown / at least 1 real interaction loop per role
6. **E2E Layering** (§4.7): fast audit (gate) + full-ai (demo rehearsal), slow chains not mixed into gate

---

### §4.19 Evaluation Grading

Tests are divided into Strict-Class and Flexible-Class:

| Class | Content | Passing Standard |
|---|---|---|
| Strict-Class | Crisis response / boundary violation detection / security boundaries (sensitive field isolation / RAG knowledge boundary / user_id isolation) | 100% pass before release |
| Flexible-Class | Functional / performance / Coverage | Per threshold (Coverage ≥70%) |

---

### 5-Dimension Audit (1 per chain)

| Dimension | Meaning | Must Run | Tool |
|------|------|------|------|
| Code Standards | Static check / formatting | Must run | ruff / mypy / black |
| Dynamic Testing | Run code to verify behavior | Must run (no skipping allowed) | pytest (unit + integration + E2E) |
| Contract Consistency | API implementation vs interface design vs contract freeze document | Must run | Manual comparison / OpenAPI tools |
| Documentation Completeness | 7-layer documentation + README | Must run | Manual |
| Practical Retrospective | Pitfalls encountered this time | Must run | Manual |

**Agent Chain Additional Audit Items**:
- Degradation test: LLM failure → error + fallback (§4.15)
- Crisis short-circuit test: keyword → security template, no LLM invoked (§4.16)
- Security boundary test: student-side zero exposure / user_id isolation / strictest rating (§4.14)
- Evaluation Grading annotation: Strict-Class 100% / Flexible-Class per threshold (§4.19)

No "claiming pass" allowed — every item must have tool output or screenshot.

**Audit Report Template** (placed in _chains/chainN-xxx/5-Dimension-Audit-ChainN.md):

```markdown
# 5-Dimension Audit - Chain N

## Dimension 1: Code Standards
- ruff: 0 errors
- Output: complete ruff check output

## Dimension 2: Dynamic Testing
- pytest: N passed
- Coverage: XX%
- Output: complete pytest output
- Must run

## Dimension 3: Contract Consistency
- API implementation vs interface design vs contract freeze: consistent
- Cross-chain calls: marked

## Dimension 4: Documentation Completeness
- 7-layer documentation: complete
- Missing: none

## Dimension 5: Practical Retrospective
- Pitfall: [specific issue]
- Fix: [specific solution]

## Agent-Specific (when Agent chain is included)
- Degradation test: LLM failure → error + fallback ✅/❌
- Crisis short-circuit: keyword → security template ✅/❌
- Security boundary: zero exposure / isolation / strictest ✅/❌

## Evaluation Grading
- Strict-Class: X/X 100% pass ✅/❌
- Flexible-Class: Coverage XX% ✅/❌

## Overall
Green / Yellow / Red
```

---

### Triggers

| Number | Condition | Judgment |
|------|------|------|
| T10.1 | Shared file conflict occurring "by chain number" | Flag Red |
| T10.2 | Cross-chain call depends on mock | Flag Red |
| T10.3 | 5-Dimension Audit skips Dimension 2 (Dynamic Testing) | Flag Red |
| T10.4 | Chain Agent directly writes main directory files | Flag Red |
| T10.5 | Integration Rehearsal fails | Flag Red |
| T10.6 | Cross-chain call not marked in interface design | Flag Red |
| T10.7 | Agent degradation test missing | Flag Red |
| T10.8 | Strict-Class tests not 100% passed | Block |
| T10.9 | Frontend Perspective Convergence not completed (when frontend is included) | Flag Red |

**Decision Point**: canyu decides "Is the merge correct?"

**Rollback Procedure**: Conflict — isolate in isolation zone (t2), do not touch main branch; cross-chain HTTP failure — pull 1 team member to reproduce in isolation zone; 5-Dimension Audit has red — fix code, re-enter parallel development.

**Red/Yellow/Green**:

- Green: Integration Rehearsal passes + 5-Dimension Audit all green + Strict-Class 100% + frontend Perspective Convergence complete
- Yellow: Integration Rehearsal passes but has warnings
- Red: Cross-chain failure / contract inconsistency / audit skips Dimension 2 / Strict-Class not 100%

---

## Round 8: Testing and Release

**Input**: Integrated code + 5-Dimension Audit all green + Integration Rehearsal passed + Strict-Class 100%.

**Outputs**: E2E tests + Scenario Regression test suite + test report + acceptance criteria cross-reference + launch checklist + Inheritance Snapshot final version.

**§4.8 Scenario Regression Test Suite**:

Must produce Scenario Regression test suite before release:
- Fake seed users (f21_ prefix, cleaned up after completion)
- Fake LLM / RAG monkeypatch (to avoid slow real LLM tests)
- Scenario numbers (S01-SN, covering each milestone capability)
- Cross-student isolation security test (user_id strict isolation verification)
- TXT / JSON dual output
- try/finally auto-cleanup

Especially suitable for AI Agent type projects.

**§4.2 Delivery Consistency Acceptance Lock**:

Before release, the delivery report must pass V1-V10 acceptance checklist (see File 06 §III). Core principle: the delivery report is the object being accepted, not a unilateral declaration.

**Key Steps**:

1. E2E testing: real run (no mock), covering complete business flows
2. **Scenario Regression Test Suite** (§4.8): fake seeds + mock + scenario numbers + dual output + cleanup
3. Coverage final check: `pytest --cov=app --cov-fail-under=70`, no relaxation allowed
4. **Evaluation Grading confirmation** (§4.19): Strict-Class 100% + Flexible-Class per threshold
5. Write test report (summarizing 5-Dimension Audit + E2E + Scenario Regression results)
6. Write acceptance criteria cross-reference (item-by-item acceptance, aligned with Round 1b acceptance criteria)
7. **Acceptance Lock V1-V10** (§4.2): delivery report passes 10 checks
8. **Inheritance Snapshot final version** (§4.12): update workflow_state = acceptance passed + latest commit + frozen decision list
9. Performance test (optional): Locust run P95 below 500ms
10. Launch checklist:

```
- .env.example complete
- Database migration ready
- Vector store collection created (when Agent chain is included)
- LLM Provider configuration documentation (when Agent chain is included)
- User manual
- Rollback plan
- Monitoring and alerting
- Log collection
- Inheritance Snapshot final version updated
```

**Triggers**:

| Number | Condition | Judgment |
|------|------|------|
| T11.1 | Coverage below 70% | Block |
| T11.2 | E2E failed | Block |
| T11.3 | 5-Dimension Audit has red | Block |
| T11.4 | Test report or acceptance criteria missing | Block |
| T11.5 | 7-layer documentation has gaps | Block |
| T11.6 | Strict-Class not 100% passed | Block |
| T11.7 | Scenario Regression test suite missing | Block |
| T11.8 | Acceptance Lock V1-V10 not all passed | Block |
| T11.9 | Inheritance Snapshot not updated to final version | Flag Yellow |

**Decision Point**: canyu decides "Whether to release."

**Rollback Procedure**: Release failure — rollback + re-integrate, do not directly re-release; E2E failure — fix code, re-enter parallel development.

**Red/Yellow/Green**:

- Green: E2E passes + Scenario Regression passes + Coverage no less than 70% + audit all green + Strict-Class 100% + Acceptance Lock all passed + 7-layer documentation all complete + Inheritance Snapshot final version
- Yellow: E2E passes but has yellow + Inheritance Snapshot not updated
- Red: E2E failed / audit has red / Strict-Class not 100% / Acceptance Lock not passed / 7-layer documentation has gaps

---

## Prompt Design Principles for the Coordinator

### Principle 1: Place Hard Constraints at the End of the Prompt

AI pays the most attention to content at the end; hard constraints must be placed in a prominent final position.

### Principle 2: Execution Check Items Must Be Verifiable

| Non-Verifiable | Verifiable |
|---------|--------|
| "Must test" | "Must run pytest tests/... -v, commit with output" |
| "Must write interface docs" | "Interface design includes path / method / input params / output params / error codes" |
| "Follow naming standards" | "snake_case / plural table names / singular model names" |
| "Coverage should be high" | "Coverage no less than 70%, no degradation" |

### Principle 3: Forbidden Items Must Be Explicitly Listed

AI does not know by default "what not to do."

### Principle 4: Output Format Must Be Structured

So that AI output can be checked.

### Constraint Balance Experience

| Category | Suggested Quantity | Examples |
|------|---------|------|
| Hard Constraints (must follow) | 5-12 per phase | mock prohibition / locked versions / Coverage no less than 70% / Agent degradation |
| Suggestions (AI discretion) | 3-5 per phase | Index suggestions / error handling |
| Forbidden Items (must be explicit) | 3-7 per phase | Forbid modifying core / forbid mocking critical paths / forbid claiming pass / forbid self-executing pip install |

Violation of hard constraints or forbidden items: Block, Flag Red. Violation of suggestions: Warning, Flag Yellow.

---

> Round 6-8 complete. For quick reference of all templates and triggers, see 04-Appendix; for quick operation reference, see 05-Quick Reference Card.
