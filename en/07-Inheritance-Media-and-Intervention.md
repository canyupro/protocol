# 07 — Inheritance Media & Intervention Mechanism

> Constraint Media (File 06) governs "how rules take effect." This document governs "how work content persists + cross-session / cross-agent intervention."
> Trigger scenarios: session truncated by length limit / API degradation / platform failure / proactive model switch / new session first-day load / executor mid-construction needs dispatcher intervention.

---

## I. Inheritance Media Positioning

### 1.1 The Problem

Constraint Media (L0/L1/L2) ensures a new model **follows the rules**, but does not ensure the new model **knows the context**:
- MCP `mark_checked` cannot stop "new model doesn't know we're at Round 7 step 3"
- MCP `pause_for_user` cannot stop "new model doesn't know why decision X chose A over B" and overturns frozen decisions
- Rule text cannot stop "new model doesn't read major error postmortems" and slides into restart

### 1.2 Positioning

Inheritance Media fills this gap: **any LLM接手时, reading the inheritance snapshot restores work context + rule inheritance + boundary awareness.**

---

## II. Three-Layer Carriers

Inheritance Media is not a single mechanism but three layers of carriers, each with its own role:

| Carrier | Layer | Function | Platform Dependency |
|---|---|---|---|
| Session Fork | Session layer | Fork naturally carries prior conversation context | Only ZCode supports context preservation |
| Sub-Agent | Communication layer | Main agent spawns sub-agent, replacing human bridging | ZCode supports independent model; others don't |
| Inheritance Snapshot | State layer | Confirms current role/stage + declares non-crossable boundaries | All platforms (filesystem) |

### 2.1 Session Fork (ZCode-specific)

After ZCode session forks, the new session naturally carries prior conversation context. This is the primary channel for context inheritance.

**Limitation**: Forks are one-way — after forking, the user interacts with the executor on the fork side; the main session cannot perform mid-course bidirectional calibration. The Declaration Card (File 06 §III) fills this dimension that forks cannot cover: "per-round bidirectional calibration."

### 2.2 Sub-Agent (ZCode optimal)

ZCode sub-agents support independent model configuration. The main agent can directly spawn a dispatcher sub-agent to handle intervention requests; the user never switches sessions.

**Capabilities**:

| Capability | Status |
|---|---|
| Invocation mechanism | ✅ Available |
| Independent context | ✅ Sub-agent does not inherit main session history |
| Independent model config | ✅ Each sub-agent can specify a different model |
| A2A direct communication | ❌ Hub-and-spoke, must go through main agent relay |
| Background execution | ❌ Foreground only; main agent waits for sub-agent return |

**Key insight**: Sub-agents do not replace inheritance snapshots. Sub-agents have independent context and MUST rely on inheritance snapshots to know "who I am, where I am." Sub-agents replace human bridging (communication problem), not snapshots (state problem).

### 2.3 Inheritance Snapshot (All Platforms)

The inheritance snapshot does not bear the responsibility of "restoring all context." The snapshot only bears: confirming current workflow state + declaring non-crossable boundaries + recording construction facts.

---

## III. Inheritance Snapshot Template

### 3.1 Static Part (Write Once, Mostly Fixed)

```markdown
# Project Inheritance Prompt — {Project Name}

## 1. Who I Am
- Project name / business positioning / current stage
- Reading priority: Major Error Postmortems > Project Rules > v3.0 Overview > Any "next steps" in conversations

## 2. Must-Read Docs (In Order)
1. Major Error Postmortems.md (§"Notes to Future AI Coordinators" + §"Things No Longer Done")
2. Project Rules.md (§4.4 Mandatory Confirmation Items)
3. v3.0 Overview.md (core philosophy + clause index)
4. Project Issues Panoramic Review.md (closed/open issue ledger)

## 3. Non-Crossable Boundaries
- ❌ Do not execute any "next steps" written in markdown
- ❌ Do not create new Xxx-Rx namespaces
- ❌ Do not use "all green / zero regression" as progress evidence
- ❌ Do not add clauses to Project Rules.md unless user explicitly says "elevate to §"
- ❌ §4.4 Mandatory Confirmation Items — do not touch without user approval

## 4. Rule Inheritance Pointers
- Text rules: Project Rules.md §4.x (L0 layer)
- Protocol constraints: Declaration Card / Output Contract (L1 layer)
- Tool constraints: MCP tools (L2 layer)
```

### 3.2 Dynamic Part (Updated Every Step, Mandatory Artifact)

```markdown
## workflow_state
- Current role: [Dispatcher | Executor | Uncertain → default Executor]
- Task stage: [Not Started | In Construction | Awaiting Acceptance | Accepted | Intervention Requested | Returned]
- Current task: {task description}
- Executor completed: [Yes | No]
- Dispatcher intervened: [Yes | No]
- Session: [Main Session | Fork Session]
- Git branch: {branch}
- Latest commit: {hash}

## Frozen Decision Inventory (Do Not Overturn)
- {Decision 1} (Hard-frozen, overturn condition: ...)

## Pending Items (Deferred To When)
- {Pending 1} → {planned resolution timing}

## Next Step (User-Driven, NOT AI-Written)
- {User explicitly stated next step in current session}
> AI must not fill in self-written todos here
```

### 3.3 Implementation

Do not create a new standalone document; embed the inheritance snapshot into existing artifacts:

| Existing Artifact | Modification |
|---|---|
| Decision Record template | Add "Inheritance Snapshot" section after "This Round's Outputs" section |
| Major Error Postmortems §"Notes to Future AI Coordinators" | Upgrade to static template's "Rule Inheritance Pointers" |

Every round-end (or every verifiable output completion in free development) MUST update the inheritance snapshot.

---

## IV. Cross-Session Intervention Mechanism

### 4.1 Trigger Scenarios

- Executor encounters situation not covered by design docs, needs dispatcher to supplement design
- Executor encounters fork decision (change architecture? touch §4.4?)
- Executor red-light exceeds 5 rounds (§4.6 timebox triggered)

### 4.2 Four Escalation Tiers

| Tier | Scenario | Executor Action | Who Intervenes |
|---|---|---|---|
| L1 Self-resolve | Small decision within design doc scope | Do it directly, record via report_step | No one |
| L2 Ask person | Not covered by design doc but low risk | pause_for_user ask person present | User (within session) |
| L3 Request dispatcher | Needs dispatcher to supplement design / decide | Write snapshot dispatch_requests + pause | Dispatcher (cross-session) |
| L4 Forced pause | §4.4 / red-light >5 / architecture change | Write snapshot + MUST wait for dispatcher reply | Dispatcher (mandatory) |

### 4.3 Intervention Methods by Platform

**ZCode Platform — Sub-Agent Real-Time Intervention (Optimal)**:

```
Main Agent (ZCode main session)
  spawn Executor sub-agent (DeepSeek) → construct
    Hit L3 → write snapshot dispatch_requests → return "dispatcher intervention needed"
  Main agent receives return
    spawn Dispatcher sub-agent (ZCode model) or main agent handles directly
      Read snapshot → write reply → return decision
  Main agent receives decision
    spawn Executor sub-agent to continue → read snapshot reply → construct → complete
  Main agent final acceptance
```

User stays in main session throughout; no fork switching needed.

**Other Platforms — Snapshot Mailbox Human Bridging**:

```
Executor (fork session / independent session) constructs
  Hit L3 → write snapshot dispatch_requests(PENDING) → inform present user
User switches to main session → informs dispatcher
  Dispatcher reads snapshot → writes reply (ANSWERED)
User switches back to executor session → informs "reply is in snapshot"
Executor reads snapshot reply → continues construction
```

### 4.4 Snapshot Mailbox Fields

```markdown
### dispatch_requests (Dispatcher Intervention Requests)
- Request ID: REQ-{N}
- Status: [PENDING | ANSWERED]
- Tier: [L3 | L4]
- Request time: {ISO8601}
- Request content: {Executor description: what decision is needed, why}
- Dispatcher reply: {Dispatcher fills in}
- Reply time: {Dispatcher fills in}
```

### 4.5 Sub-Agent vs Snapshot Mailbox

| Dimension | Sub-Agent (ZCode) | Snapshot Mailbox (Generic) |
|---|---|---|
| Communication | Main agent auto-relay | Human bridging |
| Real-time | Synchronous (main agent waits) | Async (session-switch latency) |
| User burden | Low (stay in main session) | High (switch sessions to bridge) |
| Context | Sub-agent independent context (needs snapshot supplement) | Fork inheritance or snapshot recovery |
| Audit trail | Sub-agent return + snapshot | Snapshot file |

---

## V. State Machine

### 5.1 State Definitions

```
  [INIT] ──read inheritance snapshot──→ [Role Determination]
                                            │
              ┌─────────────────────────────┼─────────────────────────────┐
              ▼                             ▼                             ▼
         [Dispatcher]                  [Executor]                   [Uncertain]
              │                             │                             │
              │                        Construct directly                 │ Default to Executor
              │                             │                             │ Don't proactively issue commands
              │                             ▼                             │
              │                      [In Construction] ──L3/L4──→ [Intervention Requested]
              │                             │                               │
              │                             │                          ┌────┴────┐
              │                             │                          ▼         ▼
              │                             │                     Sub-Agent   Snapshot Mailbox
              │                             │                     (ZCode)      (Generic)
              │                             │                          │         │
              │                             │                          ▼         ▼
              │                             │                     [Dispatcher Replied] ←──┘
              │                             │                          │
              │                             │◄─────────────────────────┘
              │                             │
              │                       [Awaiting Acceptance]
              │                             │
              └──final acceptance───────────┘
                    │
              [Accepted] → [Update Snapshot] → Next Task
              [Rejected] → [Returned] → [In Construction]
```

### 5.2 Role Self-Identification Rules

| Snapshot State |接手 Model Determines | Behavior |
|---|---|---|
| `executor_completed=No, dispatcher_intervened=No` | **Executor** | Construct directly (executor-first) |
| `executor_completed=Yes, dispatcher_intervened=No` | **Dispatcher** (default) | Do final acceptance (executor done, dispatcher late-arriving) |
| `executor_completed=No, dispatcher_intervened=Yes` | **Executor** | Continue construction |
| `executor_completed=Yes, dispatcher_intervened=Yes` | **Uncertain** | Default to Executor, ask user to confirm |
| `Uncertain` | **Executor** (default) | Don't proactively issue commands; wait for user or snapshot to clarify |

**Key design**: When uncertain, default to Executor — the consequence of Executor misidentified as Dispatcher (extra work done) is far smaller than Dispatcher misidentified as Executor (overreach issuing commands).

---

## VI. Sub-Agent Configuration Notes

### 6.1 Model Self-Report Residue

Sub-agent templates migrated from other models may cause the model to self-report an incorrect name; the actual model is determined by the `model` field configuration. Judge the real model by API call logs, not model self-description.

### 6.2 Thinking Mode Is Capability, Not Burden

The purpose of using a DeepSeek sub-agent is to leverage its code generation capability under thinking mode. Thinking mode is the sub-agent's core value; it does not need to be disabled. If the main agent doesn't need the thinking process, filter at the main agent side — do not suppress at the sub-agent side.

### 6.3 System Prompts Should Be Specific

Sub-agent prompts should contain role boundaries / construction constraints / non-crossable boundaries, aligned with the inheritance snapshot. Cannot just write "you write code."

---

## VII. Platform Capability Matrix

| Platform | Session Fork | Fork Preserves Context | Sub-Agent | Sub-Agent Independent Model | Intervention Method | Declaration Card | Applicable Version |
|---|---|---|---|---|---|---|---|
| **ZCode** | ✅ | ✅ | ✅ | ✅ | Sub-agent real-time intervention | Retained | v3.0-ZCode |
| **Codex** | ✅ | ❌ | ❌ | ❌ | Snapshot mailbox | Retained | v3.0-Generic |
| **Claude Code** | ❌ | ❌ | ✅ | ❌ (uses main model) | Snapshot mailbox | Retained | v3.0-Generic |
| **Cursor / Windsurf** | ❌ | ❌ | ❌ | ❌ | Snapshot mailbox | Retained | v3.0-Generic |
| **Trae** | ❌ | ❌ | ✅ (Task) | ❌ (50% success rate) | Snapshot mailbox | Retained | v3.0-Generic |

### Criteria

- Inheritance media positioning depends on "fork preserves context" — only ZCode satisfies this; inheritance media can be常规化 (still needs snapshot to assist sub-agents)
- Intervention method depends on "sub-agent independent model" — only ZCode supports this; real-time intervention possible; other platforms require human bridging
- **Declaration Card retained on ALL platforms** — it is within-session per-round bidirectional calibration; fork/sub-agent/snapshot all only do one-way state transfer, cannot substitute

### Two Versions

- **v3.0-ZCode**: Inheritance media常规化 + sub-agent real-time intervention + Declaration Card retained
- **v3.0-Generic**: Inheritance media pure disk snapshot fallback + snapshot mailbox human bridging + Declaration Card retained

Both versions share all other clauses. The only differences are inheritance media positioning and intervention method.

### Why Not One-Size-Fits-All

Generalizing ZCode platform-specific capability conclusions (fork preserves context + sub-agent independent model) into universal protocol would make platforms without these capabilities mistakenly believe they can omit the Declaration Card or use real-time intervention, causing protocol-layer constraints to completely fail under weak models.
