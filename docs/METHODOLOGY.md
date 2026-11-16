# Methodology

1. Verify the authorized source workbook against the SHA-256 fingerprint in
   [provenance.json](../results/provenance.json). Read the EM-DAT Data sheet,
   keep Natural rows and derive Event ID from the source identifier.
2. Retain incomplete dates as blank, preserve explicit numeric zeros, sum
   nonblank country contributions and carry an observed-country count alongside
   each event metric. Retain a blank sum when every contribution is unknown.
   Validate four tables and compare the rebuild checksums.
3. Compare hazard counts, temporal composition, reported totals, means, medians,
   spread and coverage. Rerun the analysis for 2000–2025 and require complete
   country reporting as a separate sensitivity check.
4. Estimate a retrospective mortality classifier from three metadata inputs
   using independent chronological partitions. Explain held-out scores with a
   training-only SHAP reference.
5. Transform complete recent outcome profiles for three complementary embeddings,
   cluster assessment and anomaly triage. The profile task uses measured impact
   directly. The classification task excludes those measures from its inputs.
6. Use event-grain counting and country-restricted contributions in the four
   dashboard views. Country geometry is joined on validated ISO codes. Keep
   historical ISO mismatches in tables.

The historical data dictionary documents all four schema contracts. The new
statistical summaries are long-form and carry the metric, unit, distinct event
count, row count, reporting count and fractional coverage. Value columns report
the observed total, mean, median, sample SD, quartiles, IQR, 90th/99th
percentiles, upper-winsorized mean and largest-event share. Country and region
reporting counts use the country record denominator.
