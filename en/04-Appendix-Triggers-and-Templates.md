# 04 — Appendix: Triggers and Templates Complete Reference

> A quick-reference manual for daily execution. Complete trigger inventory, Decision Record Template, PPM template, Session Start Template, Inheritance Snapshot Template, Intervention Request Template, MCP reference, and Rollback Procedure Master Table.

---

## A. Complete Trigger Inventory

### Round 1b (Requirements Classification)

| # | Condition | Verdict |
|------|------|------|
| T2.1 | Chain count exceeds 6 | Warning, too many, consider merging |
| T2.2 | A chain has fewer than 3 stories | Warning, too small, consider merging |
| T2.3 | Acceptance criteria missing or too abstract | Flag Red |
| T2.4 | Chains overlap with each other | Flag Red |
| T2.5 | Agent chain type not labeled (RAG/Agent/Recommendation/Sentiment) | Flag Red |

### Round 2a (Implementation Breakdown + Tech Stack)

| # | Condition | Verdict |
|------|------|------|
| T3.1 | Each chain has no fewer than 8 organs | Pass if granularity is reasonable |
| T3.2 | Any organ without test points marked | Flag Red |
| T3.3 | Task breakdown spec lacks "Task Granularity Criteria" | Flag Red |
| T3.4 | Cross-chain dependencies not marked | Flag Red |
| T3.5 | Chain todo missing or too few organs | Flag Red |
| T3.6 | Agent chain todo missing Agent-specific organs | Flag Red |
| T4.1 | Using "latest version" without pinning | Flag Red |
| T4.2 | No "Alternative" or "Risk" | Flag Yellow |
| T4.3 | Version number missing | Flag Red |
| T4.4 | Version incompatibility between different technology choices | Flag Red |
| T4.5 | Agent chain but LLM framework/Embedding/Vector DB versions not confirmed | Flag Red |

### Round 2b (Directory Structure)

| # | Condition | Verdict |
|------|------|------|
| T5.1 | Directories organized by technical layer under backend/app/ | Fix |
| T5.2 | No 7-layer directory structure under docs/ | Fix |
| T5.3 | _chains/ not created or missing a chain subdirectory | Block |
| T5.4 | _chains/ chain Agent told "write here first" before parallel work | Must Run |
| T5.5 | chain_routes.py or chainN_*.py appears under backend api/v1/ | Flag Red |
| T5.6 | Has Agent chain but ai/agents/ directory not created | Flag Red |
| T5.7 | Has frontend but _shared/views/ single-source View directory not created | Flag Red |
| T5.8 | Contract freeze document missing (API schema/enums/SSE events/field mappings) | Block |

### Round 3 (Standards Definition)

| # | Condition | Verdict |
|------|------|------|
| T6.1 | Each AI collaboration rule lacks corresponding execution check item | Flag Red |
| T6.2 | AGENTS.md missing 4 essential elements | Flag Red |
| T6.3 | Coding Standards.md missing "Dynamic Testing Standards" subsection | Flag Red |
| T6.4 | Dev Rules.md — 5 standard rules modified or removed | Flag Red |
| T6.5 | Agent Responsibility Division.md missing "Do/Don't" | Flag Red |
| T6.6 | Prompt Design Spec.md missing "Task Template" | Flag Red |
| T6.7 | Has Agent chain but missing AI Agent Prompt Spec.md | Flag Red |
| T6.8 | Has Agent chain but missing AI Agent Security Boundary Spec.md | Flag Red |
| T6.9 | Has frontend but missing Frontend Spec.md | Flag Red |

### Round 4a (Database Design)

| # | Condition | Verdict |
|------|------|------|
| T7.1 | Table/field names inconsistent with code | Flag Red |
| T7.2 | No is_deleted field | Flag Red |
| T7.3 | No created_at / updated_at | Flag Red |
| T7.4 | No Alembic migration | Flag Red |
| T7.5 | Missing foreign keys / missing indexes | Flag Yellow |
| T7.6 | Has Agent chain but no memory architecture design | Flag Red |
| T7.7 | Memory architecture lacks user_id isolation scheme | Flag Red |

### Round 4b (Overall Framework Construction)

| # | Condition | Verdict |
|------|------|------|
| T8.1 | Environment rehearsal failed | Block |
| T8.2 | Smoke test failed | Block |
| T8.3 | Config missing extra="ignore" | Block |
| T8.4 | router.py contains business routes | Flag Red |
| T8.5 | _chains/ not yet created | Block |
| T8.6 | Has Agent chain but Agent framework not constructed | Flag Red |
| T8.7 | Has Agent chain but SSE protocol skeleton not implemented | Flag Red |
| T8.8 | Has Agent chain but crisis circuit-breaker not implemented | Flag Red (Block release) |
| T8.9 | Has Agent chain but vector DB unreachable with no fallback | Flag Yellow |

### Round 6 (Parallel Chain Development)

| # | Condition | Verdict |
|------|------|------|
| T9.1 | Team member says "tests pass" but no pytest output attached | Flag Red |
| T9.2 | Team member mocked LangChain / SSE / cross-chain HTTP | Flag Red |
| T9.3 | Coverage below 70% | Flag Red |
| T9.4 | Interface design missing a new interface | Flag Red |
| T9.5 | Cross-chain calls not marked in interface design | Flag Red |
| T9.6 | Chain Agent modified shared files like core/ router.py | Flag Red |
| T9.7 | Commit message without test output | Flag Red |
| T9.8 | Chain Agent ran pip install on their own | Flag Red |
| T9.9 | Agent chain has no fallback path | Flag Red |
| T9.10 | Agent chain has no crisis circuit-breaker | Flag Red |

### Round 7 (Multi-Chain Integration)

| # | Condition | Verdict |
|------|------|------|
| T10.1 | Shared file conflicts by "chain number" appear | Flag Red |
| T10.2 | Cross-chain calls depend on mock | Flag Red |
| T10.3 | 5-dimension audit skipped dimension 2 | Flag Red |
| T10.4 | Chain Agent directly writes main directory files | Flag Red |
| T10.5 | Integration rehearsal failed | Flag Red |
| T10.6 | Cross-chain calls not marked in interface design | Flag Red |
| T10.7 | Agent fallback test missing | Flag Red |
| T10.8 | Strict-class tests not passing at 100% | Block |
| T10.9 | Frontend view convergence not completed (when frontend included) | Flag Red |

### Round 8 (Testing & Release)

| # | Condition | Verdict |
|------|------|------|
| T11.1 | Coverage below 70% | Block |
| T11.2 | E2E failed | Block |
| T11.3 | 5-dimension audit has red | Block |
| T11.4 | Test report or acceptance criteria missing | Block |
| T11.5 | 7-layer documentation incomplete | Block |
| T11.6 | Strict-class not passing at 100% | Block |
| T11.7 | Scenario-based regression test suite missing | Block |
| T11.8 | Acceptance Lock V1-V10 not all passed | Block |
| T11.9 | Inheritance snapshot not updated to final version | Flag Yellow |

---

## B. Decision Record Template

Produced by the Coordinator at the end of each round in this format. Storage path: `docs/06-project/决策记录/round-NN-主题.md`.

```markdown
# Decision Record — Round N: [Topic]

> Time: 2026-XX-XX
> Previous Round: round-N-1-xxx.md
> Next Round: Round N+1: [Topic]

## 1. Inputs for This Round
- Previous round decision record: docs/06-project/决策记录/round-N-1-[Topic].md
- Current PPM: [link]

## 2. Agenda Item Tally for This Round
| # | Agenda Item | Selection | Result |
|---|-------------|-----------|--------|
| 1 | [Item name] | Discuss This Round | 达成(Agreed) |
| 2 | [Item name] | Discuss This Round | Partially 待定(Pending) |
| 3 | [Item name] | Quick Pass | Default approach approved |
| 4 | [Item name] | Defer to Next Round | Postponed to Round N+1 |

## 3. Outputs for This Round
| Output | Path | Status | Freeze Level |
|--------|------|--------|-------------|

## 4. Decision Record
### 达成(Agreed)
- Decision 1: [Content]
  - Freeze Level: Hard-Freeze / Soft-Freeze
  - Reversible condition: [Write "None" if none]
  - Files involved: ...

### 否决(Rejected)
- Rejected 1: [Content] — Reason: [Why rejected]

### 待定(Pending) (Deferred to Next Round)
| # | Pending Item | Reason for Deferral | Planned Round |
|---|-------------|---------------------|---------------|

## 5. Trigger Check
| Trigger | Result | Handling |
|---------|--------|----------|

## 6. PPM Changes This Round
| Document | Before This Round | After This Round |
|----------|-------------------|------------------|

## 7. Inheritance Snapshot (§4.12)
| Field | Value |
|-------|-------|
| Current Role | Dispatcher |
| Task Phase | [Phase] |
| Latest Commit | {hash} |
| Frozen Decisions | [Summary] |
| Pending Items | [Summary] |
| Next Step | [Explicit user directive] |

## 8. canyu Confirmation
- [ ] Confirmed for this round, proceed to Round N+1
- [ ] Revisions needed (Items: ...)
```

---

## C. PPM Progressive Production Map Template

Updated at the end of each round. Review at the start of the next round — red and yellow are omission signals.

```markdown
# Progressive Production Map — [Project Name]
> Last Updated: Round N

## Project Meta-Info
| Field | Value |
|-------|-------|
| Project Name | [Project Name] |
| Track | Standard / Premium / Demo |
| Current Round | Round N |
| Chain Count | N chains |
| Agent Count | N agents |

## 02-product/ — Product Layer
| Document | Round 1a | Round 1b | Round 2a | Status |
|----------|----------|----------|----------|--------|
| PRD.md | Skeleton | Done | — | Done |
| 用户故事.md | 5/15 | 12/15 | 15/15 | Done |
| MVP 范围定义.md | — | Draft | Done | Done |

## 03-agent/ — AI Agent Layer
| Document | Round 1b | Round 2a | Round 3 | Status |
|----------|----------|----------|---------|--------|
| AGENTS.md | — | — | Done | Done |
| Agent 职责划分.md | — | — | Done | Done |
| Prompt 设计规范.md | — | — | Done | Done |
| AI Agent Prompt 规范.md | — | — | Done | Done |
| 任务拆分规范.md | — | Done | — | Done |
| 验收标准.md | Done | — | — | Done |
| AI Agent 安全边界规范.md | — | — | Done | Done |
| 链路N-todo.md | — | 4/4 chains | — | Done |

## 04-technical/ — Technical Layer
| Document | Round 2a | Round 2b | Round 4a | Round 4b | Status |
|----------|----------|----------|----------|----------|--------|
| 技术选型.md | Done | — | — | — | Done |
| 系统架构设计.md | — | Done | — | — | Done |
| 数据库设计.md | — | — | Done | — | Done |
| 模块划分.md | — | — | — | Done | Done |
| 契约冻结文档.md | — | Done | — | — | Done |
| _chains/chain1-xxx/接口设计.md | — | — | — | — | Await Round 6 |

## 05-ai-coding/ — AI Coding Layer
| Document | Round 3 | Status |
|----------|---------|--------|
| 开发规则.md | Done | Done |
| 代码规范.md | Done | Done |
| 前端规范.md | Done | Done |

## 06-project/ — Project Execution Layer
| Document | Status |
|----------|--------|
| 决策记录/round-00-项目播种.md | Done |
| ... | |

## 07-testing/ — Testing Layer
| Document | Status |
|----------|--------|
| 测试报告.md | Await Round 8 |
| 验收标准对照.md | Await Round 8 |
| 场景化回归测试集 | Await Round 8 |

## Legend
| Mark | Meaning |
|------|---------|
| — / Blank | This round does not involve this document |
| 未开始 | Not yet touched |
| Skeleton / 5/15 | In progress (progress description attached) |
| 完成 | Done this round |
| 最终完成 | Final — no further changes |
| 阻塞 | Blocked (reason attached) |
| 待 Round X | Planned for marked round |
```

---

## D. Session Start Template

The Coordinator presents an agenda checklist at the start of each round. The user selects from three options: "Discuss This Round / Defer to Next Round / Quick Pass".

```markdown
## Round N: [Topic for This Round]
> Previous Round: Round N-1 [Topic] | Next Round: Round N+1 [Topic]

[Mode] caveman={ON|OFF} | §8={ON|OFF} | timebox={N}min | Risk={LOW|MEDIUM|HIGH}

### Agenda Checklist (Total M items, please select)

#### Must Discuss
□ [Core agenda item 1]
  - Background: [Why discussion is needed]
  - Documents involved: [Which file]
  - Expected output: [What will be produced after discussion]

#### Optional
□ [Optional agenda item 1]
  - Background: ...
  - If not discussed: Default to [default approach]

#### Automated Checks
□ [Check item 1: Trigger T.X.Y]
□ [Check item 2: Trigger T.X.Y]

### Carry-Over from Previous Round
待定(Pending) items:
- [Pending 1]: Unresolved from last round, continue this round

### Freeze Pre-Assessment for This Round
- [Output A] → Pre-assessed Hard-Freeze (Reason: ...)
- [Output B] → Pre-assessed Soft-Freeze (Reason: ...)

### Current PPM Snapshot
| Item of Concern | Status | Target for This Round |
|----------------|--------|----------------------|
```

---

## E. Rollback Procedure Master Table

| Scenario | Round Where It Occurs | Handling |
|----------|----------------------|----------|
| Unreasonable directory structure | Round 0 | Return to Round 0 and redo |
| Conflicting requirements | Round 1a | Confirm with business side, revise user stories |
| Chain overlap | Round 1b | Return to Round 1a to re-classify |
| MVP is vague | Round 1b | canyu decides |
| Tech stack won't run after selection | Round 2a | Troubleshoot versions; don't easily swap tech stack |
| Unreasonable directory structure | Round 2b | Redesign; don't write code on a wrong structure |
| Contract change | Round 2b+ | Return to Round 2b to re-freeze contract |
| Standards cannot be enforced | Round 3 | Don't redesign; record as exception for Round 8 postmortem |
| Table structure inconsistent with standards | Round 4a | Realign |
| Memory architecture lacks isolation | Round 4a | Redesign user_id isolation scheme |
| Skeleton won't run | Round 4b | Troubleshoot config / dependencies / versions; don't rewrite architecture |
| Agent framework missing | Round 4b | Supplement Agent framework construction; don't skip |
| Hard-freeze decision is wrong | Round 5 | Return to corresponding round for re-discussion; downgrade affected outputs |
| Single chain failure | Round 6 | Isolate and debug that chain; don't break the skeleton |
| Integration conflict | Round 7 | Resolve in isolation zone (t2); don't touch main branch |
| Cross-chain HTTP failure | Round 7 | Pull 1 team member to reproduce in isolation zone |
| Strict-class not at 100% | Round 7/8 | Fix code; release not allowed |
| Release failure | Round 8 | Rollback + re-integrate; don't directly re-release |
| Late discovery of a wrong hard-freeze decision | Any round | Flag Red, return to that round for re-discussion; subsequent outputs not automatically voided; Coordinator determines impact scope |

---

## F. Combat Postmortem Lessons

| # | Lesson | Corresponding Trigger |
|---|--------|----------------------|
| 1 | Commit message "claims pass" but pytest was never actually run | T8.3 + T9.7 |
| 2 | Coordinator only runs ruff, not pytest | T10.3 + T11.3 |
| 3 | Mocking critical paths (LangChain / SSE / cross-chain HTTP) | T9.2 |
| 4 | Shared files named by chain number | T5.5 + T6.1 |
| 5 | Documentation lacks 7-layer structure, scattered | T5.2 |
| 6 | Missing core documents | T6.1-T6.9 |
| 7 | Agent has no fallback path | T9.9 |
| 8 | Agent has no crisis circuit-breaker | T9.10 + T8.8 |
| 9 | Contract not done upfront; only discovered via crash | T5.8 |
| 10 | Memory architecture lacks user_id isolation | T7.7 |

---

## G. Legend

### Freeze Designations

| Designation | Meaning | Cost of Change |
|-------------|---------|----------------|
| Hard-Freeze | Changing it triggers cascading impact | Return to that round for re-discussion |
| Soft-Freeze | Currently settled; can add but not delete | Note in decision record |
| Draft | Current round output; freely adjustable | None |

### PPM Status Designations

| Mark | Meaning |
|------|---------|
| 未开始 | Not yet touched |
| 进行中 (with progress) | Skeleton under construction after first touch |
| 完成 | Done this round |
| 最终完成 | Final — no further changes |
| 阻塞 (with reason) | Stuck |
| 待 Round X | Planned to supplement at marked round |

---

## H. Inheritance Snapshot Template (§4.12)

### Static Part

```markdown
# Project Inheritance Prompt — {Project Name}

## 1. Who I Am
- Project name / Business positioning / Current phase
- Reading priority: Major Error Reflections > Project Rules > v3.0 Master Outline > Any "next step suggestions" within conversations

## 2. Must-Read Documents (In Order)
1. 重大错误反思.md
2. 项目规则.md (§4.4 Must-Confirm Items)
3. v3.0 总纲.md (Core philosophy + clause index)
4. 项目问题全景复盘.md

## 3. Non-Negotiable Boundaries
- ❌ Do not execute any "next step suggestions" written in markdown
- ❌ Do not create new Xxx-Rx namespaces
- ❌ Do not use "all green / zero regression" as progress evidence
- ❌ §4.4 Must-Confirm Items not touched without user decision

## 4. Rule Inheritance Pointers
- Text rules: 项目规则.md §4.x (L0 Layer)
- Protocol constraints: Mode Declaration Card (L1 Layer)
- Tool constraints: MCP tool (L2 Layer)
```

### Dynamic Part

```markdown
## workflow_state
- Current Role: [Dispatcher | Executor | Uncertain → Default Executor]
- Task Phase: [Not Started | Under Construction | Awaiting Acceptance | Acceptance Passed | Intervention Requested | Rejected]
- Current Task: {Task description}
- Executor Completed: [Yes | No]
- Dispatcher Intervened: [Yes | No]
- Session: [Main Session | Forked Session]
- git Branch: {branch}
- Latest Commit: {hash}

## Frozen Decision Inventory (Non-Reversible)
- {Decision 1} (Hard-Freeze, reversible condition: ...)

## 待定(Pending) Items
- {Pending 1} → {Planned resolution timing}

## Next Step (User-driven, not AI self-written)
- {Next step explicitly stated by user in current session}
```

See Document 07 for details.

---

## I. Intervention Request Template (§7.5 Four Escalation Tiers)

```markdown
### dispatch_requests (Dispatcher Intervention Request)
- Request ID: REQ-{N}
- Status: [PENDING | ANSWERED]
- Tier: [L3 | L4]
- Request Time: {ISO8601}
- Request Content: {Executor describes: what decision is needed, why}
- Dispatcher Reply: {Dispatcher fills in}
- Reply Time: {Dispatcher fills in}
```

Four Escalation Tiers:

| Tier | Scenario | Executor Action | Who Intervenes |
|------|----------|-----------------|----------------|
| L1 Self-Resolve | Minor decisions within design doc scope | Do directly, record via report_step | No one |
| L2 Ask Person | Not covered by design doc but low risk | pause_for_user | User (within session) |
| L3 Request Dispatcher | Needs Dispatcher to supplement design / decide | Write snapshot dispatch_requests + pause | Dispatcher (cross-session) |
| L4 Mandatory Pause | §4.4 / Red flags >5 / Architecture change | Write snapshot + must wait for reply | Dispatcher (mandatory) |

See Document 07 §四 for details.

---

## J. MCP Tool Reference (L2 Tool Layer)

| tool | Function | Corresponding Protocol | Spec |
|------|----------|----------------------|------|
| `mark_checked(item_id, evidence_url, evidence_type)` | Mark AC complete; reject without evidence | Acceptance Lock V7/V9 | Doc 06 §四 |
| `pause_for_user(forks, context)` | Strategy fork pause | §4.6 Fork Pause | Doc 06 §四 |
| `resume_from_pause(pause_id, choice)` | Resume after user selection | §4.6 companion | Doc 06 §四 |
| `report_step(phase, content, artifacts)` | Report step completion, ≤500 chars | Report compression + D5 | Doc 06 §四 |

evidence_type allowed values: `pytest` / `ruff` / `git_log` / `screenshot` / `review`

phase allowed values: `read` / `plan` / `implement` / `test` / `wrap_up`

---

> End of Appendix. For operational quick reference, see 05-操作速查卡.
