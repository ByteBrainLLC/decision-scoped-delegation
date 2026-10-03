# Provenance and contribution boundary

Author: Ed Fassio. Affiliation: ByteBrain LLC.

## Conceptual sources

The primary conceptual source is Ed Fassio's *The Constitution of the Frontier:
What Must Remain True, No Matter How Intelligent the Machines Become*, first
edition, 2026. Its five-rung Delegation Ladder, retained human authority over the
bounds, and Sponsor of Record commitments guide this work.

The related paper is *Decision-Scoped Delegation for AI Systems: A research
specification and evaluation package grounded in The Constitution of the
Frontier*, public-facing edition 1.1, 3 October 2026. That paper situates the
technical proposal and its antecedents. This companion provides executable
examples for a selected subset of the proposed model; it does not implement every
obligation discussed in the book or paper.

The machine-readable grant, process-local reference monitor, explicit transition
semantics, synthetic oracle fixtures, and differential implementation are technical
extensions. They are not claimed to be an implementation supplied by the book or
a demonstration that the broader constitutional commitments have been achieved.

Generative AI assisted implementation, fixture construction, documentation, and
preparation of the associated research materials. The checked-in logs record actual
execution of the supplied deterministic tests. They are not observational field
data, human-subject results, or estimates of production failure rates.

## File provenance and external components

- Python sources, schema, fixtures, and documentation were prepared for this
  companion; version-to-version changes are recorded in CHANGELOG.md
- Fixture expected outcomes were authored before replay, independently of observed
  results; maintainer fixture builders do not import or run the monitor
- The unchanged grant schema remains version 1.0.0; distribution version 1.0.2
  changes licensing/citation metadata rather than schema or decision semantics
- `LICENSE` is the official Apache License 2.0 text fetched from
  https://www.apache.org/licenses/LICENSE-2.0.txt on 3 October 2026;
  SHA-256: cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30
- Python 3.12.14 and the already-installed optional `jsonschema` 4.26.0 were used
  for the recorded validation; neither dependency is redistributed in the ZIP
- No private source documents, paid book materials, credentials, or external-service
  data are included. All actors, authority records, and effects are synthetic

The previously delivered 1.0.0 and 1.0.1 archives are preserved as historical
artifacts. Version 1.0.2 supplies the approved Apache-2.0 licensing for this
companion and cites the separately licensed CC BY 4.0 paper. No repository location,
DOI, publication acceptance, or third-party endorsement is inferred.
