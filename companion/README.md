# Delegation grant reference-monitor companion, version 1.0.2

**Research reference implementation. Synthetic simulation only.** This executable
companion accompanies the revised Ed Fassio Delegation Ladder research
specification. It operationalizes selected proposed extensions; it is not code
from *The Constitution of the Frontier*, a production authorization service,
certification, or empirical validation of the book's governance claims.

Copyright 2026 Ed Fassio and ByteBrain LLC. This companion's original source,
schema, tests, synthetic fixtures/results, and documentation are licensed under
[Apache License 2.0](LICENSE). See [LICENSING.md](LICENSING.md) and [NOTICE](NOTICE).
The related paper, *Decision-Scoped Delegation for AI Systems*, edition 1.1, licenses
its original text and tables separately under CC BY 4.0. The paper and book are not
bundled here, and no additional branding or trademark rights are granted.
Citation and provenance are provided in [CITATION.md](CITATION.md), `CITATION.cff`,
and [PROVENANCE.md](PROVENANCE.md).

## What was actually run

On 2026-10-03, Python 3.12.14 and the already-installed `jsonschema` 4.26.0 ran:

- 44 predeclared scenario fixtures: 44 passed, 0 mismatches
- 98 asserted allow/deny/escalate transitions within those scenarios
- The same 44 scenarios in pure-standard-library mode: 44 passed
- 23 `unittest` test methods: passed; one method reruns the scenario suite, so
  these counts are overlapping checks, **not independent trials**
- One additional, separately reported differential experiment: 2 policy arms,
  4 admission observations and 3 commit observations (7 transitions); both
  predeclared arm oracles matched in full-schema and standard-library modes
- Six serial arrival permutations of three 60-unit requests within one unit
  test; two explicit child-admission orderings in the fixture suite

These are observed deterministic test results against authored oracles. They
provide no measured unauthorized-action rate, statistical confidence bound,
human-oversight efficacy estimate, or distributed concurrency guarantee.

## Reproduce locally

No network, accounts, credentials, real recipients, or external effects are used.
From this directory, using Python 3.10 or later:

```sh
python run_fixtures.py
python run_differential.py
python -m unittest discover -s tests -v
```

The evaluator and these commands use only Python's standard library. This mode
performs explicitly named **custom model shape checks**, plus model constraints.
It does not claim general JSON Schema compliance.

For full validation against the supplied Draft 2020-12 schema, if `jsonschema`
is already installed:

```sh
python run_fixtures.py --full-schema --output results/fixture-results.json
python run_differential.py --full-schema --output results/differential-results.json
```

The recorded full-schema run used version 4.26.0 (also identified in
`requirements-optional.txt`). If the optional package is missing, this command
fails; it does not silently relabel the custom checks as full validation. No
package is installed automatically. The published schema is self-contained and
uses no network-resolved references. See the [Draft 2020-12 specification](https://json-schema.org/draft/2020-12)
and [`Draft202012Validator` documentation](https://python-jsonschema.readthedocs.io/en/stable/validate/).

## Files and artifact boundary

- `grant.schema.json`: versioned, machine-readable proposed grant shape
- `fixtures/grant.json`: complete synthetic, human-readable root grant
- `fixtures/effect.json`: complete protected-effect descriptor
- `fixtures/cases.json`: fixed inputs and predeclared expected outcomes
- `monitor.py`: process-local state machine, reference monitor, and simulated endpoint
- `run_fixtures.py`: replay runner; compares observations with fixture oracles
- `fixtures/differential.json`: identical two-request inputs, declared comparison
  policies, and manually specified differential oracles
- `run_differential.py`: isolated static-per-call versus shared-ledger comparison
- `results/differential-results.json`: full-schema differential observations
- `results/differential-stdlib-results.json`: standard-library differential replay
- `results/differential-full-schema-run.log`, `differential-stdlib-run.log`:
  actual differential run logs
- `tests/test_monitor.py`: edge, integrity, idempotency, and serial-order tests
- `STATE_MACHINE.md`: admission and lifecycle semantics and field interpretation
- `results/fixture-results.json`: full-schema expected-versus-observed results
- `results/stdlib-fixture-results.json`: independent replay using custom checks
- `results/worked-trace.json`: complete primary two-child budget trace
- `results/full-schema-run.log`, `stdlib-run.log`, `unit-tests.log`: actual run logs
- `manifest.sha256`: hashes of the frozen distributed files, excluding itself
- `LICENSE`, `NOTICE`, `LICENSING.md`: Apache-2.0 terms, attribution, and scope
- `CITATION.md`, `CITATION.cff`, `PROVENANCE.md`: citations and contribution boundary
- `CHANGELOG.md`: release changes; 1.0.2 changes licensing/metadata, not decisions

`_build_schema.py`, `_build_fixtures.py`, and `_build_differential_fixture.py` are
maintainer utilities. The fixture
builder never imports or executes the monitor and never derives expectations
from observed outcomes. Running these utilities is not necessary to reproduce
the results. Changes to either the schema or the fixtures require a new review
and rerun; their hashes are pinned in the distribution manifest.

## Versioning and exact archive identity

Distribution version 1.0.2 adds the approved license, citation, and provenance
metadata while preserving all decision behavior and fixture oracles. Version 1.0.1
added the isolated differential experiment. The grant
schema remains 1.0.0, and the original 44-fixture suite and 23 unittest methods are
unchanged. The differential is not folded into or counted as another original
scenario. Its two arms replay the same two requests; these are deterministic
observations, not additional independent empirical trials.

The external ZIP SHA-256 is reported alongside the delivered archive and in the
paper. This archive contains no copy of the paper or self-referential ZIP hash.
`manifest.sha256` pins its payload files; the paper can therefore identify the
exact ZIP without a circular hash dependency.

## Added differential: per-call limit versus shared exposure

`fixtures/differential.json` fixes two complete requests, `E-a` and `E-b`, each
for 60 units, from accepted child actors. Both arms use identical descriptors,
static scope, a 70-unit per-effect cap, time zero, valid unchanged human/scope
prerequisites, and the same admission-then-commit order. Their canonical request
hashes match in the results. The declared comparison dimension is cumulative
budget control. Both admission attempts occur before either permitted commitment,
so the shared reservation alone is sufficient to reject the second request:

- Static permissions plus per-call cap: both admissions allow; both simulated
  effects commit; post-hoc committed total is **120 units**
- Shared workflow ledger with limit 100: `E-a` admits and commits; `E-b` admission
  denies at **R5**; committed total is **60 units**, final reserved total is zero

The static baseline deliberately implements no cumulative admission or reservation
ledger. Its endpoint receipt log deduplicates commits and supports post-hoc
measurement; the accumulated total is never consulted during admission. It checks
the expressly listed static actor/grant, scope, version, fixed-context, and per-call
constraints. It is a narrow comparison component, not an alternative production
authorization system. The shared arm runs the existing reference monitor.

The experiment demonstrates the difference between **these specified controls**
on one pinned budget example. It does not establish that all static-permission
designs are unsafe, that runtime mediation always succeeds, or that a static
system could not be combined with an external cumulative-budget mechanism. All
other conditions are held valid; approval drift, revocation, human oversight, and
real endpoint failure are not being compared in this differential.

Both arm oracles were written in the fixture before replay and independently
specify admissions, committed identifiers, and committed totals. The runner exits
nonzero on an oracle mismatch. The 2 arms / 7 observed transitions are reported
separately from the original 44 scenarios / 98 transitions and the 23 overlapping
unit-test methods.

## Exact primary worked example

The root grant and two accepted derived grants share ledger `L-shared`, accounting
epoch `E1`, with a 100-unit workflow cap. Child `child-a` proposes `E-a` for 60 units;
child `child-b` proposes `E-b` for 60 units. After both derived grants register:

1. Admit `E-a`: **allow**, reserve 60; committed 0, reserved 60
2. Admit `E-b`: **deny R5**; committed 0, reserved 60
3. Commit `E-a`: **allow**, committed 60, reserved 0

The reverse arrival order also passes its independently stated oracle and gives
the reservation to `E-b`. Work is not divided into independent copies of a budget.
The operation called `analyze` is a recorded synthetic protected effect; no model
inference or corpus processing actually occurs.

## Scope and decision semantics

The book's labels remain decision-scoped: 1 Execute; 2 Recommend; 3 Decide within
bounds; 4 Decide and act, reviewed after; 5 Set the bounds. The grant schema permits
machine decision contracts only at 1–4. Rung numbers are never compared to decide
permission inclusion. All ancestor business-scope predicates and obligations
apply conjunctively to the actual descendant actor and proposed effect.

Rungs 1 and 2 require a payload-bound human choice for commitment. This models
exact execution of a settled recommendation, not a promotion of the recommender.
Rungs 3 and 4 have explicit decision timing, sampling, aggregate checks, and review
deadlines. Rung 4 admits only modeled `restorable` effects. An irreversible or
otherwise non-restorable proposed Rung 4 commitment is held for an appropriate
human-chosen exact-execution contract. No machine can activate proposed bounds
or resume suspended authority through the governance interface.

`intent` is prose for a human to inspect. `pinned_predicates` uses the intentionally
small, versioned `edf-exact-v1` language: exact equality, list membership, or
nonnegative-integer upper bounds on dotted effect fields. Missing mandatory fields
hold the request; false predicates deny it. There is no `eval`, arbitrary policy
code, natural-language compiler, or claim that the predicates capture all harms.

The **intent_text_alone_is_not_enforced** case is an important negative assurance
result: if a trusted human attestation incorrectly says that contradictory prose
and predicates align, the monitor allows the effect. The software cannot establish
semantic equivalence. The **intent_predicate_known_mismatch** case instead holds
an explicitly recorded known mismatch. Neither result is hidden by the pass count.

## Threat model and trust assumptions

The machine actor may propose an out-of-scope effect, request broader child
permissions, vary approved payloads, submit stale work, reuse identifiers, or
attempt governance changes. Those requests enter the modeled monitor.

Trusted in this simulation:

- The fixture harness, its administrative events, and nondecreasing integer clock
- Human-role, sponsorship, coverage, acceptance, and assurance records
- Immutable installed grants and version pins (accidental post-install changes
  are detected by a digest check)
- Correct resolved resource/recipient identifiers and exposure upper bounds
- One process-local `RLock`, monitor memory, and the simulated endpoint
- Human review attestations, including that examination actually occurred

The strings `human-issuer`, `human-sponsor`, and `human-reviewer` are synthetic
identities. Flags and recorded evidence references **do not authenticate real
people or establish organizational standing, competence, capacity, independence,
or meaningful review**. Sponsor acceptance and practical inspect/halt/refuse
powers are represented as trusted registry inputs. The filled independence
attestation represents external assessment of capacity, competence, independence,
and an effective escalation route; this code verifies only its presence/expiry.

SHA-256 is used as a stable content digest to detect local binding changes, not as
a signature, key-management system, or authenticated identity protocol. The monitor
is not protected from an adversary who can change its Python state or bypass it.

## Failure handling actually implemented

- Admission reserves shared exposure, claims any one-use approval, and appends the
  intended effect under one lock; no external side effect occurs at admission
- The simulated endpoint rechecks mutable authority, all ancestors, expiry,
  sponsorship, policy/configuration pins, review, scope, recovery, and fences
- A revoked ancestor prevents a queued descendant's later commitment
- Duplicate commitment returns the existing receipt and does not charge twice
- A definitive pre-commit rejection releases the unused reservation
- A known endpoint failure releases exposure but does not unspend its approval
- An unknown endpoint result retains both reservation and approval claim and
  forbids blind retry; only trusted `not_committed` reconciliation is implemented
- Sponsor loss or review lapse suspends authority; an accepted coverage record
  or successor is represented separately from an absent/unaccepted sponsor
- Completing overdue review does not itself resume a suspended grant
- A cap reduction below already committed exposure records the overage and stops
  additional effects; creating a child cannot reset a shared ledger's epoch

## Explicit limitations and out-of-scope properties

This is a single-process, in-memory model with serialized transitions. It does not
implement durable logging, transactions surviving process death, databases, actor
isolation, real endpoints, credential confinement, encrypted logs, recovery from a
crash inside a transaction, multithreaded stress, linearizability, distributed
fencing, network partitions, time-source security, or cross-service exactly-once
execution. The “audit storage unavailable” fixture changes a simulation flag; it
is not a storage fault-injection experiment. The “ambient credential” fixture
rejects broader requested business effects through the monitor; it cannot prevent
use of a real out-of-band credential.

Unknown outcomes that were actually committed but not observed are not modeled.
The system intentionally retains exposure indefinitely until the implemented
negative reconciliation is provided. Real deployments need positive settlement,
endpoint receipts, bounded leases, and human resolution without blind replay.

The model has one nonnegative integer exposure dimension. Costs, harms,
classifications, reversibility, and scope are supplied facts, not inferred. No
claim is made about fairness, proxy drift, social harms, decision quality, recourse
quality, real sponsor independence, or the sufficiency of the chosen limits.

The governance method's `actor_type='human'` is a **trusted harness assertion**,
not an authentication check. Likewise, fixture `state` steps represent trusted
organizational events. Exposing these methods to untrusted agents would invalidate
the model. A new human-approved immutable grant version and safe supersession are
specified conceptually; a complete issuance, renewal, or migration service is not
implemented here. The full paper's abstract model is broader than this subset.

## Prospective empirical evaluation, not yet performed

Before any empirical claim, preregister task families, threat models, protected
effect definitions, excluded actions, severity weights, exposure denominators,
oracle adjudication, sample sizes, stopping rules, and uncertainty reporting.
Compare the same task inputs under (a) model instructions alone, (b) tool-level
allowlists/per-call limits, (c) reusable approval flags, and (d) the complete
mediated contract. Do not send unsafe effects into real systems for comparison;
use instrumented endpoints with independently labeled admissibility.

Add independent tasks and adversarial inputs beyond these authored fixtures.
Measure attempted effects separately from actual endpoint commitments; record
unauthorized commitments, missed authorized work, escalation burden, review delay,
post-revocation commitments, evidence completeness, and recovery quality. Test
concurrent service histories, restarts, partitions, replay, credential bypass, and
late policy changes against explicit consistency assumptions. A separate human
study must assess whether sponsors and reviewers understand the bounds, have time
to examine evidence, can refuse, and can stop work in practice. Zero observed
failures cannot establish zero risk. None of those studies was performed here.
