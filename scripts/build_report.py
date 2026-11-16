"""Build the editable academic report from verified analysis artifacts."""
import csv
import json
from pathlib import Path
import re

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SUBMISSION = ROOT / "submission"
METRICS = ("Deaths", "Affected population", "Adjusted damage")
FIELDS = ("Total Deaths", "Total Affected", "Total Damage, Adjusted (million US$)")
document = Document()
section = document.sections[0]
section.top_margin = Inches(.7)
section.bottom_margin = Inches(.68)
section.left_margin = Inches(.88)
section.right_margin = Inches(.88)
for name in ("Normal", "Title", "Subtitle", "Heading 1", "Heading 2", "Caption"):
    style = document.styles[name]
    style.font.name = "Aptos"
    style.font.color.rgb = RGBColor.from_string("000000")
    style.paragraph_format.space_after = Pt(7)
document.styles["Normal"].font.size = Pt(11)
document.styles["Normal"].paragraph_format.line_spacing = 1.12
document.styles["Heading 1"].font.size = Pt(23)
document.styles["Heading 2"].font.size = Pt(13)
document.styles["Title"].font.size = Pt(39)
for border in document.styles["Title"].element.xpath(".//w:pBdr"):
    border.getparent().remove(border)
document.styles["Subtitle"].font.size = Pt(18)
document.styles["Caption"].font.size = Pt(9)
document.styles["Caption"].font.italic = False
document.core_properties.title = "When Nature Strikes"
document.core_properties.subject = "Natural disaster frequency and reported impact"
document.core_properties.author = "When Nature Strikes project team"
footer = section.footer.paragraphs[0]
footer.alignment = WD_ALIGN_PARAGRAPH.RIGHT
footer.add_run("When Nature Strikes  /  ")
field = OxmlElement("w:fldSimple")
field.set(qn("w:instr"), "PAGE")
footer._p.append(field)


def artifact(name):
    return json.loads((RESULTS / name).read_text())


def records(name):
    with (RESULTS / name).open() as input_file:
        return list(csv.DictReader(input_file))


def page(title):
    document.add_page_break()
    document.add_heading(title, 1)


def paragraph(*items):
    for item in items:
        document.add_paragraph(item)


def figure(name, caption, width=6.35):
    p = document.add_paragraph()
    p.paragraph_format.keep_with_next = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(RESULTS / "figures" / f"{name}.png"), width=Inches(width))
    document.add_paragraph(caption, "Caption")


def table(headers, rows):
    tab = document.add_table(rows=0, cols=len(headers))
    tab.style = "Table Grid"
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "bottom", "left", "right", "insideH", "insideV"):
        line = OxmlElement(f"w:{edge}")
        line.set(qn("w:val"), "single")
        line.set(qn("w:color"), "D9D9D9")
        borders.append(line)
    tab._tbl.tblPr.append(borders)
    for index, values in enumerate([headers, *rows]):
        row = tab.add_row()
        for cell, item in zip(row.cells, values):
            cell.text = str(item)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(3)
            for run in p.runs:
                run.font.size = Pt(10)
                run.bold = index == 0
            if index == 0:
                fill = OxmlElement("w:shd")
                fill.set(qn("w:fill"), "EAF2F5")
                cell._tc.get_or_add_tcPr().append(fill)


def sub(title):
    document.add_heading(title, 2)


f = artifact("findings.json")
m = artifact("model_metrics.json")
shap = artifact("shap_summary.json")
profiles = artifact("profile_summary.json")
geo = artifact("map_summary.json")
provenance = artifact("provenance.json")
types = records("impact_by_type.csv")
corrs = records("correlations.csv")
overall = {r["metric"]: r for r in records("overall.csv")}
model = m["test"][m["selected"]]
freq = next(iter(f["type_counts"]))
reference_rows = [line.strip("| ").split(" | ")[:2] for line in (ROOT / "docs/LITERATURE_REVIEW.md").read_text().splitlines()
                  if re.match(r"^\| \[\d+\]", line)]

title = document.add_paragraph("When Nature Strikes", "Title")
title.paragraph_format.space_before = Pt(46)
document.add_paragraph("A Visualization Approach to Determine the Impact of Natural Disasters", "Subtitle")
paragraph("Undergraduate Computer Science Engineering project", "Samarth Ramesha, Shashank S K, Shreya Patil and Shreya S Mattimadu",
          "Technical submission draft for team and faculty review · 16 November 2026")
sub("Abstract")
paragraph(
    f"Are the most frequent natural disasters also the most destructive? We consolidated {f['impacts']:,} EM-DAT "
    f"country-impact records into {f['events']:,} events. {freq} occurred most frequently "
    f"({f['type_counts'][freq]:,} events) and led total reported affected population. Storms led total adjusted damage, "
    "earthquakes led average adjusted damage, and historical droughts led total and mean reported mortality. "
    "The ranking changes with the loss measure, the aggregation and the time window.",
    f"In a retrospective, chronological test of {m['splits']['test']['events']:,} single-country events with reported mortality, "
    f"{m['selected'].lower()} achieved {model['average_precision']:.3f} average precision. An analysis of "
    f"{profiles['complete_events']:,} events with all three impacts reported compared PCA, t-SNE, UMAP and cluster diagnostics. "
    "A four-view dashboard makes the reporting denominators and geographic coverage available alongside the findings.")
sub("Report guide")
paragraph("Study scope and literature · Data and reproducibility · Frequency and impact · Statistical evidence · "
          "Mortality classification and SHAP · Impact profiles · Dashboard and geography · Discussion · References")

page("Study scope and related work")
sub("Problem and objectives")
paragraph("Recorded frequency is often available even when the harms from those events are missing. A frequency ranking therefore cannot on its own answer questions about accumulated losses or losses per reporting event. This study compares hazard rankings by frequency and nine definitions of reported impact. It examines stability across time, documents geography and reporting, and evaluates whether a narrow mortality task can be learned from basic event metadata.")
sub("What prior work contributes")
paragraph("Delforge et al. describe EM-DAT’s collection system, eligibility criteria and country-level record structure [1, 14]. Jones et al. show that observed loss missingness varies by hazard, time and socioeconomic conditions [2]. Gall et al. identify six classes of loss database bias, including changes in reporting, geographic coverage and accounting conventions [3]. These findings motivate visible coverage and an explicit recent period.")
paragraph("Jäger et al. illustrate how limited information about interactions between hazards constrains attribution [4]. We use the recorded primary hazard and retain associated hazard tags as metadata. Rosvold and Buhaug demonstrate how subnational analysis requires additional geocoding and validation [5]. This project maps reported impacts at country level.")
paragraph("Precision-recall evaluation exposes performance on an infrequent positive class [6]. SHAP offers an additive decomposition of scores relative to reference data [7]. Comparison of linear PCA and local nonlinear projections distinguishes variance from neighborhood preservation [8–10]. Density-connected groupings and isolation scores address exploratory segmentation [11, 12]. Munzner’s design model connects analytical tasks, visual encodings and implementation checks [13].")
sub("Project contribution")
paragraph("The workflow links distinct events, loss summaries, reporting denominators and geographic filtering through one set of metric rules. The inferential checks are exploratory. The retrospective model and profile study examine different subsets and have separate interpretations.")

page("Data engineering and provenance")
paragraph("The source is the EM-DAT custom-request export version 2026-10-23, delivered on 31 October 2026, from CRED / UCLouvain. The source workbook is read without modification. The DisNo. field embeds a country suffix. The preparation pipeline filters to the Natural group, removes that suffix for the consolidated Event ID, and retains the original country-impact identifiers.")
table(["Source property", "Verified value"], [
    ("Workbook rows", f"{provenance['source_rows']:,}"), ("Natural country-impact records", f"{f['impacts']:,}"),
    ("Distinct natural events", f"{f['events']:,}"), ("Events spanning multiple countries", f"{provenance['multi_country_events']:,}"),
    ("Primary disaster types", provenance["types"]), ("Rows with both coordinates", f"{provenance['coords']:,}"),
    ("Country/year/type groups", f"{provenance['country_year_type_groups']:,}"), ("Coverage", "1900–2026, final year partial")])
paragraph("Four tables serve country impacts, unique events, hazard totals and country/year/type summaries. The event table adds reporting counts and preserves an unknown result when every country contribution is blank. A single reported contribution makes a partially documented event observable for that metric. A sensitivity table requires complete reporting across the contributing countries.")
paragraph("Adjusted total damage is the export's adjusted loss field in thousands of US dollars, divided by 1,000 for millions. Incomplete dates remain blank. Hazard magnitude has units that differ across hazards and is excluded from new models and comparisons. For consistent geography filters the dashboard uses each event’s canonical start year. The geographic analytical tables retain source country-row start year.")
paragraph("The repeat build matched all four SHA-256 fingerprints. The 71-check baseline validator returned 69 passes, two warnings and zero failures or skips. The warnings cover recorded zero magnitudes and the double-count that would result from summing country event counts. The independent EDA script reproduced 89 comparisons.")

page("Frequency and reported impact")
paragraph(f"{freq} accounted for {f['type_counts'][freq]:,} of {f['events']:,} events. Storm, earthquake and epidemic followed with "
          f"{f['type_counts']['Storm']:,}, {f['type_counts']['Earthquake']:,} and {f['type_counts']['Epidemic']:,}. "
          "Fog, animal incident and impact each appeared once. The three impact metrics have different reporting denominators.")
report_rows = []
for label, metric in zip(METRICS, FIELDS):
    pool = [r for r in types if r["metric"] == metric and r["window"] == "1900–2026"]
    for summary in ("total", "mean", "median"):
        leader = max((r for r in pool if r[summary]), key=lambda r: float(r[summary]))
        unit = "M USD" if metric == FIELDS[2] else "people"
        val = float(leader[summary])
        report_rows.append((f"{label}, {summary}", leader["Disaster Type"],
                            f"{val:,.1f} {unit}" if metric == FIELDS[2] else f"{val:,.0f} {unit}",
                            f"{leader['reported']}/{leader['events']}"))
table(["Measure", "Leading hazard", "Reported value", "Reporting events"], report_rows)
paragraph(f"Full-window event coverage is {f['coverage'][FIELDS[0]]:.1%} for deaths, {f['coverage'][FIELDS[1]]:.1%} for affected population "
          f"and {f['coverage'][FIELDS[2]]:.1%} for adjusted damage. The mortality median for fog comes from a single event. With at least "
          "20 reports, drought has the highest historical mortality median at 200 deaths. Drought mortality rests on only 67 of 647 events.")
paragraph("The recent window changes the mortality conclusion. During 2000–2025, earthquakes lead total and mean deaths, while extreme temperature leads the median. Earthquakes also lead mean adjusted damage in that window. Capping the top one percent within each hazard changes the leading mean adjusted damage to extreme temperature in the full window and drought in 2000–2025.")

page("Frequency severity and statistical evidence")
figure("frequency_vs_impact", "Figure 1. Distinct-event frequency against total, mean and median reported impacts, by hazard. Marker size represents reporting coverage. Currency is in million adjusted US dollars.", 6.15)
paragraph("Pearson, Spearman and Kendall compare paired hazard-level frequency and loss summaries. Spearman is the main rank analysis. We resampled hazard pairs 2,000 times to illustrate coefficient sensitivity and applied Holm correction to nine Monte Carlo permutation tests per period [16]. The categories are fixed, sparse, and share reporting conditions. The intervals describe sensitivity to category composition.")
rank_rows = []
for label, metric in zip(METRICS, FIELDS):
    pool = {r["statistic"]: r for r in corrs if r["window"] == "1900–2026" and r["method"] == "Spearman" and r["metric"] == metric}
    rank_rows.append([label, *[f"{float(pool[x]['coefficient']):.2f}" for x in ("total", "mean", "median")]])
table(["Impact", "Total ρ", "Mean ρ", "Median ρ"], rank_rows)
paragraph("Totals carry a mechanical frequency component because total = reporting count × mean. The per-event summaries show weaker rank associations. Kruskal–Wallis compares rank distributions across hazards with at least 20 reports. The full-window epsilon-squared estimates are 0.061 for deaths, 0.156 for affected and 0.030 for damage. These comparisons are conditional on reporting, and events may still share geographic or historical influences.")

page("Temporal patterns and coverage")
figure("annual_trends", "Figure 2. Annual event counts and rolling reporting coverage. The open marker shows partial 2026. Coverage trends average five adjacent annual proportions.")
paragraph(f"{f['busiest_year']} is the busiest recorded year in this snapshot. The record contains 6,710 events before 2000, 8,864 during 2000–2025 and 153 in partial 2026. Affected-population coverage rose from 66.3% before 2000 to 87.7% in 2000–2025. Only one event reports adjusted damage in partial 2026.")
paragraph("The recorded annual and decadal patterns reflect the reporting system, criteria and exposure as well as events. CRED flags historical time bias, so full-history trends describe the archive. The recent-period analyses use complete calendar years to avoid the 2026 endpoint. The annual-by-hazard output supports composition checks within those windows.")
sub("Reading denominators")
paragraph("An event reporting count is the number of unique Event IDs with at least one observed loss contribution. A country reporting count uses the country-impact records within the selected scope. Affected totals count instances of reported impact and may include the same people in different events. Country and regional comparisons use absolute recorded impacts without population normalization.")

page("Retrospective mortality classification")
paragraph(f"The task ranks recorded single-country events by probability of at least {m['threshold_deaths']} reported deaths. "
          "Inputs are primary hazard, region and start month. Month missingness is an explicit category. Year is used only for splitting, "
          "and IDs, losses, response indicators, and post-event fields are excluded. Multi-country and death-unknown events are out of scope.")
table(["Partition", "Years", "Events", "Positive"], [
    (name.title(), "–".join(map(str, values["years"])), f"{values['events']:,}", values["positives"] )
    for name, values in m["splits"].items()])
paragraph("One-hot encoding was fitted on training events. Models were selected by validation average precision and thresholds maximize positive-class F1 in the validation set. The prior baseline predicts a constant training prevalence. The baseline’s selected threshold predicts every event positive, making its accuracy a poor ranking comparison. The test was reserved for final evaluation.")
table(["Model", "AP", "ROC AUC", "Brier", "Accuracy", "Macro F1"], [
    (name, *[f"{scores[k]:.3f}" for k in ("average_precision", "roc_auc", "brier", "accuracy", "macro_f1")])
    for name, scores in m["test"].items()])
figure("model_evaluation", "Figure 3. Precision–recall and quantile-bin calibration on 2022–2025. Average precision emphasizes the positive class. Lower Brier scores indicate smaller squared probability errors.")
positive = model["by_class"]["1"]
ci = m["selected_test_ci"]["average_precision"]
paragraph(f"The selected model has {positive['precision']:.0%} positive precision and {positive['recall']:.1%} recall. "
          f"The confusion matrix is {model['confusion']}, ordered lower then high mortality. The class-stratified 95% bootstrap interval "
          f"for average precision is {ci[0]:.3f}–{ci[1]:.3f}. This is a retrospective association among eligible records. "
          "The recall and label selection limit operational use.")

page("Explaining fitted mortality scores")
paragraph(f"SHAP used {shap['events']} randomly sampled held-out events with a training-only background of 256 rows. Independent-masker "
          "linear explanations use the fitted log-odds scale. One-hot contributions sum to the original input group. "
          f"The maximum reconstruction error was {shap['max_additivity_error']:.2g}.")
figure("shap_global", "Figure 4. Mean absolute SHAP contribution after summing dummy-column effects by input group.", 6.1)
figure("shap_hazard", "Figure 5. Signed hazard contribution by held-out type where at least 12 sampled events were available.", 6.1)
paragraph("Hazard has the largest grouped mean absolute contribution, followed by region and month. Epidemic and earthquake show positive mean hazard-group contributions in this sample. The saved beeswarm shows encoded-category effects, and the local waterfall shows how contributions move a selected case from baseline log-odds to the fitted score. Correlated input groups and one-hot encoding affect how attributions are allocated. These values describe the fitted model.")

page("Impact profiles and anomaly review")
paragraph(f"We retained {profiles['complete_events']:,} of {profiles['recent_events']:,} events in 2000–2025 with all three losses "
          "reported by every contributing country. Log transformation and standardization give each impact comparable numeric scale. "
          "The representation uses the observed outcome measures directly, so these plots are descriptive. Hazard colors were added after fitting.")
figure("impact_embeddings", "Figure 6. PCA, t-SNE and UMAP of standardized log impacts. T15 measures preservation of local neighbors.")
ratio = profiles["explained_variance_ratio"]
paragraph(f"PC1 and PC2 explain {sum(ratio[:2]):.1%} of variance. PC1 loads positively on all three losses, with strongest loading on "
          "deaths. PC2 emphasizes damage relative to human impacts. At 15 neighbors, trustworthiness is 0.928 for PCA, 0.995 "
          "for t-SNE and 0.978 for UMAP. Changing settings and seed retained 79.7% of t-SNE neighbor sets and 61.0% for UMAP. "
          "The settings distinguish perplexity 30 vs 50 and UMAP neighborhoods 25 vs 45 with minimum distances 0.15 vs 0.35.")
paragraph("K-means tested k from 2 to 8 in standardized impact space. The best silhouette selected k = 2 (0.327) with a median "
          "subsample adjusted Rand index of 0.991. The groups contained 681 and 1,140 events with medians of 62 and 6 deaths, "
          "350,000 and 4,029 affected, and 460 and 69 million USD adjusted damage. DBSCAN yielded one dense group plus noise at all three settings. "
          "The plots and diagnostics support an exploratory impact gradient. Isolation Forest flagged 19 events in the top score percentile for inspection.")

page("Integrated dashboard and geography")
figure("dashboard_overview", "Figure 7. Actual Chromium capture of the dashboard overview. The reporting counts are displayed underneath the loss metrics.", 6.35)
paragraph("The dashboard shares year, hazard, region and country filters across its four views. Overview shows the filtered event count and reported loss totals. Frequency vs impact exposes total, mean and median for each loss measure. Trends shows composition, losses and reporting periods. Geography joins country records to Natural Earth boundaries by ISO code.")
paragraph(f"The map matches {geo['matched_records']:,} of {geo['total_records']:,} country-impact rows to {geo['matched_country_codes']} codes. "
          f"The other {geo['unmatched_country_codes']} codes remain in tables. Contemporary 1:110m boundaries omit some small territories "
          "and historical entities. No synthetic point coordinates are assigned. The countries with the highest recorded counts in this "
          "snapshot are the USA, China and India. Those counts are conditional on recording and are unadjusted for exposure.")
paragraph("The browser dashboard was tested at localhost. The Power BI handover supplies M queries, DAX, a theme and model guidance. "
          "Native PBIX assembly and refresh require a Windows Power BI authoring environment.")

page("Discussion limitations and conclusion")
sub("What the question resolves")
paragraph("The most frequent hazard does lead one accumulated burden, affected population. It does not lead all impact measures, and different hazards lead typical or average losses. The cost rankings also change with capping and the study window. A single frequency ranking therefore leaves important differences in human and economic impact unreported.")
sub("External validity and ethics")
paragraph("EM-DAT thresholds and reporting changes limit comparisons over time. Historical extremes, repeated impacts on the same people, broad hazard labels and the sparse recent loss data affect interpretation. Documented events reflect both occurrence and detection. The mortality cohort omits multi-country events and unknown outcomes. The profile cohort selects for complete loss reporting.")
paragraph("The public current tree contains executable code and aggregated analysis. Authorized users obtain the workbook from EM-DAT "
          "and regenerate the local tables. Earlier public commits contain the workbook and derived CSVs. Git history is preserved. "
          "The contribution record identifies prior commit evidence and technical work generated by Codex. Institutional disclosure "
          "and teammate acceptance require human review.")
sub("Follow-up work")
paragraph("An exposure-normalized study would need a documented population or economic denominator at suitable grain. Missingness "
          "sensitivity could use defensible bounds or external validation against independent loss records. A second export would "
          "allow a stronger test of reporting drift, and a verified native Power BI build could be compared with the browser implementation.")
sub("Reproduction and acceptance")
paragraph("Use Python 3.11 and the pinned requirements. The repository README walks through source verification, the four-table rebuild, "
          "validation, analytics, dashboard and tests. Code, figures and metric evidence live in src and results. The literature matrix "
          "and contribution record live in docs. See the submission checklist for review items and the QA record for actual checks.")

for offset in (0, 8):
    page("References" if offset == 0 else "References continued")
    for number, citation in reference_rows[offset:offset+8]:
        citation = re.sub(r'\[([^]]+)\]\(([^)]+)\)', r'\2', citation).replace('*', '')
        document.add_paragraph(f"{number} {citation}")
    if offset:
        sub("Data attribution")
        paragraph("EM-DAT, CRED / UCLouvain, Brussels, Belgium. https://www.emdat.be. Custom-request snapshot dated 2026-10-23. "
                  "Natural Earth admin 0 country vectors, public domain.")

SUBMISSION.mkdir(exist_ok=True)
document.save(SUBMISSION / "final_report.docx")
