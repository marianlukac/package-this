<!--
SYNC IMPACT REPORT
==================
Version change: (none) → 1.0.0 (initial ratification)
Modified principles: N/A — initial creation from template
Added sections:
  - Purpose (project context and scope statement)
  - Core Principles (13 principles, expanded from 5-slot template)
  - Engineering Constraints (explicit checkable rules derived from principles)
  - Governance (amendment procedure, versioning policy, compliance review)
Templates checked:
  ✅ .specify/templates/plan-template.md
     Constitution Check section present; gates will be derived from this constitution.
     No structural changes required.
  ✅ .specify/templates/spec-template.md
     Functional-only by design; aligns with Principle III.
     No changes required.
  ✅ .specify/templates/tasks-template.md
     Audit, security, and test task categories already present in template phases.
     Aligns with Principles V, VIII, and XI.
     No changes required.
  ✅ .specify/templates/constitution-template.md
     Source template — not modified (operating on memory/constitution.md).
Deferred TODOs: None — all placeholders resolved.
-->

# Dunder Mifflin Package Manager Constitution

## Purpose

This constitution defines the non-negotiable principles governing the Dunder Mifflin Package
Manager project. It applies to every specification, plan, implementation decision, and
contribution made to this codebase.

This project is the official trainer baseline for a full-day Agentic AI workshop. Attendees
will use this application as the foundation for building agents, memory, tools, MCP
integrations, and agent-to-agent scenarios. The constitution therefore prioritizes clarity,
stability, and enterprise-pattern fidelity above all else.

This document does NOT describe specific features, user stories, UI screens, APIs, database
schemas, cloud resources, frameworks, libraries, or implementation details. Those concerns
belong in functional specifications and technical plans respectively.

## Core Principles

### I. Workshop-First Clarity

The codebase, documentation, structure, naming, and runtime behavior MUST be understandable
for workshop attendees with mixed experience levels.

**Rules:**
- Prefer readable, explicit, and beginner-friendly implementations over clever abstractions.
- Every module, function, and variable name MUST communicate intent without requiring context
  outside the immediate scope.
- Avoid premature generalization. Three similar concrete implementations are better than one
  abstract pattern an attendee must decode under workshop time pressure.
- Documentation MUST explain WHY decisions were made, not only WHAT the code does.
- Error messages MUST be human-readable and actionable.

**Rationale:** Attendees encounter this codebase for the first time during the workshop.
Anything opaque becomes a distraction from the learning goal. Clarity is the primary feature.

---

### II. Enterprise-Translatable Design

Every important design choice MUST map to a recognizable enterprise concern.

**Rules:**
- Design decisions MUST be traceable to enterprise patterns: traceability, auditability,
  operational visibility, reliable integrations, event-driven communication, API consumption,
  or controlled state changes.
- Non-trivial patterns MUST have a stated enterprise rationale — not aesthetic justification.
- Documentation and comments MUST name the enterprise concept that each design choice
  represents so attendees can connect theme to reality.

**Rationale:** The Dunder Mifflin theme is memorable, but attendees must leave with knowledge
they can apply to real enterprise systems. Every design decision is a teaching opportunity.
If the enterprise mapping is invisible, the lesson is lost.

---

### III. Separation of Functional Specification and Technical Implementation

Functional specifications MUST describe what the system does and why it matters. Technical
plans MUST describe how it is implemented. These concerns MUST NOT be mixed.

**Rules:**
- A functional specification MUST NOT reference frameworks, infrastructure, databases,
  messaging systems, cloud services, or deployment decisions.
- A technical plan MUST reference the functional specification it implements and MUST justify
  each technology choice against a functional requirement.
- The `spec.md` and `plan.md` workflow artifacts represent this boundary explicitly.
  They MUST NOT be collapsed into a single document.
- Reviewers MUST reject specifications containing implementation details and MUST reject
  plans that do not cite a functional specification.

**Rationale:** Mixing concerns produces specifications hostage to technology choices and plans
lacking business grounding. The separation makes both documents more durable, more testable,
and reusable across technology generations — a critical enterprise documentation discipline.

---

### IV. API-First and Agent-Ready Behavior

The system MUST expose stable, predictable, and well-documented business capabilities that
agents and MCP servers can consume without relying on UI behavior or undocumented side effects.

**Rules:**
- Every meaningful business operation MUST be accessible through the system's API.
- API contracts MUST be defined before UI is built for any given capability.
- API endpoints MUST behave identically whether called by a human-facing UI, an automated
  agent, or a test harness.
- Undocumented side effects MUST NOT be a required path to correct system behavior.
- Breaking API changes MUST be treated as first-class architectural decisions requiring
  deliberate versioning or a documented migration path.

**Rationale:** Agents cannot see the UI. If a business capability is only reachable through
the UI, it is invisible to agents. Agent-readiness is not a post-launch concern; it is a
design constraint from the first line of code.

---

### V. Auditability by Default

Every meaningful business change MUST produce an immutable audit record.

**Rules:**
- An audit record MUST capture: actor, timestamp, event type, source system, affected entity
  identifier, previous value (where applicable), new value (where applicable), and reason
  (where applicable).
- Audit records MUST be immutable once written. They MUST NOT be editable or deletable
  through normal system operations.
- The absence of an audit record for a meaningful business event is a defect, not a feature
  gap.
- Audit records MUST be queryable by actor, entity, time range, and event type at minimum.

**Rationale:** Enterprise systems are accountable systems. "Who changed this, when, and why?"
is not a convenience — it is a compliance, debugging, and operational necessity. Audit logs
are also structured and queryable, making them an ideal target for AI agents during the
workshop.

---

### VI. Controlled State Changes

Business state transitions MUST be explicit, validated, deterministic, and testable.

**Rules:**
- The valid states of every business entity and the allowed transitions between them MUST be
  defined and enforced at the business logic layer, not only in the UI.
- An invalid state transition MUST be rejected with a clear, descriptive error identifying
  the current state, the attempted transition, and why it is not permitted.
- Unauthorized state changes MUST be rejected server-side, not merely hidden in the UI.
- State machine definitions MUST be independently readable and testable without instantiating
  a full application runtime.

**Rationale:** Package lifecycle management is the core domain of this application. If any
actor — human or agent — can place a package into an invalid state, the system is unreliable.
Explicit state machines are also a transferable enterprise workflow design pattern.

---

### VII. Event-Driven Where It Matters

Important domain events MUST be emitted when other parts of the system need to react.
Events MUST NOT be published for every trivial internal change.

**Rules:**
- An event MUST be emitted when a business state change has consequences outside the
  immediate transaction boundary (e.g., another service, an agent, a notification consumer).
- Events MUST carry enough context for a consumer to act without querying the source system.
- Audit records and domain events are related but MUST NOT be conflated. An audit record
  documents what happened for accountability. An event signals what happened for reaction.
- The set of publishable events MUST be explicitly documented. Undocumented events MUST NOT
  be relied upon by agents or other consumers.

**Rationale:** Event-driven communication is a foundational enterprise integration pattern.
Workshop agents will subscribe to and react to these events. Choosing deliberately which
events matter prevents event flood and keeps the system comprehensible and teachable.

---

### VIII. Secure by Default

The system MUST apply security controls as the default state, not as an afterthought.

**Rules:**
- Secrets (API keys, passwords, tokens, connection strings) MUST NEVER be committed to
  version control under any circumstances.
- All configuration that varies by environment MUST be externalized.
- All write operations MUST validate and sanitize input at the business logic layer,
  regardless of any client-side validation present.
- Persona-based permissions MUST be enforced server-side. UI-only permission enforcement
  is insufficient and MUST be treated as a security defect.
- The system MUST fail closed: an ambiguous authorization decision MUST deny, not permit.

**Rationale:** Security mistakes in a workshop baseline propagate to every attendee's project.
A workshop that teaches insecure patterns causes harm at scale. This principle also maps
directly to OWASP Top 10 concerns, making the codebase a teachable enterprise security
reference.

---

### IX. Accessible and Usable UI

The UI MUST be visually polished, responsive, and accessible to users with diverse needs and
abilities.

**Rules:**
- The UI MUST support keyboard navigation throughout all primary workflows.
- Color contrast MUST meet WCAG AA minimums at minimum.
- Every interactive element MUST have a clear, descriptive label.
- Every list or collection view MUST have a purposeful empty state (not a blank screen).
- Error messages MUST explain what went wrong and what the user can do next.
- The UI MUST be functional and readable on both desktop and tablet viewport sizes.

**Rationale:** Workshop attendees will demo this system. A polished, accessible UI signals
professional quality and avoids distracting participants from Agentic AI learning goals.
Accessibility is a non-negotiable enterprise standard — not an optional enhancement added
after everything else works.

---

### X. Demo Reliability

The system MUST support resettable seed data and predictable demo scenarios.

**Rules:**
- A documented, single-command (or near-single-command) process MUST exist to restore the
  system to its baseline demo state.
- Seed data MUST represent realistic business scenarios: multiple actors, multiple package
  states, representative audit histories, and meaningful event sequences.
- Demo scenarios MUST be documented so trainers can execute them consistently across
  workshop cohorts.
- The baseline seed state MUST be version-controlled alongside the application code.

**Rationale:** A workshop that breaks during the demonstration destroys confidence and wastes
attendee time. Demo reliability is an operational requirement, not a convenience. Trainers
must be able to reset and run the baseline on any workshop day without diagnosing state.

---

### XI. Test the Core

Core business rules, lifecycle validation, permission checks, event creation, audit logging,
and API behavior MUST be covered by automated tests.

**Rules:**
- Business logic MUST be testable without a running UI, without a live database connection,
  and without external service dependencies where possible.
- State machine transitions MUST have tests covering both valid and invalid transition
  attempts.
- Permission enforcement MUST have tests covering both authorized and unauthorized actors.
- Audit record creation MUST be verified by tests, not assumed.
- API contracts MUST have tests verifying both structure and behavior.

**Rationale:** The workshop is a live, high-pressure environment. Regressions that surface
during a workshop are costly and avoidable. A tested core also demonstrates to attendees that
enterprise-grade systems are maintained through automated verification, not heroic manual
checking.

---

### XII. No Hidden Workshop Dependencies

The project MUST be runnable with clear setup instructions. Every external dependency MUST be
documented, configurable, and have a stated local or shared-resource strategy.

**Rules:**
- The README MUST contain step-by-step setup instructions sufficient to bring the system up
  from a clean machine.
- Every external service dependency MUST be documented with: its purpose, its configuration
  method, and the local alternative (mock, emulator, or shared resource).
- Setup instructions MUST be validated before each workshop cohort.
- A dependency that is undocumented but required is a defect, not a known limitation.

**Rationale:** Workshop attendees arrive with varying machine configurations. An undocumented
dependency that breaks setup for one attendee costs the entire cohort time and momentum.
Runnable-from-scratch is a first-class quality criterion for this project.

---

### XIII. Theme Supports Learning

The Dunder Mifflin theme MUST make the workshop memorable and accessible. It MUST NOT obscure
the business domain, technical learning goals, or enterprise patterns.

**Rules:**
- Every themed entity (package, branch office, employee persona) MUST have a clear mapping
  to the real enterprise concept it represents.
- Documentation MUST name the enterprise concept alongside the themed name wherever the
  mapping is not immediately obvious.
- Humor and theme MUST be present in names, seed data, and documentation tone — but MUST NOT
  appear in error handling logic, security enforcement, state machine rules, or audit records.
- If the theme ever conflicts with comprehension, comprehension wins unconditionally.

**Rationale:** Memorable workshops produce better recall and higher attendee satisfaction.
The Dunder Mifflin theme serves this goal. But a workshop where attendees cannot connect the
theme to real enterprise concepts fails its primary educational objective.

---

## Engineering Constraints

These constraints apply uniformly across all specifications, plans, and implementations.
They are derived from the Core Principles but stated here as explicit, independently
checkable rules.

| Constraint | Classification | Source Principle |
|---|---|---|
| Secrets committed to version control | PROHIBITED | VIII |
| UI-only permission enforcement | PROHIBITED | VIII |
| Undocumented breaking API changes | PROHIBITED | IV |
| Business state transitions without validation | PROHIBITED | VI |
| Meaningful business events without audit records | PROHIBITED | V |
| Clever abstractions without measurable readability benefit | PROHIBITED | I |
| Functional specifications naming frameworks or infrastructure | PROHIBITED | III |
| Technical plans without a referenced functional specification | PROHIBITED | III |
| External service dependencies without local alternative documentation | PROHIBITED | XII |

## Governance

### Authority

This constitution supersedes all other project documentation, conventions, and preferences.
When any specification, plan, or implementation decision conflicts with this constitution,
the constitution prevails. Conflicts MUST be explicitly resolved — not quietly ignored or
silently overridden.

### Amendment Procedure

1. Any contributor may propose an amendment by opening a pull request modifying this file.
2. The proposed amendment MUST include: the principle being modified, the specific change,
   the rationale for the change, and an assessment of downstream impact on existing
   specifications, plans, and implementations.
3. Amendments require review and explicit approval from the project maintainer.
4. The constitution version MUST be incremented according to the semantic versioning policy.
5. The `Last Amended` date MUST be updated to the date of the amendment merge.
6. Downstream artifacts (specs, plans, tasks) affected by the amendment MUST be updated
   or explicitly flagged as requiring update before the amendment PR is closed.

### Semantic Versioning Policy

- **MAJOR**: A principle is removed, renamed with changed meaning, or redefined in a
  backward-incompatible way. Existing compliant specifications may become non-compliant.
- **MINOR**: A new principle or section is added, or existing guidance is materially
  expanded. Existing compliant specifications remain compliant.
- **PATCH**: Wording clarifications, typo fixes, or non-semantic refinements that do not
  change what is required.

### Compliance Review

- Every pull request MUST include a Constitution Check confirming the change is consistent
  with all applicable principles.
- Any deliberate deviation from a principle MUST be documented in the `Complexity Tracking`
  section of the relevant plan, with a justification and a record of simpler alternatives
  that were considered and rejected.
- A review of this constitution SHOULD occur before each new workshop cohort to validate
  that principles remain current and that known violations are tracked and addressed.

### Specification and Plan Alignment

- A functional specification (`spec.md`) MUST NOT be approved if it violates Principle III
  by containing implementation details.
- A technical plan (`plan.md`) MUST NOT be approved if its Constitution Check section
  contains unresolved violations.
- A task list (`tasks.md`) MUST include tasks for audit logging, permission enforcement,
  and automated testing wherever Principles V, VI, and XI apply to the feature being
  implemented.

**Version**: 1.0.0 | **Ratified**: 2026-06-19 | **Last Amended**: 2026-06-19
