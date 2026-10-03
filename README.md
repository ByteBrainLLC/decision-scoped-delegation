# Decision-Scoped Delegation for AI Systems

By **Ed Fassio**, ByteBrain LLC. Copyright 2026 Ed Fassio and ByteBrain LLC.

Technical research specification and executable reference model grounded in
*The Constitution of the Frontier*. **Not peer reviewed.** The implementation is
a deterministic, synthetic, single-process research model, not a production
authorization service or empirical proof of effective governance.

## Read and download

- [Technical research specification, edition 1.1 (PDF)](papers/Fassio_Decision_Scoped_Delegation_ByteBrain_v1.1.pdf)
- [Exact executable companion archive, version 1.0.2 (ZIP)](archives/Fassio_Delegation_Executable_Companion_v1.0.2.zip)
- [Reference model, schema, fixtures, tests, results, and detailed limitations](companion/README.md)
- [Author's book page](https://edfassio.com/books/the-constitution-of-the-frontier/)
- [ByteBrain Agentic Futures](https://bytebrain.org/agentic-futures/)

The files inside `companion/` preserve the approved version 1.0.2 archive payload.
Repository navigation and download copies are additions outside that frozen
payload. The archive's original statements about unassigned repository URLs
describe its packaging state; this repository is its subsequent publication.

## Licensing and attribution

- **Companion source, schema, tests, synthetic fixtures/results and original
  documentation:** [Apache License 2.0](companion/LICENSE), with
  [NOTICE](companion/NOTICE) and [licensing scope](companion/LICENSING.md).
- **Paper:** its original text and tables are separately licensed under
  [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), subject to the
  paper's stated exclusions. The code license does not replace the paper license.
- Logos, branding, trade names, trademarks, the cited book and paid source
  materials are not granted for branding reuse or relicensed by this repository.
  Consult the actual license terms for customary origin and attribution uses.

Retain applicable attribution and notices and mark changes as the licenses
require. Citation suggestions do not add license conditions. No DOI, publication
acceptance, certification, or third-party endorsement is claimed.

## Suggested citations

Fassio, Ed. 2026. *Decision-Scoped Delegation for AI Systems: A research
specification and evaluation package grounded in The Constitution of the
Frontier*. Public-facing edition 1.1, 3 October 2026. ByteBrain LLC.

Fassio, Ed. 2026. *Delegation grant reference-monitor companion*. Version 1.0.2.
ByteBrain LLC. https://github.com/ByteBrainLLC/decision-scoped-delegation

See [citation metadata](companion/CITATION.cff), [citation details](companion/CITATION.md),
and [provenance](companion/PROVENANCE.md), including AI assistance and the distinction
between the book's concepts and this proposed technical operationalization.

## Reproduce

With Python 3.10 or later, from `companion/`:

```sh
python run_fixtures.py
python run_differential.py
python -m unittest discover -s tests -v
```

The standard-library checks are not general JSON Schema validation. The detailed
README describes optional full-schema validation and the recorded environment.
Recorded results comprise 44 scenarios with 98 asserted transitions, 23
overlapping unit-test methods, and a separate 2-arm/7-transition differential.
These are authored synthetic checks, not independent empirical trials.

## Exact download identity

| Artifact | SHA-256 |
| --- | --- |
| Paper edition 1.1 | `d6b9063df9f183572a1691fa325d782d7c2f67a2030090f4d0962a9b2c910fb9` |
| Companion ZIP version 1.0.2 | `aa649e8608cc3d2217d25db0f43d0d71c9dc7cb24baa749719e873b596be26f0` |

The exact ZIP is stored in `archives/`. GitHub's automatic **Download ZIP** creates
a different archive and must not be described as having the companion ZIP hash.
The prior 1.0.1 ZIP is a historical input, not the current licensed release.
Future modified releases require a new version/hash and coordinated paper update.
