# Changes

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
