# 08 — Frontend & Async Division of Labor

> Frontend completion definition, perspective convergence, single-source View template, async division protocol, executor-first pattern.

---

## I. Frontend Completion Definition (§4.5)

### 1.1 Core Principle

**Frontend = interaction layer, not presentation layer.** "Demo-able ≠ interactive." Any page that cannot be clicked / typed into / trigger a request / show result feedback is not considered a qualified frontend.

### 1.2 Completion Definition

Centered on project requirements, entered through role perspective, covering 80–90% of backend capability, with low design complexity.

### 1.3 Three Mandatory Questions Per UI Element

- Who uses this? (role / perspective)
- What can they do with it? (action / business outcome)
- What do they see after doing it? (feedback / state / subsequent path)

Any question unanswerable → delete, merge, or demote to backend script.

### 1.4 Anti-Patterns

- Placing a "Generate Plan for Student" button directly in `/admin` while `/student` has no such entry
- Using one `FeatureGrid` for all roles simultaneously, with copy text driven by if-conditions
- Demo director's cut being only a text timeline, pointing to no real interface or real interaction
- Treating "clickable but does nothing when clicked" buttons as frontend capability
- Leaving test-use "debug entries" on production paths during convergence phase

---

## II. Perspective Convergence

### 2.1 Testing Phase: Centralized Admin Dumping Ground

Before features are complete and perspective splits are frozen, allow using `/dev` (or a dedicated internal dev page) as a "universal entry" to dump all new features.

Allowed:
- Seeing feature entries for any role
- Calling any role's APIs (backend permission checks still required)
- Displaying raw data / debug info

But MUST explicitly mark as `TEST ENTRY / DEV ONLY / REMOVE BEFORE PROD`.

### 2.2 Convergence Phase: Split Interfaces by Perspective

When any of the following triggers, enter UI convergence phase:
- User explicitly says "prepare for demo / launch / interview"
- Entering Round 7 / Round 8 or the corresponding UI convergence round
- After browser-level demo acceptance

Convergence phase MUST execute:

1. Against the role matrix, list every feature currently in the admin interface, annotating the true owning role
2. Migrate or replicate each feature to the corresponding role page:
   - Student features → `/student/*`
   - Parent features → `/parent/*`
   - Teacher features → `/teacher/*`
   - Admin features → `/admin/*` keep only ops / permissions / policy maintenance
   - Visitor features → public pages `/`, `/policies`, `/policies/[id]`
3. Admin interface keeps only capabilities genuinely needed by the admin role
4. When one feature is needed by multiple roles, MUST render differently per perspective
5. After splitting is complete, MUST do one real browser walkthrough — every role completes at least 1 real interaction (click → API → feedback)

---

## III. Single-Source View Template

### 3.1 Three Iron Laws

1. **True source single-write**: Business components exist only in `app/_shared/views/*` — one copy. Route `page.tsx` files are thin shells, only `return <XxxView />`. Any business change goes to `_shared/views/*`; no business logic in route `page.tsx`.
2. **Role-state sharing**: Use a lightweight `RoleContext` holding current role and shared token; do NOT write `localStorage`. During testing, `/dev`'s `RoleSwitcher` overrides the Context; in production, real login state takes over.
3. **Production takedown**: Three-layer removal of test entries via env switch + middleware + main nav conditional rendering. When the production build has the switch off, `/dev/**` returns 404 directly.

All three iron laws must be satisfied simultaneously; missing any one degrades into common anti-patterns.

### 3.2 Directory Structure Template

```
frontend/
  app/
    _shared/
      role-context.tsx           # RoleProvider / useRole / isDevConsoleEnabled / APP_ROLES
      DevConsoleNavLink.tsx      # Main nav conditional dev entry; returns null when env=0
      views/
        StudentView.tsx          # Student true-source View
        ParentView.tsx           # Parent true-source View
        TeacherView.tsx          # Teacher true-source View
        AdminView.tsx            # Admin true-source View
    student/page.tsx             # Thin shell: return <StudentView />
    parent/page.tsx              # Thin shell
    teacher/page.tsx             # Thin shell
    admin/page.tsx               # Thin shell
    dev/page.tsx                 # /dev aggregation entry: only imports _shared/views/*, no second copy of business logic
    layout.tsx                   # Wraps RoleProvider + DevConsoleNavLink
  middleware.ts                  # matcher: /dev, /dev/:path*; when env=0 rewrite -> /not-found
.env.example                     # Explicitly declares NEXT_PUBLIC_ENABLE_DEV_CONSOLE
```

Key points:
- `app/_shared/` starts with underscore,不会被 Next App Router 暴露为路由
- Route thin-shell `page.tsx` MUST NOT contain any business logic, `useState`, `useEffect`, or API calls
- `dev/page.tsx` is only allowed to do three things: render top dev banner, maintain `RoleSwitcher`, render the corresponding View per current role

### 3.3 Adoption Conditions

Adopt when any of the following is true:
- Project has ≥3 fixed roles, each with independent interactive pages
- Demo phase needs quick role switching from one entry point
- Pre-launch must forcibly remove test entries to avoid polluting production paths

If only one role or a marketing-only page, the template would induce over-abstraction and may be skipped.

### 3.4 Acceptance Checklist

After implementation, MUST manually pass these 6 steps in browser:

1. Create `frontend/.env.local`, write `NEXT_PUBLIC_ENABLE_DEV_CONSOLE=1`
2. Start frontend → top nav shows prominent `DEV` button
3. Visit `/dev` → top red banner, `RoleSwitcher`, token input all visible
4. Switch to student → paste demo token → load student data → generate plan, confirm real API closed loop
5. Switch parent / teacher / admin, confirm rendering corresponding true-source View, no second business implementation
6. Turn off env, restart frontend → `/dev` returns 404, main nav `DEV` button not rendered

Any item not passed → template implementation not considered complete.

---

## IV. Async Division Protocol (§4.3)

### 4.1 Division Boundary

When the main dispatcher and executor (weak model) are separated:

- **Dispatcher**: Only does initial acceptance / final acceptance / bug triage
- **Executor**: Construction + intermediate verification
- Intermediate verification is pushed down to executor; dispatcher does not re-run full acceptance, only spot-checks

### 4.2 Cost Discipline

After the low-cost model completes work, the high-cost dispatcher does NOT re-run full acceptance, only spot-checks. Otherwise the division design fails.

### 4.3 Milestone Granularity

- Single M/F work-hour recommendation: 2–4h executor construction
- Single M/F must be independently verifiable (AC ≥ 3 items)
- Cross-chain changes > 2 modules → split into multiple milestones
- Involving mandatory confirmation items → dispatcher MUST confirm with user before launch; executor does not proactively touch

### 4.4 Mandatory Confirmation Items (§4.4)

The following changes MUST be confirmed by the dispatcher with the user before launch; executor does not proactively touch:

- Database schema changes
- RBAC permission matrix seed data modifications
- Mental health record access permission changes (involving minor protection)
- Education policy data source changes
- Whitelist / Redlist entry manual additions/removals

---

## V. Executor-First

### 5.1 Pattern

The executor can complete construction before dispatcher intervention; dispatcher only does final acceptance. Saves entry-card writing + context transfer package + Declaration Card.

```
1. Any model接手, reads inheritance snapshot
2. Determines self as executor (construction_done=No)
3. Constructs directly (no need to wait for entry card)
4. After completion, updates snapshot: construction_done=Yes + commit hash + acceptance evidence
5. Dispatcher reads snapshot
6. Determines self as dispatcher (construction_done=Yes, dispatcher_intervened=No)
7. Does final acceptance (acceptance only, no re-running construction)
8. Acceptance passed → update snapshot → next task
```

### 5.2 Prerequisites

The inheritance snapshot must contain enough information for the executor to know "what to do, how to do it, where the boundaries are." This requires the snapshot to be more structured than a traditional entry card.

### 5.3 Platform Limitations

- **ZCode**: Fork preserves context + sub-agent independent model → executor-first + sub-agent real-time intervention (optimal)
- **Other platforms**: No fork context preservation → executor relies on inheritance snapshot for context recovery, intervention relies on snapshot mailbox human bridging

See File 07 for details.
