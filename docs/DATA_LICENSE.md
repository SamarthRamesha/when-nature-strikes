# Data provenance and publication

The analysis uses **EM-DAT data, 2026, CRED / UCLouvain, Brussels, Belgium**,
custom-request export version 23 October 2026, delivered 31 October 2026.
The exact workbook fingerprint is recorded in the [project provenance](../results/provenance.json).
Request the same export through the [EM-DAT public portal](https://public.emdat.be/).

## What the release branch distributes

| Asset | Basis for inclusion |
| --- | --- |
| Invented demonstration rows | The labeled CSVs under `dashboard/powerbi/` are project fixtures. The packaged PBIP embeds those fixtures. |
| Aggregate results and academic artifacts | EM-DAT allows the publication of attributed analyses, aggregate figures, charts and findings. [EM-DAT FAQ](https://doc.emdat.be/docs/additional-resources-and-tutorials/faq/#can-i-redistribute-em-dat-data) · [Citation policy](https://doc.emdat.be/docs/legal/citation-policy/) |
| Natural Earth boundaries | The country polygons are public-domain Natural Earth data. [Boundary provenance](../dashboard/BOUNDARIES.md) · [Natural Earth terms](https://www.naturalearthdata.com/about/terms-of-use/) |
| Shared Power BI report scaffold assets | Microsoft Power BI report-authoring CLI supplies the scaffold and Fluent base theme. The bundled MIT notice covers those assets. [Microsoft license notice](../dashboard/powerbi/MICROSOFT_LICENSE.txt) |

The custom-request workbook and detailed derivatives remain local. This
includes all four prepared tables, granular country and hazard exports,
row-level predictions and ICE, exact event embeddings, fitted models and
PBIX files with imported authorized data. This project has no separate
redistribution permission or Archive DOI for this export. The separate
EM-DAT Archive has its own CC BY-NC-ND terms for unchanged snapshots.
[EM-DAT terms](https://doc.emdat.be/docs/legal/terms-of-use/) · [EM-DAT documentation](https://doc.emdat.be/)

The supplied original Power BI files, including both imported-data PBIX
files, the template with a local source reference and the standalone PBIP
entry, are kept separately in the local recovery workspace. The integrated
public project includes the rebound report definitions and labeled invented
fixtures. [Recovery and source evidence](RECOVERY_AND_POWER_BI.md)

The publication rules above cover the named assets. The team has yet to
record a general reuse license for the repository's original code and materials.

## Existing public exposure

At the handover audit, GitHub's default branch `main` still tracked the
custom workbook and all four prepared CSVs. Historical commits `9613b1a`
(workbook) and `a0140c4` (prepared CSVs) also retain these assets. The current
review branch drops the five paths, checks tracked paths in CI, and retains
original history. The owner should coordinate with CRED about the exposure
and decide how to publish the cleaned default branch after reviewing draft
PR #3. [Release review](https://github.com/SamarthRamesha/when-nature-strikes/pull/3)
