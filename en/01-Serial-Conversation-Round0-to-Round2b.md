# 01 — Serial Conversation: Round 0 to Round 2b

> Round-by-round operation guide for the first half of the project. Each round is presented across 7 fields: Input / Outputs / Key Steps / Triggers / Decision Point / Rollback Procedure / Red/Yellow/Green.
> Every round must output a Mode Declaration Card (§4.4) in its first sentence, and every round must update the Inheritance Snapshot (§4.12) at its end.

---

## General Conventions (Effective for Every Round)

- Before the round begins, the Coordinator provides an Agenda Checklist (5-8 items); you check off which items are discussed this round and which are deferred to the next round
- Only the items you checked off are frozen/flagged at the end of this round
- Each round produces Decision Records + Updated PPM + Updated Inheritance Snapshot
- You must confirm before advancing to the next round
- **§4.4 Mode Declaration Card**: In every round, the AI's first sentence outputs `[Mode] caveman={ON|OFF} | §8={ON|OFF} | timebox={N}min | Risk={LOW|MEDIUM|HIGH}`. Retained on all platforms; orthogonal and complementary to the inheritance medium
- **§4.12 Inheritance Snapshot**: At the end of every round, update `workflow_state` (current role / task phase / most recent commit / frozen decisions / pending items / next steps). Template: see Appendix H in File 04

---

## Round 0: Project Seeding

**Input**: Empty working directory.

**Outputs**: Top-level directory structure + git init + .env.example + environment rehearsal + Project Seeding Record.

**§4.1 Environment Discipline Runbook Pre-Check**:

Before project launch, the environment Runbook must be passed (see File 05-G Quick Reference). Core Three-Item Suite (Windows + async DB projects):
1. Docker Desktop running (`docker version` confirms Server endpoint reachable)
2. Python cache discipline: `python -B` disables .pyc + clear `__pycache__` after modifying .py files
3. Windows async driver: use `run_backend.py` (set SelectorEventLoopPolicy); do NOT launch directly via `uvicorn`

For non-Windows projects, adjust to actual environment, but the "solidify at launch" principle remains --- no ad-hoc debugging on the spot.

**Agenda Checklist**:

- Top-level directory discussion (backend/ frontend/ docs/ scripts/ tests/ .gitignore README.md, approximately 8 directories)
- Tech stack initialization (Python version / Node version / virtual environment / minimal dependencies)
- Version control (git init + .gitignore rules)
- Environment rehearsal (pass health check)
- Trigger track evaluation (whether in Demo Mode)

**Key Steps**:

1. Confirm top-level directory names and structure
2. git init, write .gitignore
3. Initialize Python virtual environment, install minimal dependencies (FastAPI / pytest / ruff)
4. Initialize frontend scaffolding (per actual selection)
5. Create .env.example and .env (empty)
6. Pass a health check to prove the environment is functional

Stage 0 only discusses the top-level directory; the 7-layer breakdown of `docs/` is deferred to Round 2b.

**Freeze Determination**:

- Top-level directory structure: Hard-Freeze
- .env.example format: Soft-Freeze
- Tech stack version range: Soft-Freeze

**Decision Point**: canyu confirms the top-level directory structure + determines whether it is Demo Mode.

**Rollback Procedure**: If the directory structure is unreasonable, return to Round 0 and redo.

**Red/Yellow/Green**:

- Green: Top-level directory structure confirmed + git init completed + environment rehearsal all green
- Yellow: Environment rehearsal passed but with warnings
- Red: Environment rehearsal failed

---

## Round 1a: Gather Requirements

**Input**: Client requirements / meeting minutes / emails.

**Outputs**:

- `docs/02-product/PRD.md` (skeleton: business background + target users + core scenarios + non-functional requirements + coarse acceptance criteria)
- `docs/02-product/User Stories.md` (each with AC, format: As a / I want to / So that)
- Raw materials archived to `docs/02-product/raw/`

**§4.10 Empathy Thinking Principle (换位思考)**:

During the requirements phase, empathy thinking is mandatory for the following subjects:
- Minors
- Vulnerable user groups
- Those in a served rather than serving role within the business process
- Those producing non-explicit data within the business process (emotional / psychological state / privacy behavior)

Coordinator must:
1. Proactively raise "empathy scenario" as an agenda item and add it to the Agenda Checklist
2. Identify at least 1-2 needs that "the business side did not mention but the user side inevitably has"
3. Even if not implemented in MVP, pre-reserve fields or interfaces during the PRD/DB phase
4. Explicitly ask canyu whether to include in MVP / V2 / V3

**Agenda Checklist**:

- Business background and target users
- Core scenario ranking (3-5 items)
- Non-functional requirements (performance / security / compliance)
- User story discussion one by one (each confirmed by you before finalizing)
- Whether the Acceptance Criteria (AC) for each user story are verifiable
- **Empathy Scenarios** (§4.10 mandatory): Which user groups require empathy thinking? What needs has the business side not mentioned?

**Key Steps**:

1. Collect all raw requirements (emails / meeting minutes / chat logs), archive to raw/
2. Organize structured PRD: business background, target users, core scenarios, non-functional requirements, acceptance criteria (coarse)
3. Decompose into user stories, each story must carry AC:
   ```
   As a [role]
   I want to [action]
   So that [value]
   Acceptance Criteria:
   - Given [precondition]
   - When [action]
   - Then [result]
   ```
4. Empathy thinking: for every user-facing role, inspect non-business needs and pre-reserve fields/interfaces

**Freeze Determination**:

- User story content: Soft-Freeze (attribution may be adjusted in Round 1b)
- Business background: Soft-Freeze

**Decision Point**: None (pure output; classification deferred to Round 1b).

**Rollback Procedure**: If requirements conflict, confirm with the business side, then return to revise user stories.

**Red/Yellow/Green**:

- Green: PRD + user stories complete, acceptance criteria clear and verifiable
- Yellow: PRD present but user stories incomplete
- Red: Requirements vague, acceptance criteria missing

---

## Round 1b: Requirements Classification

**Input**: PRD + user stories produced in Round 1a.

**Outputs**:

- `docs/02-product/MVP Scope Definition.md` (Must / Optional / Won't Do)
- Chain Mapping Table (each story assigned to 1 chain)
- `docs/03-agent/Acceptance Criteria.md` (one of the 6 core documents, interface-level granularity)

**AI Agent Chain Identification**:

During requirements classification, if the project includes AI Agent capabilities, the following chains must be separately labeled (do NOT follow the CRUD chain template):

| Agent Chain Type | Characteristics | Difference from CRUD Chains |
|---|---|---|
| RAG Retrieval Chain | User query → Vector retrieval → LLM generation | Requires vector DB collection planning + Embedding selection + degradation strategy |
| Agent Conversation Chain | Multi-tool context + LLM decision-making + SSE streaming | Requires memory architecture + Prompt versioning + Crisis Short-Circuit + degradation |
| Recommendation Chain | Structured reasoning + LLM generation | Requires fallback rule-based recommendation |
| Sentiment/Psychological Monitoring Chain | Keyword trigger + LLM rating | Requires safety boundaries + strictest rating + zero exposure on student side |

Once labeled, these chains must go through Agent-specific engineering nodes in Rounds 2a/2b/3/4a/4b (see subsequent Rounds for details).

**Agenda Checklist**:

- Business object extraction (which business objects, 1 per chain)
- Chain mapping (which story belongs to which chain)
- **AI Agent Chain Identification** (which chains are Agent-type and require specialized engineering nodes)
- MVP scope definition (Must / Optional / Won't Do)
- Trigger checks: more than 6 chains? Fewer than 3 stories per chain? Overlap?
- Whether acceptance criteria reach interface level (path / method / input params / output params / error codes)

**Key Steps**:

1. Classify by business object: list all business objects (customer / student / enterprise, etc.), assign each story to 1 object, each object = 1 chain
2. **Label Agent Chains**: identify non-CRUD chains such as RAG / Agent Conversation / Recommendation / Sentiment Monitoring
3. Label MVP scope: Must / Optional / Won't Do
4. Write the Chain Mapping Table, format:
   ```
   Chain 1: Customer Management (customer) [CRUD]
     Story 1.1: Registration / Story 1.2: Login / Story 1.3: Profile Edit
   Chain 5: K12 Agent Conversation (k12_agent) [Agent]
     Story 5.1: Student conversation / Story 5.2: Conversation persistence
   ```
5. Write acceptance criteria; for each story, specify "how to verify completion," covering both normal and exception paths

**Acceptance Criteria Template** (can be copied and used directly):

```markdown
# Acceptance Criteria

## Chain 1: [Chain Name]
### Story 1.1 [Story Name]
- Acceptance: [HTTP Method] [Path] returns [Status Code], [Verification Condition]
- Exception: [Exception Condition] → [Expected Status Code], [Another Exception] → [Expected Status Code]
- Test Coverage: Unit / Integration / E2E
```

**Triggers**:

| No. | Condition | Determination |
|------|------|------|
| T2.1 | Number of chains exceeds 6 | Warning: too many; consider merging |
| T2.2 | A chain has fewer than 3 stories | Warning: too small; consider merging into another chain |
| T2.3 | Acceptance criteria missing or too abstract (only "done" without "how to verify") | Flag Red |
| T2.4 | Chains overlap (same story assigned to 2 chains) | Flag Red |
| T2.5 | Agent chain type not labeled (RAG/Agent/Recommendation/Sentiment) | Flag Red |

**Freeze Determination**:

- Number of chains: Hard-Freeze (adding a new chain requires audit)
- MVP scope definition: Hard-Freeze
- Acceptance criteria: Soft-Freeze (granularity may be deepened later, but must not be reduced)

**Decision Point**: canyu decides "Are the chain classification + MVP scope correct?"

**Rollback Procedure**: If chains overlap, return to Round 1a to reclassify; if MVP is vague, canyu makes the call.

**Red/Yellow/Green**:

- Green: Reasonable number of chains (2-6), MVP clear, acceptance criteria verifiable, Agent chains labeled
- Yellow: Too many or too few chains, acceptance criteria vague
- Red: MVP vague, chains overlap, acceptance criteria missing, Agent chains not labeled

---

## Round 2a: Implementation Decomposition + Tech Stack

**Input**: Chain Mapping Table + Acceptance Criteria + Agent chain labels.

**Outputs**:

- `docs/03-agent/Task Decomposition Specification.md` (second of the 6 core documents)
- `docs/03-agent/ChainN-todo.md` (1 per chain, labeling Organs + test points + cross-chain dependencies)
- `docs/04-technical/Tech Selection.md` (including alternatives + risks + version pinning)

**§4.17 Prompt Versioning Rules**:

If the project includes AI Agent chains, the tech selection must confirm the following AI Agent tech stack:

| Item | Requirement |
|---|---|
| LLM Framework | Version pinned (e.g. LangChain 1.0); confirm create_agent / astream_events API availability |
| LLM Provider | Version pinned + switchable (e.g. DeepSeek / Ollama / OpenAI) |
| Embedding | Version pinned + dimension confirmed (e.g. bge-m3 1024-dim) |
| Vector DB | Version pinned + collection planning (e.g. Milvus 2.6) |
| Prompt Versioning | All prompts written in `ai/chains/*` files, git-tracked; PROMPT_VERSION required |
| SSE | Confirm astream_events / EventSourceResponse compatibility |

**Agenda Checklist**:

- Tech selection (backend / frontend / database / AI / cache / deployment)
- **AI Agent tech stack confirmation** (§4.17: LLM Framework / Provider / Embedding / Vector DB / Prompt Versioning / SSE)
- Version pinning (write to requirements.txt / package.json; "latest" forbidden)
- Task decomposition specification established (granularity criteria: no more than 1 file / no more than 200 lines / no more than 30 minutes)
- Each chain decomposed into Organs (API / Service / Model / Schema / Test / E2E)
- Cross-chain dependency labeling
- Trigger checks: at least 8 Organs? Test points complete? Dependencies labeled?

**Key Tech Selection Requirements**:

Each selection must fill 3 items: Why chosen (1-2 sentences), Alternative (what to switch to if the choice is wrong), Risk (known pitfalls / version compatibility / upgrade cost). Versions written into requirements.txt / package.json; "latest" forbidden.

**Task Decomposition Specification Template**:

```markdown
# Task Decomposition Specification

## Task Granularity Criteria
- One task changes no more than 1 file (large files excepted)
- One task does not exceed 200 lines of code
- One task does not exceed 30 minutes to complete
- One task = one commit-able unit

## Task Template
- Task ID: chainN-task-001
- Input (Dependencies): Phase skeleton
- Output (File + Content): Corresponding code file path
- Test Points: Unit / Integration / E2E
- Definition of Done: pytest pass + interface design updated

## Prohibitions
- Do not cross multiple chains
- Do not modify unrelated code
- Do not "opportunistically" optimize
- Do not mock critical paths
```

**Chain Todo Format** (every chain must include):

```markdown
# Chain N Todo — [Chain Name] [CRUD / Agent]

## Organ Inventory
| Organ | Type | File Path | Test Points | Dependencies |
|------|------|---------|--------|------|
| Registration API | API POST | api/v1/customer.py | Unit + Integration | — |
| Registration Service | Service | services/customer_svc.py | Unit | — |
| ... | ... | ... | ... | ... |

## Cross-Chain Dependencies
- Chain 3 calls Chain 1: POST /api/v1/customers → pass-through JWT token
```

Agent chain todos additionally label Agent-specific Organs (Memory Layer / RAG Tools / Prompt / Degradation / Crisis Short-Circuit).

**Triggers**:

| No. | Condition | Determination |
|------|------|------|
| T3.1 | Each chain has no fewer than 8 Organs | Pass if decomposition is reasonable |
| T3.2 | Any Organ lacks test points | Flag Red |
| T3.3 | Task decomposition specification lacks "Task Granularity Criteria" | Flag Red |
| T3.4 | Cross-chain dependencies not labeled | Flag Red |
| T3.5 | Chain todo missing or too few Organs (fewer than 5) | Flag Red |
| T3.6 | Agent chain todo lacks Agent-specific Organ labels | Flag Red |
| T4.1 | Using "latest version" without pinning | Flag Red |
| T4.2 | No "Alternative" or "Risk" | Flag Yellow |
| T4.3 | Version number missing | Flag Red |
| T4.4 | Version incompatibility between different selections | Flag Red |
| T4.5 | Agent chain present but LLM Framework / Embedding / Vector DB versions not confirmed | Flag Red |

**Freeze Determination**:

- Tech stack + versions: Hard-Freeze
- Task decomposition specification: Soft-Freeze (standards may be added, not removed)
- Chain todo Organs: Soft-Freeze (may be appended during coding)

**Decision Point**: canyu decides "Is the tech selection correct?"

**Rollback Procedure**: If the selected stack cannot run, troubleshoot versions; do not casually switch the tech stack.

**Red/Yellow/Green**:

- Green: Every chain has complete Organs + complete test points + clear dependencies + task decomposition spec has granularity criteria + Agent tech stack confirmed
- Yellow: Organs complete but test points incomplete
- Red: Chain missing Organs / dependencies chaotic / task decomposition spec missing / Agent tech stack not confirmed

---

## Round 2b: Directory Structure

**Input**: Tech selection + Chain todos + Business object inventory + Agent chain labels.

**Outputs**:

- `docs/04-technical/System Architecture Design.md`
- Complete directory tree (including `docs/04-technical/_chains/` chain isolation zone + frontend single-source View directory + Agent tool layer directory)
- **Contract Freeze document** (§4.13)
- Premium upgrade assessment (Coordinator proactively asks at the end of this round)

**§4.13 Contract Freeze**:

After the directory structure is determined and before Round 3 specification formulation begins, the frontend-backend contract must be frozen:

| Contract Item | Content | Freeze Level |
|---|---|---|
| Interface Schema | Every interface of every chain includes path/method/input params/output params/error codes | Hard-Freeze |
| Enum Values | Complete set of values for all enums (roles/statuses/types, etc.) | Hard-Freeze |
| SSE Event Protocol | Event names (conversation_created / token / meta / done / error) + fields | Hard-Freeze |
| Frontend-Backend Field Mapping | Fields needed by frontend vs. fields returned by backend, no omissions | Hard-Freeze |

The contract document precedes code; it is not patched after a crash. Item 8 of the Launch Gate checks "Contract Frozen."

**Frontend Directory Planning**:

If the project includes a frontend, the directory structure must follow the single-source View template (see File 08 §C):

```
frontend/app/
  _shared/
    views/           # Business component single source of truth (StudentView / ParentView / ...)
    role-context.tsx # Role-state sharing
  student/page.tsx   # Thin shell: return <StudentView />
  parent/page.tsx    # Thin shell
  dev/page.tsx       # Aggregated testing entry (DEV ONLY, removed in production)
```

**Agent Tool Layer Directory**:

If the project includes AI Agent chains, the backend directory must contain the Agent tool layer:

```
backend/app/ai/
  agents/            # Agent orchestration (supervisor / context / response_format)
  agents/tools/      # Agent tools (one file per @tool)
  agents/guards/     # Safety guards (keyword fallback / Crisis Short-Circuit)
  chains/            # LLM chains (one file per chain, Prompt versioning)
  llm_factory.py     # LLM factory
  embeddings.py      # Embedding
  vectorstore.py     # Vector store
  reranker.py        # Re-ranker (optional)
```

**Agenda Checklist**:

- System architecture design (inter-module relationships / data flow / deployment approach)
- Backend directory tree (files organized by business object; chainN_*.py forbidden)
- **Agent tool layer directory** (ai/agents/ / ai/chains/ / ai/guards/)
- **Frontend directory planning** (_shared/views single-source View + dev aggregation entry)
- **Contract Freeze** (§4.13: interface schema / enums / SSE events / frontend-backend field mapping)
- `_chains/` isolation zone structure (1 subdirectory per chain)
- Upgrade assessment: sliding toward Premium? (Coordinator proactively asks)
- Trigger checks: organized by technical layer? 7 layers missing? _chains/ missing a chain? Contract not frozen?

**Key Directory Constraints**:

```
docs/ strictly uses 7-layer structure: 01-business/ 02-product/ 03-agent/
  04-technical/ 05-ai-coding/ 06-project/ 07-testing/

docs/04-technical/_chains/  1 subdirectory per chain, chain Agent workspace
backend/app/
  core/        Shared modules, written by Coordinator, chain Agents forbidden to modify
  api/v1/      Organized by business object: customer.py / student.py / ai_chat.py / mental.py
  models/      By chain: customer.py / student.py / ...
  schemas/     By chain
  services/    By chain
  ai/          Agent tool layer (agents/ chains/ guards/ llm_factory.py ...)
  tests/       By chain: test_chain1_customer.py / test_chain2_student.py / ...
```

**Strictly Forbidden**: files named chain_routes.py or chainN_*.py under backend/api/v1/ (files named by chain number).

**_chains/ Design Principles**:

- Only cut into the 04-technical layer (only the technical-layer chain Agents will actually write)
- Backend code directory is not redundant; use git branch isolation + organize files by business object
- During phase integration, the Coordinator merges chain drafts into the main directory; `_chains/` is retained as chain archive
- Underscore prefix = internal directory; tools/AI skip scanning

**Triggers**:

| No. | Condition | Determination |
|------|------|------|
| T5.1 | controllers/ views/ models/ appear under backend/app/ organized by technical layer | Fix |
| T5.2 | docs/ lacks the 7-layer directory structure | Fix |
| T5.3 | docs/04-technical/_chains/ not created or missing a chain subdirectory | Block |
| T5.4 | _chains/ chain Agents not told "write here first" before parallel work | Must-run |
| T5.5 | chain_routes.py or chainN_*.py appears under backend/api/v1/ | Flag Red |
| T5.6 | Agent chains present but ai/agents/ directory not created | Flag Red |
| T5.7 | Frontend present but _shared/views/ single-source View directory not created | Flag Red |
| T5.8 | Contract Freeze document missing (interface schema / enums / SSE events / field mapping) | Block |

**Freeze Determination**:

- Directory structure: Hard-Freeze (changing it means 4x rework)
- System architecture design: Hard-Freeze
- Contract Freeze document: Hard-Freeze

**Decision Point**: None (naturally derived from tech selection), but if upgrading to Premium, canyu decides.

**Rollback Procedure**: If the directory structure is unreasonable, redesign; do not write code on a wrong structure. Contract changes require returning to Round 2b for re-freezing.

**Red/Yellow/Green**:

- Green: Business objects clearly layered + docs 7-layer structure complete + _chains/ chain count equals todo count + Agent directories complete + frontend single-source View complete + Contract Freeze completed
- Yellow: Partially by business object, partially by technical layer; contract partially frozen
- Red: Completely organized by technical layer / docs directory chaotic / _chains/ missing / contract not frozen

---

> Round 0-2b complete. Before entering Round 3, ensure all triggers have been checked and passed, the contract is frozen, and the Inheritance Snapshot has been updated. Continue reading File 02 — Serial Conversation: Round 3 to Round 5 and Launch Gate.
