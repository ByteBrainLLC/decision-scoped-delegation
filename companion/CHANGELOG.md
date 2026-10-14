# Changes

## 1.0.3 — 14 October 2026

Security fix. Found in an independent review of 1.0.2.

- `derive()` accepted a child grant whose `parent_grant_id` was null or unknown.
  The ancestor chain came back empty, so template, depth, lineage, and
  active-ancestor checks were skipped and the child was installed as a new root
  with its own caps and recipients. `derive()` now denies at R1 unless the parent
  is an installed grant
- `derive()` now enforces Table 3C's "no fresh ledger" rule: a child may draw only
  on ledgers held by its ancestors; any other ledger is denied at R1
- Add fixtures `derive_without_parent_denied` and `derive_fresh_ledger_denied`
  (46 scenarios, 100 asserted transitions). Both fail on 1.0.2 and pass on 1.0.3
- The 44 earlier fixture inputs and oracles, the differential, the grant schema
  (1.0.0), and the 23 unittest methods are unchanged
- Rerun all tests and both validation modes; regenerate results, logs, and manifest
- Known gap: the fixture runner still injects `parent_grant_id='G-root'` by
  default; fixtures that test derive edge cases must override it explicitly

## 1.0.2 — 3 October 2026

- Apply Apache License 2.0 to the original companion source, schema, tests,
  synthetic fixtures/results, and documentation; add the complete official
  LICENSE, NOTICE, SPDX Python headers, and explicit licensing scope
- Replace the previous unspecified-license/author-review labeling with a
  research-reference-implementation description; preserve all implementation,
  threat-model, assurance, and empirical limitations
- Add software and paper citation guidance, machine-readable CITATION.cff, and
  provenance. The related paper's original text/tables are separately CC BY 4.0;
  the book, paid materials, third-party material, and brand rights are not relicensed
- Update distribution/version metadata to 1.0.2. Grant schema stays 1.0.0
- Do not change monitor logic, test oracles, original fixture inputs, differential
  inputs, admission/commit decisions, or measured totals
- Rerun all original tests and both differential validation modes, regenerate
  result metadata/logs and the manifest, and verify a fresh extraction of the ZIP
- Preserve the earlier archives; do not include the paper or a self-referential
  ZIP hash inside this distribution

## 1.0.1 — 3 October 2026

- Add an isolated, pinned two-request differential: static permissions and a
  70-unit per-call cap commit two 60-unit requests (120 total); a 100-unit shared
  reservation ledger denies the second at R5 and commits 60
- Keep the original 44 scenarios / 98 transitions and 23 overlapping unittest
  methods separately reported from 2 differential arms / 7 observed transitions
- Preserve the narrow interpretation: these specified controls in fixed valid
  context, not a universal finding about static-permission systems

## 1.0.0 — 3 October 2026

- Initial process-local simulation, grant schema, fixed oracle fixtures, worked
  trace, unit checks, lifecycle semantics, and explicit limitations
