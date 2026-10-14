# Decision-Scoped Delegation for AI Systems

By **Ed Fassio**, ByteBrain LLC. Copyright 2026 Ed Fassio and ByteBrain LLC.

Technical research specification and executable reference model grounded in
*The Constitution of the Frontier*. **Not peer reviewed.** The implementation is
a deterministic, synthetic, single-process research model, not a production
authorization service or empirical proof of effective governance.

## Read and download

- [Technical research specification, edition 1.1 (PDF)](papers/Fassio_Decision_Scoped_Delegation_ByteBrain_v1.1.pdf)
- [Exact executable companion archive, version 1.0.3 (ZIP)](archives/Fassio_Delegation_Executable_Companion_v1.0.3.zip): security fix, see [changelog](companion/CHANGELOG.md)
- [Previous companion archive, version 1.0.2 (ZIP)](archives/Fassio_Delegation_Executable_Companion_v1.0.2.zip): cited by paper edition 1.1
- [Reference model, schema, fixtures, tests, results, and detailed limitations](companion/README.md)
- [Author's book page](https://edfassio.com/books/the-constitution-of-the-frontier/)
- [ByteBrain Agentic Futures](https://bytebrain.org/agentic-futures/)

The files inside `companion/` are the version 1.0.3 archive payload. Version 1.0.3
fixes a `derive()` flaw in 1.0.2 that let a child grant with no installed parent
become a new root and bypass the parent's caps; see the companion changelog.
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
require. Citation suggestions do not add license conditions. Zenodo DOI registration
does not imply peer review, publication acceptance, certification, or third-party endorsement.

## Suggested citations

Use these **version-specific DOIs** to cite the exact releases. Prefer the paper
when discussing the research specification; also cite the software when using the
reference implementation, fixtures, or results.

**Paper v1.1 (preferred research citation)**

Fassio, Ed. 2026. *Decision-Scoped Delegation for AI Systems: A research
specification and evaluation package grounded in The Constitution of the
Frontier*. Public-facing edition 1.1, 3 October 2026. ByteBrain LLC.
[https://doi.org/10.5281/zenodo.23126767](https://doi.org/10.5281/zenodo.23126767).
[Zenodo record](https://zenodo.org/records/23126767).

**Companion software v1.0.2**

Fassio, Ed. 2026. *Delegation grant reference-monitor companion*. Version 1.0.2.
ByteBrain LLC. [https://doi.org/10.5281/zenodo.23126782](https://doi.org/10.5281/zenodo.23126782).
[Zenodo record](https://zenodo.org/records/23126782).

See the current [citation metadata](CITATION.cff), [citation details](CITATION.md),
and [provenance](companion/PROVENANCE.md), including AI assistance and the distinction
between the book's concepts and this proposed technical operationalization.
The root citation metadata identifies the software DOI and supplies the paper as
`preferred-citation`. Citation files inside `companion/` record the packaging version (1.0.3). A
version-specific DOI for software 1.0.3 will be added once Zenodo archives it; until
then, cite 1.0.2 by its DOI and note the 1.0.3 fix.

## Reproduce

With Python 3.10 or later, from `companion/`:

```sh
python run_fixtures.py
python run_differential.py
python -m unittest discover -s tests -v
```

The standard-library checks are not general JSON Schema validation. The detailed
README describes optional full-schema validation and the recorded environment.
Recorded 1.0.3 results comprise 46 scenarios with 100 asserted transitions, 23
overlapping unit-test methods, and a separate 2-arm/7-transition differential.
These are authored synthetic checks, not independent empirical trials. Paper
edition 1.1 reports the 1.0.2 counts (44 scenarios, 98 transitions).

## Exact download identity

| Artifact | SHA-256 |
| --- | --- |
| Paper edition 1.1 | `d6b9063df9f183572a1691fa325d782d7c2f67a2030090f4d0962a9b2c910fb9` |
| Companion ZIP version 1.0.3 | `f924c4cd4ab78782789a4f834579a69c2c87385f68156edc3637c1a58bec7f78` |
| Companion ZIP version 1.0.2 | `aa649e8608cc3d2217d25db0f43d0d71c9dc7cb24baa749719e873b596be26f0` |

The exact ZIP is stored in `archives/`. GitHub's automatic **Download ZIP** creates
a different archive and must not be described as having the companion ZIP hash.
The 1.0.2 ZIP and the prior 1.0.1 ZIP are historical; 1.0.3 is the current release.
Future modified releases require a new version/hash and coordinated paper update.
