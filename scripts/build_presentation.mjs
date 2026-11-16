import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const library = process.env.ARTIFACT_TOOL_ENTRY;
const { Presentation, PresentationFile } = await import(library ? pathToFileURL(library).href : '@oai/artifact-tool');
const output = path.join(root, 'submission');
const pictures = path.join(root, 'results', 'figures');
const get = async (name) => JSON.parse(await fs.readFile(path.join(root, 'results', name)));
const [findings, models, shap, profile, geo] = await Promise.all([
  get('findings.json'), get('model_metrics.json'), get('shap_summary.json'),
  get('profile_summary.json'), get('map_summary.json'),
]);

const deck = Presentation.create({ slideSize: { width: 1280, height: 720 } });
const ink = '#182942';
const teal = '#087F80';
const light = '#EFF5F6';
const muted = '#475972';
const white = '#FFFFFF';
const font = 'Aptos';
const emdat = 'EM-DAT data, 2026 · www.emdat.be · CRED / UCLouvain · export dated 23 Oct 2026';
const fmt = value => Number(value).toLocaleString('en-US');

function text(slide, id, value, x, y, w, h, { size = 30, color = ink, bold = false } = {}) {
  const box = slide.shapes.add({
    name: id, geometry: 'textbox', position: { left: x, top: y, width: w, height: h },
    fill: 'none', line: { fill: 'none', width: 0 },
  });
  box.text = value;
  box.text.style = { fontFamily: font, fontSize: size, bold, color, autoFit: 'none',
    insets: { top: 0, bottom: 0, left: 0, right: 0 }, verticalAlignment: 'middle' };
}

function slide(title, notes, source = emdat) {
  const page = deck.slides.add();
  page.background.fill = white;
  page.speakerNotes.text = notes + '\n\nSource: ' + source;
  text(page, 'title', title, 60, 43, 1160, 77, { size: 43, bold: true });
  text(page, 'source', source, 60, 659, 1110, 28, { size: 15, color: muted });
  text(page, 'page-number', String(deck.slides.items.length).padStart(2, '0'), 1180, 659, 42, 28,
    { size: 15, color: muted });
  return page;
}

function body(page, items, x = 60, width = 1160, top = 149) {
  let y = top;
  for (const [lead, content] of items) {
    text(page, 'label-' + y, lead, x, y, width, 38, { color: teal, size: 27, bold: true });
    text(page, 'detail-' + y, content, x, y + 42, width, 69, { size: 25 });
    y += 124;
  }
}

async function graphic(page, name, x = 60, y = 125, w = 1160, h = 505) {
  const data = await fs.readFile(path.join(pictures, name + '.png'));
  const width = data.readUInt32BE(16);
  const height = data.readUInt32BE(20);
  const scale = Math.min(w / width, h / height);
  const size = { width: width * scale, height: height * scale };
  page.images.add({ blob: new Uint8Array(data), contentType: 'image/png', alt: name.replaceAll('_', ' '),
    position: { left: x + (w - size.width) / 2, top: y + (h - size.height) / 2, ...size } });
}

const cover = deck.slides.add();
cover.background.fill = ink;
cover.speakerNotes.text = 'Introduce the project team and ask the audience to think of a hazard that occurs frequently and a separate event they remember for its losses. Explain that the study uses reported impacts from EM-DAT. Technical draft for team and faculty review.';
text(cover, 'title', 'When Nature Strikes', 66, 100, 1145, 122, { color: white, size: 78, bold: true });
text(cover, 'subtitle', 'A Visualization Approach to Determine\nthe Impact of Natural Disasters', 70, 242, 1090, 136,
  { color: '#B9E0E0', size: 48 });
text(cover, 'authors', 'Samarth Ramesha, Shashank S K,\nShreya Patil and Shreya S Mattimadu', 72, 490, 1070, 82,
  { color: white, size: 27 });
text(cover, 'programme', 'Undergraduate Computer Science Engineering project', 72, 626, 1100, 35,
  { color: '#B9E0E0', size: 18 });

body(slide('Are frequent hazards also the most destructive?', 'Ask the main research question exactly. Separate how often something occurs from the losses it accumulates and the typical severity when impact is reported.'), [
  ['Occurrence', 'How many distinct events does EM-DAT record for each primary hazard?'],
  ['Accumulated burden', 'Which hazards account for the most reported deaths, affected people or adjusted damage?'],
  ['Per-event severity', 'Does the ranking change when we use the mean or median among reporting events?'],
]);

body(slide('Country records feed a distinct-event analysis', 'Explain how a cross-border storm can appear once in the events table and multiple times in the country-impact table. Use full event IDs only after removing country suffixes. Unknown impacts stay blank.'), [
  [fmt(findings.impacts) + ' country-impact records', 'Natural hazards in the 1900–2026 export, with 2026 partial.'],
  [fmt(findings.events) + ' unique events', '1,067 events span more than one country. Geography filters select contributions before aggregation.'],
  ['Three reported consequences', 'Deaths, affected population and inflation-adjusted damage in million USD.'],
]);

const frequency = slide('Floods were the most frequently recorded hazard', 'Point to the distinct event counts. Four hazard classes account for most events. Several classes are extremely sparse, which affects the precision of summary ranks.');
const top = Object.entries(findings.type_counts).slice(0, 5).reverse();
frequency.charts.add('bar', {
  position: { left: 75, top: 136, width: 1118, height: 485 },
  title: 'Distinct recorded events among the five most frequent hazards',
  categories: top.map(([label]) => label),
  series: [{ name: 'Distinct events', values: top.map(([, count]) => count), fill: teal }],
  barOptions: { direction: 'bar', grouping: 'clustered', gapWidth: 65 },
  hasLegend: false,
  dataLabels: { showValue: true, position: 'outEnd' },
});

const ranking = slide('The impact ranking depends on the measure',
  'Floods lead total affected population. Storms lead total adjusted damage. Earthquakes lead average adjusted damage. Drought leads historical mortality when the singleton Fog ranking is interpreted in context.');
await graphic(ranking, 'frequency_vs_impact', 53, 124, 770, 522);
body(ranking, [
  ['Flood', 'Most events and highest total affected population'],
  ['Storm', 'Highest total adjusted damage'],
  ['Earthquake', 'Highest mean adjusted damage'],
], 880, 332, 154);
await graphic(slide('Totals track frequency more closely than medians', 'The dots show rank associations across 13–14 hazards per full-window metric. Intervals resample the available hazard pairs as a sensitivity exercise. Reported totals combine the number of reporting events with mean severity. Per-event rankings have weaker associations.'),
  'spearman_intervals');
await graphic(slide('Reporting changes across eras', 'Point out that the open marker is partial 2026, with 153 events and just one event reporting adjusted damage. Coverage changes and historical record quality prevent interpreting the shape as a hazard occurrence trend.'), 'annual_trends');

body(slide('The mortality model uses a later test period', 'Only single-country events with reported deaths enter the model cohort. A positive label is at least 100 deaths. Hazard, region and start month are the only predictors. Split at event level and fit one-hot encoding on training only.'), [
  ['Model question', 'How well can basic event metadata rank reported mortality of 100 deaths or more?'],
  ['Time split', '2000–2017 train, 2018–2021 validate, 2022–2025 test.'],
  ['Model choice', 'Validation average precision selected logistic regression over random forest.'],
]);

const selected = models.test[models.selected];
await graphic(slide('Basic metadata provided limited mortality signal',
  'Average precision is 0.288 versus 0.116 for the constant prior. ROC AUC was 0.709. At the fixed validation threshold, 34 of 97 positive cases were detected, with 66 false positives. Limited recall and selection on reporting constrain use.'), 'model_evaluation', 60, 124, 1160, 480);
text(deck.slides.items.at(-1), 'ap', 'Test AP ' + selected.average_precision.toFixed(3) + '  ·  ROC AUC ' +
  selected.roc_auc.toFixed(3) + '  ·  34 of 97 high-mortality events detected', 60, 602, 1160, 40,
  { size: 25, bold: true, color: teal });

const explanation = slide('Hazard type contributed most to fitted scores',
  'Explain the additive log-odds scale. Contributions were grouped from individual one-hot columns. This reveals model behavior, with no causal interpretation. The background was sampled from training and the explanation sample from held-out test data.',
  'EM-DAT data, 2026 · www.emdat.be · Lundberg and Lee (2017)');
await graphic(explanation, 'shap_global', 55, 130, 575, 410);
await graphic(explanation, 'shap_local', 657, 130, 575, 410);
text(explanation, 'context', fmt(shap.events) + ' held-out cases  ·  Grouped global importance and one local log-odds explanation',
  60, 571, 1155, 54, { size: 24, color: teal, bold: true });

const projections = slide('Impact profiles show local structure',
  'All three projections use the same complete-case sample and standardized log1p features. t-SNE and UMAP prioritize neighbors at the expense of global distances. The split between common points can depend on parameters. The model target is deliberately not displayed as a predictive label.',
  'EM-DAT data, 2026 · www.emdat.be · Jolliffe and Cadima (2016) · van der Maaten and Hinton (2008) · McInnes et al. (2018)');
await graphic(projections, 'impact_embeddings', 50, 128, 1170, 420);
text(projections, 'context', fmt(profile.complete_events) + ' fully reporting events  ·  First two PCs explain ' +
  (100 * profile.explained_variance_ratio.slice(0, 2).reduce((a, b) => a + b, 0)).toFixed(1) + '% of variance',
  60, 572, 1155, 55, { size: 24, color: teal, bold: true });

await graphic(slide('Clustering found a modest severity gradient',
  'The k-means k=2 solution had the highest silhouette among k=2–8 (0.327) and a subsample median ARI of 0.991. DBSCAN yielded one group plus noise. Isolation Forest flagged 19 profiles for review. The clusters summarize patterns within complete cases.'), 'clusters_and_anomalies');

const dashboard = slide('Four views share the same filters', 'Open the live local dashboard after this slide. Start at Overview. Toggle total, mean and median on Frequency vs impact. Keep one hazard filter selected as you switch pages. The screenshot was captured from the running app.');
await graphic(dashboard, 'dashboard_overview', 59, 130, 794, 511);
body(dashboard, [
  ['Overview and comparisons', 'Counts, losses and reporting coverage'],
  ['Trends and geography', 'Annual composition and ISO-based country comparisons'],
  ['Shared scope', 'Year, hazard, region and country'],
], 874, 340, 150);

const geography = slide('Country rankings retain unmapped territories', 'The map joins ISO codes to Natural Earth boundaries. Explain why historical territories or small islands may lack polygons. Counts are distinct within country and cannot be added to obtain a global event total.', 'EM-DAT data, 2026 · www.emdat.be · Natural Earth 1:110m Admin 0 countries');
await graphic(geography, 'geography', 55, 129, 1168, 462);
text(geography, 'coverage', fmt(geo.matched_records) + ' of ' + fmt(geo.total_records) + ' country-impact records mapped by ISO',
  60, 585, 1155, 48, { size: 25, color: teal, bold: true });

body(slide('Frequency answers only part of the question', 'Recap that the choice between totals and per-event summaries depends on the decision. Discuss uneven reporting, the partial year, and the complete-case profile selection. Invite the panel to check the live dashboard and the reproducible evidence.'), [
  ['Floods lead frequency and total affected population', 'Storms lead total adjusted damage. Earthquakes lead mean adjusted damage.'],
  ['Mortality rankings depend on the time window', 'Drought leads historical total deaths. Earthquake leads total deaths in 2000–2025.'],
  ['Every impact value needs a reporting denominator', 'Only 33.4% of historical events report adjusted damage.'],
]);

body(slide('Sources and contribution record', 'Reference the full literature matrix in the report and repository. Explain that the history records data preparation and EDA, and that Codex assisted in the technical takeover, advanced analysis, dashboard and final artifacts. Team and institutional acceptance are separate human steps.', 'See docs/LITERATURE_REVIEW.md and docs/TEAM_CONTRIBUTIONS.md'), [
  ['Disaster records', 'EM-DAT (Delforge et al., 2025) and its missingness study (Jones et al., 2022)'],
  ['Methods', 'Lundberg and Lee, Jolliffe and Cadima, van der Maaten and Hinton, McInnes et al.'],
  ['Evidence of work', 'Git history for the original pipeline and EDA. Codex assistance documented in the audit.'],
]);

const filename = path.join(output, 'final_presentation.pptx');
const blob = await PresentationFile.exportPptx(deck);
await blob.save(filename);
console.log('Exported', deck.slides.items.length, 'slides to', filename);
