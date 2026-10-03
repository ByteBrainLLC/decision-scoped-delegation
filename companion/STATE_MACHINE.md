# Proposed normative model and implemented subset

“MUST” below describes conformance to this proposed research model, not a
recognized standard or a claim that the surrounding organization is compliant.

## Immutable grant and mutable state

`identity` pins grant/version, workflow, actor, parent, policy, and configuration.
`principal`, `issuer`, and `sponsor` are separate roles. `decision_scope` is one
class/rung contract. `intent` records Outcome, Context, Constraints, Tolerances,
and The line. `pinned_predicates` records a versioned executable restriction and
separate human alignment attestation. `permitted_effects` names business effects,
not merely available tool methods. `exposure` names per-effect limits and shared
ledgers with explicit scope and epoch. `approvals`, `review_contract`, `recovery`,
`lifecycle`, and `derivation` add obligations and accepted templates.

Mutable `q` includes current role standing; accepted sponsorship/coverage and
powers; grant state and revocation fence; current policy/configuration versions;
approval claims; reservations and committed ledger exposure; review due times,
selected cases, and aggregate review evidence; audit records and effect outcomes.
Historical installed grants do not become writable lifecycle records.

## Seven admission conditions

1. **R1 Current authority:** applicable actor and entire ancestor chain are active,
   within their validity windows, integrity/version pinned, with valid issuer and
   accepted sponsorship. Descendant identity and sponsor satisfy ancestor templates
2. **R2 Expressed scope:** decision class, purpose, operation, resolved resource,
   recipient, data class, environment, and every pinned predicate are satisfied;
   recorded mismatch or uncertain required predicates cannot authorize commitment
3. **R3 Retained human decisions:** governing effects remain human; proposals do
   not change bounds; Rung 4 must retain its reversibility condition
4. **R4 Bound approvals:** every required human decision is current, authenticated
   by the trusted input model, authorized, target/payload/chain-policy bound,
   unexpired, and available to be claimed by this effect identifier only
5. **R5 Shared exposure:** nonnegative per-effect and all ancestor ledger limits
   remain satisfied under an all-or-nothing reservation; descendants share exposure
6. **R6 Evidence and review:** a pre-effect record is available; the explicit review
   arrangement is current, has an eligible reviewer, and has not missed its deadline
7. **R7 Recovery and cessation:** stop/recovery capability, current assurance
   attestation, practical sponsor powers, and accepted reversibility are present

A false mandatory restriction denies. Missing evidence or a pending human decision
holds and escalates. Both outcomes commit **zero** new effects. “Allow” at admission
is a reservation and recorded intent, not perpetual permission to execute.

## Fixed sequence

Inside one process-local lock: validate descriptor → resolve lineage → check
R1–R7 → claim required approval → reserve each applicable ledger once → record
intent → return admission. These Python assignments are one serialized modeled
transition, not a crash-safe durable transaction. At the simulated commit point,
recheck every mutable condition and fence against the reservation; then settle
reserved to committed exposure once and record the simulated outcome. A repeated
identifier with different content fails; an exact retry of a committed effect
returns its existing receipt without new execution.

## State transitions

- Proposed grant → active: trusted human issuance (initialization input only)
- Active → suspended: loss of sponsorship/practical power or review lapse
- Active → revoked: trusted revocation event advances its fence
- Suspended → active: explicit trusted human resume; subsequent effect checks still
  enforce repaired sponsorship, review, scope, and expiry
- Active grant at expiry → operationally unusable (stored state is not rewritten)
- No machine proposal → authority expansion; changed governance requires a fresh
  authorized immutable record through an issuance service outside this prototype

Effects have `admitted`, `committed`, `failed`, `canceled`, or `unknown` states.
Denied/held requests appear in attempts/results and need not create an effect-state
record. `unknown` retains reservation and approval claim; trusted confirmation of
noncommitment changes it to `failed` and releases only the unused reservation.
Unknown-as-committed reconciliation is deliberately outside this implementation.

## Review contract

For Rung 3, decision timing is `within_bounds`; for Rung 4, `retrospective`; Rungs
1/2 use `before_commit` and bound human decisions. Every grant specifies cadence,
reviewer, deterministic sample rule (`all` or `every_nth`), both aggregate checks
(`exposure_total`, `failure_count`), and `lapse_action=suspend`. The example cadence
of 20 synthetic ticks and sample parameters are fixture choices, not universal
thresholds. The reviewer must identify all selected cases and required aggregate
checks; the log records exposure and failure totals. This verifies submitted
attestation content, not that a real human actually examined it. Overdue review
suspends before another protected effect; later review alone does not resume.

## Semantic boundaries

Ancestor obligations are conjunctive, even when a child lists broader local
scope. No numeric rung comparison or unrelated ambient credential supplies
permission. Child creation can instantiate only the trusted human-accepted actor
and sponsor template. Equal ledger identifiers must retain cap/scope/epoch when a
new grant is installed. Human contractions may lower the current cap, preserving
existing spend and reservations rather than fabricating a reset.

Human prose and attestations remain separate from machine predicates. Correctness
of identity, institutional standing, sponsor competence/capacity/independence,
reversibility classifications, exposure bounds, and semantic alignment MUST be
established outside this prototype. Complete mediation and trusted endpoints are
assumptions, not results demonstrated by this artifact.
