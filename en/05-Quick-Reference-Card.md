# 05 — Quick Reference Card

> An operations checklist to keep open alongside during execution. Does not restate concepts — only gives actions.
> Use together with Files 01–04 + 06–08: concepts/templates are in those files; this tells you "where to put your hands, what to type."

---

## A. Per-Round Starting Action Checklist

### General (Effective Every Round)

**Coordinator Start Actions**:
1. Output Declaration Card: `[Mode] caveman={ON|OFF} | §8={ON|OFF} | timebox={N}min | risk={LOW|MEDIUM|HIGH}`
2. Present agenda checklist (5–8 items)
3. After user checks items, begin discussion

**Coordinator Wrap-Up Actions** (every round-end):
1. Produce decision record
2. Update PPM
3. Update inheritance snapshot (workflow_state + frozen decisions + pending items + next step)
4. Check triggers
5. User confirms before proceeding to next round

### Round 0 — Project Seeding

**§4.1 Environment Discipline Runbook Pre-Check**:
```powershell
# 1. Docker running
docker version

# 2. Python cache discipline
# After modifying .py, clear __pycache__
# Run tests / startup with -B

# 3. Windows async driver (Windows + async DB projects)
python -B scripts\run_backend.py
# Forbidden: uvicorn backend.app.main:app --reload
```

**Output Path Checklist**:

| Output | Path |
|---|---|
| .gitignore | `project_root/.gitignore` |
| .env.example | `project_root/.env.example` |
| Project seeding record | `docs/06-project/decision-records/round-00-project-seeding.md` |

**Decision Point**: User confirms top-level directories + Demo assessment.

### Round 1a — Gather Requirements

**§4.10 Empathy Thinking**: For minors / vulnerable groups / served parties / non-explicit-data subjects, proactively identify 1–2 "business-side didn't mention but user-side must have" needs.

**Outputs**:
| Output | Path |
|---|---|
| PRD.md | `docs/02-product/PRD.md` |
| User Stories.md | `docs/02-product/User Stories.md` |
| Raw materials | `docs/02-product/raw/` |

### Round 1b — Classify Requirements

**AI Agent Chain Identification**: Label RAG / Agent Conversation / Recommendation / Sentiment-Monitoring chain types.

**Outputs**:
| Output | Path |
|---|---|
| MVP Scope Definition.md | `docs/02-product/MVP Scope Definition.md` |
| Chain mapping table | Decision record attachment |
| Acceptance Criteria.md | `docs/03-agent/Acceptance Criteria.md` |

**Decision Point**: User confirms "chain classification + MVP scope."

### Round 2a — Implementation Breakdown + Tech Stack

**§4.17 Prompt Versioning Rules** (when Agent chains present): Confirm LLM framework / Provider / Embedding / Vector DB / Prompt versioning / SSE.

**Outputs**:
| Output | Path |
|---|---|
| Task Breakdown Standards.md | `docs/03-agent/Task Breakdown Standards.md` |
| ChainN-todo.md | `docs/03-agent/ChainN-todo.md` |
| Tech Selection.md | `docs/04-technical/Tech Selection.md` |

**Decision Point**: User confirms "tech selection."

### Round 2b — Directory Structure

**§4.13 Contract Freeze**: Lock interface schema / enums / SSE events / frontend-backend field mapping before coding.

**Outputs**:
| Output | Path |
|---|---|
| System Architecture Design.md | `docs/04-technical/System Architecture Design.md` |
| Full directory tree | Disk files |
| Contract Freeze doc | `docs/04-technical/Contract Freeze.md` |
| _chains/ subdirectories | `docs/04-technical/_chains/chainN-xxx/` |

**Decision Point**: Premium upgrade evaluation; if upgrading, user decides.

### Round 3 — Standards Definition

**6 Core Documents**:

| Output | Path |
|---|---|
| AGENTS.md | `docs/03-agent/AGENTS.md` |
| Agent Role Division.md | `docs/03-agent/Agent Role Division.md` |
| Prompt Design Standards.md | `docs/03-agent/Prompt Design Standards.md` |
| AI Agent Prompt Standards.md | `docs/03-agent/AI Agent Prompt Standards.md` (when Agent present) |
| Dev Rules.md | `docs/05-ai-coding/Dev Rules.md` |
| Code Standards.md | `docs/05-ai-coding/Code Standards.md` |
| AI Agent Security Boundary Standards.md | `docs/03-agent/AI Agent Security Boundary Standards.md` (when Agent present) |
| Frontend Standards.md | `docs/05-ai-coding/Frontend Standards.md` (when frontend present) |

**Decision Point**: User confirms "standards."

### Round 4a — Database Design

**§4.18 Memory Architecture Design** (when Agent chains present): 4-layer memory schema + vector DB collection + user_id isolation.

**Outputs**:
| Output | Path |
|---|---|
| DB Design.md | `docs/04-technical/DB Design.md` |
| DDL.sql | `docs/04-technical/DDL.sql` |
| Alembic migration | `alembic/versions/` |

### Round 4b — Framework Construction

**§4.20 SSE Dual-Track** (when Agent present) + **§4.16 Crisis Short-Circuit** (when Agent present).

**Outputs**:
| Output | Path |
|---|---|
| config.py | `backend/app/config.py` |
| main.py | `backend/app/main.py` |
| core/ modules | `backend/app/core/` |
| router.py (placeholder) | `backend/app/api/v1/router.py` |
| Agent framework | `backend/app/ai/agents/` (when Agent present) |
| env_check.py | `scripts/env_check.py` |
| test_health.py | `tests/test_health.py` |
| Module Division.md | `docs/04-technical/Module Division.md` |

**Env dry-run pass criteria**:
```powershell
python scripts/env_check.py   # All green
pytest tests/test_health.py -v  # All pass
```

**Decision Point**: User confirms "skeleton."

### Round 5 — Freeze Audit

**Coordinator runs item by item**:
```
□ Compile all hard-frozen items into a "freeze inventory"
□ Check cross-round dependencies item by item
□ Decide whether key soft-frozen items upgrade to hard-freeze
□ PPM integrity scan
□ Agent contract freeze (when Agent present)
□ Frontend completion definition freeze (when frontend present)
```

**Decision Point**: User confirms "can open the gate."

### Round 6 — Chain Parallel Development

**§4.6 Timebox**: Normal red-light 5 rounds / high-risk 2 rounds / single step exceeds 10min must report.
**§4.15 Agent Degradation**: Every LLM call must have fallback.
**§4.21 Dependency Workflow**:禁止 self pip install.

**Coordinator verification actions**:
```powershell
git checkout feature/chainN-xxx
pytest tests/test_chainN_*.py -v --no-cov
pytest tests/test_chainN_*.py --cov=app --cov-report=term | Select-String "TOTAL"
```

**Decision Point**: User confirms each chain.

### Round 7 — Multi-Chain Integration

**§4.7 E2E Tiering**: fast audit (gate) / full-ai (dress rehearsal).
**§4.19 Evaluation Grading**: Strict-class 100% / Flexible-class by threshold.
**Frontend perspective convergence** (when frontend present).

**Coordinator actions**:
```powershell
git checkout -b t2 origin/main
git merge feature/chain1-xxx
# ... merge one by one
pytest tests/e2e/ -v --no-cov  # Integration rehearsal
ruff check app/
pytest tests/test_chain1_*.py -v  # 5-Dimension Audit Dimension 2
```

**Decision Point**: User confirms "merge."

### Round 8 — Test & Release

**§4.8 Scenario Regression** + **§4.2 Acceptance Lock V1–V10** + **Inheritance snapshot final**.

**Coordinator actions**:
```powershell
pytest --cov=app --cov-fail-under=70
pytest tests/e2e/ -v
python -B scripts/f21_scenario_suite.py  # Scenario regression (if present)
git rev-parse HEAD  # Get latest hash for report
```

**Launch checklist**:
```
□ .env.example complete
□ DB migrations ready
□ Vector DB collection created (when Agent present)
□ LLM Provider config doc (when Agent present)
□ User manual
□ Rollback plan
□ Monitoring & alerting
□ Log collection
□ Inheritance snapshot final updated
□ Acceptance lock V1–V10 all passed
□ Strict-class 100%
```

**Decision Point**: User confirms "release or not."

---

## B. Decision Record Fill Example

See 04-Appendix B.

---

## C. PPM Fill Example

See 04-Appendix C.

---

## D. Session Start Fill Example

See 04-Appendix D.

---

## E. Launch Gate Checklist (8 Items)

```
Launch Gate Checklist

□ 1. Architecture Frozen
   Directory structure fixed + tech stack version-locked + shared modules written

□ 2. Contract Frozen
   Interface design includes path/method/input/output/error codes
   SSE event protocol frozen (when Agent present)
   Enums / frontend-backend field mapping frozen

□ 3. Environment Dry-Run Passed
   scripts/env_check.py all green
   Docker / Vector DB reachable (when Agent present)

□ 4. Smoke Test Passed
   pytest tests/test_health.py all pass

□ 5. 6 Core Documents Complete
   AGENTS.md / Agent Role Division / Prompt Design Standards
   / AI Agent Prompt Standards (when Agent present) / Task Breakdown Standards / Acceptance Criteria

□ 6. Every Chain todo.md Broken Down
   Includes organs + test points + cross-chain dependencies + Agent-specific organs (when Agent present)

□ 7. Whitelist Clear
   What each Agent can / cannot modify

□ 8. Contract Frozen
   Interface schema / enums / SSE events / frontend-backend field mapping
   Contract docs before code

All pass → Notify user "Launch gate all green, requesting gate open"
Any fail → Return to corresponding round to补全
```

---

## F. Coordinator Self-Check Memo (Run Every Round-End)

```
□ All outputs written to files (not left in conversation)
□ Decision record written (incl.达成/否决/待定 + freeze level + overturn conditions)
□ PPM updated
□ Inheritance snapshot updated (workflow_state + frozen decisions + pending + next step)
□ Declaration Card output
□ All relevant triggers checked
□ Pending items annotated with planned resolution round
□ Previous round's pending items have conclusions this round
□ User confirmed this round's content, can proceed to next round
```

---

## G. Runbook Quick Reference (§4.1)

### 3-Second Self-Check Before Every Session Start

- [ ] Docker running?
- [ ] Modified .py last time? If yes, clear `__pycache__` first
- [ ] Backend uses `python -B scripts\run_backend.py`, NOT `uvicorn`

### Common Troubleshooting Table

| Symptom | First Check | Second Check | Fallback |
|---|---|---|---|
| Login "network error" | Is Docker running | `docker compose ps` healthy? | Check backend logs |
| Psycopg ProactorEventLoop | Using uvicorn directly? | Switch to run_backend.py | Check SelectorEventLoopPolicy |
| Changed .py but behavior unchanged | __pycache__ cleared? | -B flag added? | Restart backend |
| Chinese garbled ??? | .pyc cache | LLM provider correct? | .env LLM_PROVIDER |
| LangChain returns empty content | V4 thinking disabled? | model_name correct? | See tech docs |
| RAG retrieval timeout | Milvus healthy? | embedding reachable? | timeout 3s empty return is normal degradation |
| pytest event loop error | async fixture conflict | duplicate import | See test standards |

---

## H. Acceptance Lock Quick Reference (§4.2)

When the dispatcher receives a delivery report, check item by item against this table. Any fail → return.

| # | Check Item | Pass Criteria |
|---|---|---|
| V1 | First-line Declaration Card | Present with all four fields |
| V2 | Commit hash real | `git log --oneline` can find it |
| V3 | Commit order reasonable | Code commits before report commit |
| V4 | Commit message standard | `feat/fix/docs/chore: <scope> <subject>` |
| V5 | Modified files outside forbidden zones | Compare against whitelist |
| V6 | Key code grep-able | Spot-check 3–5 core function names |
| V7 | pytest output genuine | Line count = actual test function count |
| V8 | ruff All checks passed | Failures must be in遗留issues |
| V9 | AC with evidence per item | "Should pass" not accepted |
| V10 |遗留issues section present | "None" counts as present |

---

## I. MCP Quick Reference

| Scenario | Call | Notes |
|---|---|---|
| Mark AC complete | `mark_checked("AC-F20-1", "tests/test_k12_facts.py::TestHistoryRecallIntent", "pytest")` | Reject without evidence |
| Strategy fork pause | `pause_for_user([{"option":"continue fixing","risk":"MEDIUM"},{"option":"degrade","risk":"LOW"}], "Test failure cause unknown")` | forks ≥ 2 |
| Resume after user choice | `resume_from_pause(pause_id, "continue fixing")` | choice must be in forks |
| Report step complete | `report_step("implement", "Implemented mark_checked", ["mcp_server/server.py"])` | content ≤ 500 chars |

evidence_type: `pytest` / `ruff` / `git_log` / `screenshot` / `review`

phase: `read` / `plan` / `implement` / `test` / `wrap_up`

---

## J. Intervention Quick Reference (§7.5 Four Escalation Tiers)

| Tier | Scenario | Action |
|---|---|---|
| L1 Self-resolve | Small decision within design doc scope | Do directly, record via report_step |
| L2 Ask person | Not covered by design doc but low risk | pause_for_user ask person present |
| L3 Request dispatcher | Needs dispatcher to supplement design / decide | Write snapshot dispatch_requests(PENDING) + pause |
| L4 Forced pause | §4.4 / red-light >5 / architecture change | Write snapshot + MUST wait for dispatcher reply |

**ZCode Platform**: Sub-agent real-time intervention (main agent spawns dispatcher sub-agent)
**Other Platforms**: Snapshot mailbox human bridging (user switches sessions to relay)

---

> Quick Reference Card complete. Use together with Files 01–04 + 06–08.
