# Parallel Development Protocol v3.0 — Overview

> Version: v3.0 / 2026-07-03
> Status: Formal Release, Self-Contained Complete Protocol

---

## File Navigation

This protocol consists of 9 files, in reading order:

| File | Content | When to Read |
|---|---|---|
| **00-Overview** (this file) | Philosophy, process overview, track selection, freeze rules, mechanism quick reference, clause index | Read first |
| **01-Serial Conversation Rounds 0–2b** | Project seeding → Requirements → Tech stack → Directory + Contract freeze | Execute round-by-round at project start |
| **02-Serial Conversation Rounds 3–5 & Launch Gate** | Standards → DB + Memory architecture → Framework + SSE + Crisis short-circuit → Freeze audit + Launch gate | After Round 2b completes |
| **03-Parallel Development & Wrap-Up Rounds 6–8** | Parallel coding (incl. Agent degradation / frontend convergence) → Integration (incl. evaluation grading) → Release (incl. scenario regression / acceptance lock) | After launch gate passes |
| **04-Appendix** | Complete triggers, decision record template, PPM template, inheritance snapshot template, intervention request template, MCP reference | Quick lookup during execution |
| **05-Quick Reference Card** | Per-round action checklist, Runbook quick ref, acceptance lock quick ref, MCP quick ref, intervention quick ref | Keep open alongside during execution |
| **06-Constraint Media & MCP** | L0/L1/L2 three-layer definitions, MCP three-tool specs, Declaration Card, Acceptance Lock | When understanding how rules take effect |
| **07-Inheritance Media & Intervention** | Fork / Sub-agent / Snapshot, four escalation tiers, state machine, platform branching | When understanding cross-session collaboration |
| **08-Frontend & Async Division** | Completion definition, perspective convergence, single-source View, DS division, executor-first | When frontend / division of labor is involved |

---

## I. What This Protocol Is

The Parallel Development Protocol is a **conversation-driven multi-AI collaborative development methodology**. It defines the complete process from an empty directory to project release, covering three protocol domains:

- **Complete Development Process**: Rounds 0–8 Serial → Parallel → Wrap-Up, including frontend and AI Agent engineering nodes
- **Full Business Development Paradigms**: CRUD + Frontend (completion definition / perspective convergence / single-source View) + AI Agent (RAG / Memory / SSE / Degradation / Prompt versioning / Crisis short-circuit) + Async division (Dispatcher / Executor / Executor-first)
- **Special Mechanism Supplement**: Constraint media stratification (L0/L1/L2) + Inheritance media (Fork / Sub-agent / Snapshot) + Intervention mechanism (four escalation tiers) + MCP tools + Declaration Card + Acceptance Lock + Environment Runbook

Three core elements:

- **Methodology Layer**: Three-stage process, progressive freezing, three-track tiering
- **Conversation Protocol Layer**: Agenda checklist, decision records, round-by-round confirmation, Declaration Card, delivery consistency acceptance lock
- **Operations Specification Layer**: Freeze determination, triggers, templates, checklists, environment Runbook, frontend completion definition, MCP tool interfaces, inheritance snapshots

---

## II. Core Philosophy

### 2.1 Three Foundational Principles

| Principle | Statement | Manifestation |
|---|---|---|
| Tokens for Time | 1 coordinator driving direction + N AIs executing in parallel | Round 6 multi-agent parallel chain推进 |
| Day 0 vs Day 10 = 4× Rework | Framework must be fully frozen before parallelization | Rounds 0–5 freeze audit + launch gate hard threshold |
| Details Delegatable, Verification Not | Coordinator must personally run dynamic tests | Rounds 6–8 mandatory pytest real-run + 5-Dimension Audit Dimension 2 |

### 2.2 Three Paradigm Shifts

#### Paradigm I: Constraint Medium from Text Layer to Protocol/Tool Layer

Text is a soft constraint; models can softly violate. Tool calls are hard constraints; even the weakest model must invoke them.

| Layer | Medium | Enforcement Strength |
|---|---|---|
| L0 Text | Rule docs / Triggers / Templates | Low (soft constraint) |
| L1 Protocol | Declaration Card / Output Contract / Acceptance Checklist | Medium |
| L2 Tool | MCP tool (cannot produce output without calling) | Very High (hard constraint) |

Migration criterion: Severe violation consequences + repeated text-layer failure → migrate to L2. Moderate consequences + needs cross-round constraint → migrate to L1. Everything else stays at L0. See File 06 for details.

#### Paradigm II: Metrics from Protocol Action Counting to Value/Hour Ratio

LOC / decision counts / candidate clause counts / commit counts are all noise. **Value/hour ratio (user-visible substantive capability increment) is the only true metric.**

Criterion: A round is valid based on "user-visible substantive capability increment," not "went through protocol-mandated steps."

#### Paradigm III: Checks-and-Balances from Self-Triggering to Role Separation

Rules that one interprets and executes oneself are equivalent to no rules. The executor does not write rules; the rule-writer does not self-trigger. Trigger authority for checks-and-balances clauses must be given to a non-executor. See File 06 for details.

---

## III. Three-Stage Process Overview

```
Serial Conversation Stage (9 rounds)
  Round 0 → 1a → 1b → 2a → 2b → 3 → 4a → 4b → 5 (Freeze Audit)
    │ Each round produces decision record + updated PPM + updated inheritance snapshot + user confirmation before proceeding
    ▼
  🚪 Multi-Agent Launch Gate (8 hard conditions, all must be met)
Multi-Agent Parallel Stage
  Round 6: Chain parallel development (incl. Agent degradation / frontend perspective convergence)
Serial Wrap-Up Stage
  Round 7: Multi-chain integration (incl. degradation testing / evaluation grading) → Round 8: Test & Release (incl. scenario regression / acceptance lock)
```

See Files 01/02/03 for details.

---

## IV. Three Tracks

### Demo Mode (Rapid Prototyping)

Entry conditions (four hard thresholds, all required):
- Purpose declaration: Will not go live after completion; demo / concept verification only
- No user data accumulation: SQLite or in-memory sufficient
- No multi-agent parallelization needed: One person, or at most 1 coding agent
- Lifecycle no more than 2 weeks

Compressed to 4 rounds; skip launch gate, skip 5-Dimension Audit, skip E2E testing.

### Standard Track (Default)

All projects default to this track. 9 serial rounds + 1 parallel round + 2 wrap-up rounds = 11 rounds total. Suitable for 2–4 chains, low-to-medium coupling, teams of ≤2 people.

### Premium Track (Full Track)

At the end of Round 2b, the coordinator proactively asks whether to upgrade, based on these 6 indicators:

| Indicator | Standard | Premium |
|---|---|---|
| Chain count | 2–4 chains | 5+ chains |
| Inter-chain coupling | Low coupling | High coupling |
| Tech stack complexity | Single backend + single DB | Microservices / multi-DB / AI models |
| Team size | ≤2 people | 3+ people |
| Requirement stability | Stable | Continuously changing |
| Compliance/security requirements | None special | Compliance audit needed |

3+ indicators sliding toward Premium → may decide to upgrade.

---

## V. Round Overview (Annotated with v3.0 Trigger Points)

| Round | Topic | Core Output | v3.0 Trigger Points |
|---|---|---|---|
| Round 0 | Project Seeding | Top-level directories + git init + .env.example + env dry-run | §4.1 Runbook pre-check |
| Round 1a | Gather Requirements | PRD skeleton + User Stories (with AC) | §4.10 Empathy thinking |
| Round 1b | Classify Requirements | MVP scope + Chain mapping + Acceptance criteria | AI Agent chain identification |
| Round 2a | Implementation Breakdown + Tech Stack | Task breakdown + Chain todos + Tech selection | §4.17 Prompt versioning rules |
| Round 2b | Directory Structure | System architecture + Full directory tree + Premium evaluation | §4.13 Contract freeze + Frontend dir + Agent dir |
| Round 3 | Standards Definition | 6 core docs + Dev rules + Code standards | §4.14 Security boundaries + §4.17 Prompt standards + §4.5 Frontend standards + §4.4 Declaration Card |
| Round 4a | Database Design | DB design + DDL + Alembic | §4.18 Memory architecture design |
| Round 4b | Framework Construction | Shared modules + smoke test | §4.20 SSE dual-track + §4.16 Crisis short-circuit |
| Round 5 | Freeze Audit | Freeze audit report + Integrity scan | Agent contract freeze + Frontend completion definition freeze + Launch gate item 8 |
| | | **After Launch Gate Passes** | |
| Round 6 | Chain Parallel Development | Per-chain code + per-chain tests | §4.15 Agent degradation + §4.6 Timebox + §4.21 Dependency workflow + Frontend parallel |
| Round 7 | Multi-Chain Integration | Merge + Integration rehearsal + 5-Dimension Audit | §4.7 E2E tiering + §4.19 Evaluation grading + Frontend perspective convergence acceptance |
| Round 8 | Test & Release | E2E + Test report + Launch checklist | §4.8 Scenario regression + §4.2 Acceptance lock + Inheritance snapshot final |

---

## VI. Core Mechanism Quick Reference

### Foundational Mechanisms (7 items)

| Mechanism | Function | Effective Rounds |
|---|---|---|
| Three-Tier Freeze (Hard/Soft/Draft) | Distinguish "immutable / extensible / freely adjustable" | Rounds 0–5, every round |
| Progressive Production Map (PPM) | Global doc progress tracking, anti-omission | Updated every round-end |
| Document Skeleton First | Build complete structure on first touch, mark待补 | Every round involving doc output |
| Integrity Scan | Hard check before launch gate | Round 5 |
| Multi-Agent Launch Gate (8 items) | The only channel from serial to parallel | After Round 5 |
| Context Transfer Package | Package accumulated conversation decisions for distribution to agents | At parallel start |
| Decision Records | Record达成/待定/否决 per round, prevent interruption loss | Every round-end |

### Extension Mechanisms (5 items)

| Mechanism | Function | See |
|---|---|---|
| Constraint Media Stratification (L0/L1/L2) | Stratify by enforcement strength; hard constraints under weak models | File 06 |
| Inheritance Media (Fork/Sub-agent/Snapshot) | Cross-session work continuity + role self-identification | File 07 |
| Intervention Mechanism (Four Escalation Tiers) | Executor mid-construction requests dispatcher | File 07 |
| MCP Tools (mark_checked / pause_for_user / report_step) | Evidence enforcement / Fork pause / Report compression | File 06 |
| Environment Discipline Runbook |固化 at startup; no live debugging | 05-G Quick Ref |

---

## VII. Three-Tier Freeze Determination Rules

To determine whether a decision is Hard-Freeze, Soft-Freeze, or Draft, answer three questions in order:

**Q1**: If this decision is overturned, would it require modifying 2 or more already-frozen outputs?
Yes → Hard-Freeze. No → Continue to Q2.

**Q2**: If this decision is overturned, would it change the whitelist boundaries of 2 or more agents?
Yes → Hard-Freeze. No → Continue to Q3.

**Q3**: Is this decision architecture-level (directory structure / cross-module protocols / language and framework)?
Yes → Hard-Freeze. No → Soft-Freeze.

Draft: Content newly produced this round, not yet confirmed.

**Default strategy**: When ambiguous, always mark Soft-Freeze; decide on upgrade during the freeze audit round. Soft-freeze can upgrade to hard (audit round hardening); hard-freeze downgrading to soft requires rollback protocol (high cost).

**Every hard-frozen decision MUST include**: an "overturn conditions" field.

---

## VIII. Anti-Omission Mechanisms

### Layer 1: Document Skeleton First
When any document is first created, build the complete chapter skeleton first; mark gaps with `[To be completed in Round X]`.

### Layer 2: Progressive Production Map (PPM)
Global progress tracking table updated every round-end. At the start of the next round, glance at it — red and yellow are omission signals.

### Layer 3: Integrity Scan
Hard threshold of Round 5 freeze audit round. Scan content:
- Under the 7-layer docs, directories marked "this round needed" must have no empty files
- 6 core docs — missing any one blocks (v3.0 expanded from 5 to 6, added AI Agent Prompt Standards)
- Every chain's interface design must include path/method/input/output/error codes
- Every chain's todo must have test point annotations per organ
- All in-progress items in PPM must be converted to complete
- Any doc with待补充 markers involving this round's mandatory output → block

### Layer 4: Checks-and-Balances Trigger Authority Externalization
Trigger authority for checks-and-balances clauses (fork pause, timebox timeout, mandatory confirmation items) is given to a non-executor:
- Fork pause: triggered by independent acceptance role or MCP `pause_for_user`
- [x] Evidence enforcement: validated by `mark_checked` tool
- Mandatory confirmation items (§4.4): confirmed by dispatcher with user before launch

Before MCP落地: rely on role separation + manual acceptance. After MCP落地: rely on tools.

---

## IX. Core Rules

- Claims of passing MUST include pytest output
- Critical paths (LangChain / cross-chain HTTP / SSE) — mock禁用
- Version pinning;禁止 "latest"
- 7-layer doc directory structure + `_chains/` chain isolation zones
- Backend files organized by business object;禁止 naming by chain number
- 5-Dimension Audit Dimension 2 (dynamic testing) is mandatory; no skipping allowed
- Code coverage ≥70%; no lowering the threshold

---

## X. v3.0 Clause Index (21 Clauses)

| # | Clause | Embedded In Round | Detail File |
|---|---|---|---|
| §4.1 | Environment Discipline Runbook | R0 | 05-G |
| §4.2 | Delivery Consistency Acceptance Lock | R8 | 06-III |
| §4.3 | Async Division Protocol | R6 | 08-IV |
| §4.4 | Declaration Card | Every Round | 06-III |
| §4.5 | Frontend Completion Definition | R3/R6/R7 | 08-I |
| §4.6 | Timebox + Red-Light Tiering | R6/R7 | 01-General |
| §4.7 | E2E Tiering | R7/R8 | 03-R7 |
| §4.8 | Scenario Regression Test Suite | R8 | 03-R8 |
| §4.9 | Long-Chain Concurrency & Disk Write | R6 | 03-R6 |
| §4.10 | Empathy Thinking Principle | R1a/R1b | 01-R1a |
| §4.11 | Vibe Coding Red Line | Throughout | This file §II |
| §4.12 | Inheritance Media Fallback | Every Round | 07 |
| §4.13 | Contract Freeze | R2b/R5 | 01-R2b |
| §4.14 | AI Agent Security Boundary | R3/R6 | 02-R3 |
| §4.15 | Agent Degradation Strategy | R6/R7 | 03-R6 |
| §4.16 | Crisis Response Short-Circuit | R4b | 02-R4b |
| §4.17 | Prompt Versioning & Security Constraints | R2a/R3 | 02-R3 |
| §4.18 | Memory Architecture Design | R4a | 02-R4a |
| §4.19 | Evaluation Grading | R7/R8 | 03-R7 |
| §4.20 | True-Streaming SSE Dual-Track | R4b | 02-R4b |
| §4.21 | Dependency Addition Workflow | R6 | 03-R6 |

---

## Version

- v3.0 / 2026-07-03 / Formal Release
  - 9 files, 21 clauses embedded into Round workflow
  - Three-domain coverage: complete process + full business paradigms + special mechanisms
  - Self-contained complete protocol; no external version references required
