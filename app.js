// Comeback Thermometer site. Reads data/latest.json (copied from the daily export) and
// never calls AWS. Titles come from YouTube, so they are always set with textContent.
"use strict";

const TEXT = {
  en: {
    title: "Comeback Thermometer",
    question: "How strong is each new TWICE, NMIXX or tripleS launch at day 1, 7 and 28, compared with the same artist's earlier launches in the same market?",
    asof: "Data as of",
    tab_explore: "Explore an artist",
    tab_compare: "Compare two",
    artist: "Artist or family",
    versus: "Compared with",
    market: "Market",
    all_markets: "All",
    kr: "Korea",
    jp: "Japan",
    family: "{name} · everyone (group, units, soloists)",
    family_short: "{name} (all)",
    unit: "unit",
    solo: "solo",
    group: "group",
    kind_group: "Group",
    kind_unit: "Unit",
    kind_solo: "Soloist",
    measured_ring: "Measured from day 1",
    tile_releases: "Releases tracked",
    tile_measured: "Measured from day 1",
    tile_latest: "Latest release",
    tile_best7: "Best day 7",
    tile_recent: "Releases in the last 12 months",
    tile_median7: "Median views at day 7",
    none_yet: "none yet",
    timeline_title: "Release timeline",
    timeline_note: "Each dot is a release, placed by its date and its views to date (log scale). Views to date always favour older videos: this shows the release history, not how strong a launch was.",
    curves_title: "Launch curves",
    curves_note_some: "Views at day 1, 7 and 28 for every launch measured from day 1.",
    curves_note_none: "No launch in this selection has been measured from day 1 yet. Tracking began on {date}; the next release will draw the first curve here.",
    curves_empty: "No launch measured from day 1 yet",
    day: "Day {n}",
    ranked_title: "Launches measured from day 1",
    ranked_note_some: "Each rank compares a launch with the same artist's other launches in the same market. Views are cumulative YouTube views on each day after release.",
    ranked_note_none: "Nothing in this selection was released after tracking began on {date}.",
    earlier_title: "Earlier releases (not comparable)",
    earlier_note: "Released before tracking began, so their first days were never observed. Shown with views to date only.",
    earlier_summary: "Show {n} earlier releases",
    col_video: "Video",
    col_released: "Released",
    col_d1: "Day 1",
    col_d7: "Day 7",
    col_d28: "Day 28",
    col_age: "Age (days)",
    col_views: "Views to date",
    col_year: "Year",
    rank: "#{rank} of {of}",
    pending: "in {days} d",
    missing: "missed",
    visual_clip: "visual clip",
    empty_earlier: "None.",
    views: "{v} views",
    released_on: "Released {date}",
    lastfm_title: "Last.fm",
    listeners: "Listeners",
    scrobbles: "Scrobbles",
    change: "{sign}{value} since the previous snapshot",
    lastfm_none: "Not tracked on Last.fm for this artist.",
    lastfm_family: "Last.fm is shown per artist: listeners can't be added up across a family, because the same fans listen to several of its artists.",
    peryear_title: "Releases per year",
    peryear_note: "How often each one releases. A bigger family releases more, so this is about rhythm, not strength.",
    overlay_title: "Release timelines side by side",
    as_table: "Show as a table",
    count: "{n} releases",
    compare_caveat: "Launch strength can only be compared once both have launches measured from day 1.",
    scope_title: "What it is and what it isn't",
    scope: [
      "It measures attention on YouTube and Last.fm, not sales, chart positions or streams on other platforms.",
      "Day-N values exist only for videos released after tracking began. Older videos are shown but not ranked.",
      "A launch is ranked only against the same artist in the same market: a Japanese MV or a solo debut is never measured against a TWICE title track. Families and comparisons group artists for reading, not for ranking.",
      "The market comes from the channel and the title: a Japanese-language song uploaded to a Korean channel with a plain title counts as Korea.",
      "Last.fm users skew toward Western listeners; Korean domestic listening is under-represented.",
      "It keeps YouTube view counts longer than the 30 days YouTube's developer policies allow for public data, and ranks them. That is accepted for this non-commercial course project; a commercial client would need YouTube's approval.",
      "This page is a dated snapshot, refreshed by hand from the daily pipeline, not live.",
    ],
    footer_data: "Built from a daily batch pipeline on AWS. This page only reads a dated JSON file.",
    footer_repo: "Source code",
    footer_sources: "Data:",
    footer_youtube: "titles, views; each title links to its video",
    lastfm_link: "{name} on Last.fm",
    switch_to: "Español",
    chart_timeline: "Release timeline chart",
    chart_curves: "Launch curves chart",
    chart_peryear: "Releases per year chart",
  },
  es: {
    title: "Termómetro de comebacks",
    question: "¿Qué tan fuerte es cada nuevo lanzamiento de TWICE, NMIXX o tripleS al día 1, 7 y 28, comparado con los lanzamientos anteriores del mismo artista en el mismo mercado?",
    asof: "Datos al",
    tab_explore: "Explorar un artista",
    tab_compare: "Comparar dos",
    artist: "Artista o familia",
    versus: "Comparado con",
    market: "Mercado",
    all_markets: "Todos",
    kr: "Corea",
    jp: "Japón",
    family: "{name} · todos (grupo, unidades, solistas)",
    family_short: "{name} (todos)",
    unit: "unidad",
    solo: "solista",
    group: "grupo",
    kind_group: "Grupo",
    kind_unit: "Unidad",
    kind_solo: "Solista",
    measured_ring: "Medido desde el día 1",
    tile_releases: "Lanzamientos registrados",
    tile_measured: "Medidos desde el día 1",
    tile_latest: "Último lanzamiento",
    tile_best7: "Mejor día 7",
    tile_recent: "Lanzamientos en los últimos 12 meses",
    tile_median7: "Mediana de vistas al día 7",
    none_yet: "aún ninguno",
    timeline_title: "Cronología de lanzamientos",
    timeline_note: "Cada punto es un lanzamiento, ubicado por su fecha y sus vistas a la fecha (escala logarítmica). Las vistas a la fecha siempre favorecen a los videos viejos: esto muestra la historia de lanzamientos, no qué tan fuerte arrancó cada uno.",
    curves_title: "Curvas de lanzamiento",
    curves_note_some: "Vistas al día 1, 7 y 28 de cada lanzamiento medido desde el día 1.",
    curves_note_none: "Nada en esta selección se ha medido desde el día 1 todavía. El seguimiento empezó el {date}; el próximo lanzamiento dibujará aquí la primera curva.",
    curves_empty: "Aún no hay lanzamientos medidos desde el día 1",
    day: "Día {n}",
    ranked_title: "Lanzamientos medidos desde el día 1",
    ranked_note_some: "Cada ranking compara un lanzamiento con los demás del mismo artista en el mismo mercado. Las vistas son acumuladas en YouTube a cada día del lanzamiento.",
    ranked_note_none: "Nada en esta selección se lanzó después de que empezó el seguimiento el {date}.",
    earlier_title: "Lanzamientos anteriores (no comparables)",
    earlier_note: "Salieron antes de que empezara el seguimiento, así que sus primeros días no se observaron. Solo se muestran las vistas a la fecha.",
    earlier_summary: "Ver {n} lanzamientos anteriores",
    col_video: "Video",
    col_released: "Lanzamiento",
    col_d1: "Día 1",
    col_d7: "Día 7",
    col_d28: "Día 28",
    col_age: "Edad (días)",
    col_views: "Vistas a la fecha",
    col_year: "Año",
    rank: "#{rank} de {of}",
    pending: "en {days} d",
    missing: "sin dato",
    visual_clip: "visual clip",
    empty_earlier: "Ninguno.",
    views: "{v} vistas",
    released_on: "Lanzado el {date}",
    lastfm_title: "Last.fm",
    listeners: "Oyentes",
    scrobbles: "Reproducciones",
    change: "{sign}{value} desde la foto anterior",
    lastfm_none: "Este artista no se mide en Last.fm.",
    lastfm_family: "Last.fm se muestra por artista: los oyentes no se pueden sumar dentro de una familia, porque los mismos fans escuchan a varios de sus artistas.",
    peryear_title: "Lanzamientos por año",
    peryear_note: "Qué tan seguido lanza cada uno. Una familia más grande lanza más, así que esto habla de ritmo, no de fuerza.",
    overlay_title: "Cronologías lado a lado",
    as_table: "Ver como tabla",
    count: "{n} lanzamientos",
    compare_caveat: "La fuerza de los lanzamientos solo se puede comparar cuando ambos tengan lanzamientos medidos desde el día 1.",
    scope_title: "Lo que sí es y lo que no",
    scope: [
      "Mide atención en YouTube y Last.fm, no ventas, posiciones en charts ni streams en otras plataformas.",
      "Los valores al día N solo existen para videos publicados después de que empezó el seguimiento. Los anteriores se muestran, pero no se comparan.",
      "Un lanzamiento solo se compara con el mismo artista en el mismo mercado: un MV japonés o un debut en solitario nunca se mide contra un sencillo principal de TWICE. Las familias y las comparaciones agrupan artistas para leer, no para el ranking.",
      "El mercado sale del canal y del título: una canción en japonés subida a un canal coreano con un título sin caracteres japoneses cuenta como Corea.",
      "Los usuarios de Last.fm son sobre todo occidentales; el consumo en Corea está subrepresentado.",
      "Guarda las vistas de YouTube más allá de los 30 días que permiten sus políticas para desarrolladores con datos públicos, y las compara entre sí. Se acepta en este proyecto académico sin fines comerciales; un cliente comercial necesitaría la aprobación de YouTube.",
      "Esta página es un corte fechado que se actualiza a mano desde el pipeline diario, no en vivo.",
    ],
    footer_data: "Construido con un pipeline batch diario en AWS. Esta página solo lee un archivo JSON fechado.",
    footer_repo: "Código fuente",
    footer_sources: "Datos:",
    footer_youtube: "títulos y vistas; cada título enlaza a su video",
    lastfm_link: "{name} en Last.fm",
    switch_to: "English",
    chart_timeline: "Gráfica de cronología de lanzamientos",
    chart_curves: "Gráfica de curvas de lanzamiento",
    chart_peryear: "Gráfica de lanzamientos por año",
  },
};

// Validated categorical palette (dark surface, all pairs): derived from the design system's
// lavender, peach and mint hues. Shape is the second encoding, so colour never works alone.
const KIND_STYLE = {
  group: { color: "#9074E9", shape: "circle" },
  unit: { color: "#D97230", shape: "square" },
  solo: { color: "#35AA76", shape: "diamond" },
};
const SIDE_STYLE = [
  { color: "#9074E9", shape: "circle" },
  { color: "#D97230", shape: "square" },
];

const state = {
  lang: pickLanguage(), data: null, view: "explore", a: null, b: null, market: "all",
};

function pickLanguage() {
  const fromUrl = new URLSearchParams(location.search).get("lang");
  const chosen = fromUrl || localStorage.getItem("lang") || (navigator.language || "en").slice(0, 2);
  return chosen === "es" ? "es" : "en";
}

const t = (key, vars = {}) => String(TEXT[state.lang][key]).replace(/\{(\w+)\}/g, (_, n) => vars[n] ?? "");
const fmtNumber = (n) => new Intl.NumberFormat(state.lang).format(n);
const fmtCompact = (n) => new Intl.NumberFormat(state.lang, { notation: "compact", maximumFractionDigits: 1 }).format(n);
const fmtDate = (iso) =>
  new Intl.DateTimeFormat(state.lang, { year: "numeric", month: "short", day: "numeric", timeZone: "UTC" })
    .format(new Date(iso.length === 10 ? `${iso}T00:00:00Z` : iso));
const daysBetween = (from, to) => Math.round((Date.parse(to.slice(0, 10)) - Date.parse(from.slice(0, 10))) / 86400000);
const median = (xs) => {
  if (!xs.length) return null;
  const s = [...xs].sort((a, b) => a - b), m = Math.floor(s.length / 2);
  return s.length % 2 ? s[m] : Math.round((s[m - 1] + s[m]) / 2);
};

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") node.className = v;
    else node.setAttribute(k, v);
  }
  for (const child of children) if (child !== null && child !== undefined) node.append(child);
  return node;
}

// ---- entities: one artist, or a whole family (a group with its units and soloists) ----
const artistBySlug = () => Object.fromEntries(state.data.artists.map((a) => [a.slug, a]));

function entities() {
  const withVideos = new Set(state.data.videos.map((v) => v.artist));
  const artists = state.data.artists.filter((a) => withVideos.has(a.slug));
  return artists.filter((a) => a.parent === null).map((group) => {
    const children = artists.filter((a) => a.parent === group.slug);
    return { group, children };
  });
}

function members(entity) {
  const [kind, slug] = entity.split(":");
  if (kind === "artist") return [slug];
  return [slug, ...state.data.artists.filter((a) => a.parent === slug).map((a) => a.slug)];
}

function entityName(entity, short = false) {
  const [kind, slug] = entity.split(":");
  const name = artistBySlug()[slug].name;
  return kind === "family" ? t(short ? "family_short" : "family", { name }) : name;
}

function videosOf(entity) {
  const slugs = new Set(members(entity));
  return state.data.videos.filter((v) => slugs.has(v.artist) && !v.is_duplicate
    && (state.market === "all" || v.market === state.market));
}

function kindOf(slug) { return artistBySlug()[slug].kind; }

function meta(video) {
  const parts = [artistBySlug()[video.artist].name, t(video.market)];
  if (video.video_type === "visual_clip") parts.push(t("visual_clip"));
  return parts.join(" · ");
}

function tooltipLines(video) {
  return [video.title, meta(video), t("released_on", { date: fmtDate(video.published_at) }), t("views", { v: fmtNumber(video.views_latest) })];
}

// ---- controls ----------------------------------------------------------------
function fillPicker(select, value) {
  select.replaceChildren(...entities().map(({ group, children }) => {
    const options = [];
    if (children.length) options.push(el("option", { value: `family:${group.slug}` }, t("family", { name: group.name })));
    options.push(el("option", { value: `artist:${group.slug}` }, group.name));
    for (const c of children) options.push(el("option", { value: `artist:${c.slug}` }, `${c.name} (${t(c.kind)})`));
    return el("optgroup", { label: group.name }, ...options);
  }));
  select.value = value;
}

function renderControls() {
  fillPicker(document.getElementById("pick-a"), state.a);
  fillPicker(document.getElementById("pick-b"), state.b);
  document.getElementById("pick-b-wrap").hidden = state.view !== "compare";
  for (const tab of document.querySelectorAll("[role=tab]")) {
    const active = tab.id === `tab-${state.view}`;
    tab.setAttribute("aria-selected", String(active));
    document.getElementById(tab.getAttribute("aria-controls")).hidden = !active;
  }
  for (const button of document.querySelectorAll("[data-market]")) {
    button.setAttribute("aria-checked", String(button.dataset.market === state.market));
  }
}

function renderStaticText() {
  document.documentElement.lang = state.lang;
  document.title = t("title");
  for (const node of document.querySelectorAll("[data-i18n]")) node.textContent = t(node.dataset.i18n);
  const lang = document.getElementById("lang");
  lang.textContent = state.lang === "en" ? "ES" : "EN";
  lang.setAttribute("aria-label", t("switch_to"));
  document.getElementById("scope").replaceChildren(...TEXT[state.lang].scope.map((line) => el("li", {}, line)));
  if (state.data) document.getElementById("snapshot-date").textContent = fmtDate(state.data.snapshot_date);
}

// ---- explore view ------------------------------------------------------------
function tile(label, value, sub) {
  return el("div", { class: "tile" }, el("p", { class: "tile-label" }, label), el("p", { class: "tile-value" }, value),
    sub ? el("p", { class: "tile-sub" }, sub) : null);
}

function renderTiles(videos) {
  const measured = videos.filter((v) => v.comparable);
  const latest = [...videos].sort((a, b) => b.published_at.localeCompare(a.published_at))[0];
  const best = [...measured].filter((v) => v.views_d7 !== null).sort((a, b) => b.views_d7 - a.views_d7)[0];
  document.getElementById("tiles").replaceChildren(
    tile(t("tile_releases"), fmtNumber(videos.length)),
    tile(t("tile_measured"), fmtNumber(measured.length)),
    tile(t("tile_latest"), latest ? fmtDate(latest.published_at) : "—", latest ? latest.title : null),
    tile(t("tile_best7"), best ? fmtCompact(best.views_d7) : t("none_yet"), best ? best.title : null),
  );
}

function kindLegend(list, videos, withRing) {
  const kinds = ["group", "unit", "solo"].filter((k) => videos.some((v) => kindOf(v.artist) === k));
  const items = kinds.map((k) => ({ label: t(`kind_${k}`), ...KIND_STYLE[k] }));
  if (withRing && videos.some((v) => v.comparable)) items.push({ label: t("measured_ring"), ring: true });
  Charts.legend(list, items);
}

function renderTimeline(videos) {
  kindLegend(document.getElementById("timeline-legend"), videos, true);
  Charts.timeline(document.getElementById("timeline"), videos.map((v) => ({
    date: Date.parse(v.published_at), value: v.views_latest, highlight: v.comparable,
    ...KIND_STYLE[kindOf(v.artist)], tooltip: tooltipLines(v),
  })), { label: t("chart_timeline"), empty: "—", formatAxis: fmtCompact });
}

function renderCurves(videos) {
  const measured = videos.filter((v) => v.comparable);
  document.getElementById("curves-note").textContent = measured.length
    ? t("curves_note_some") : t("curves_note_none", { date: fmtDate(state.data.first_snapshot_date || state.data.snapshot_date) });
  kindLegend(document.getElementById("curves-legend"), measured, false);
  Charts.curves(document.getElementById("curves"), measured.map((v) => ({
    ...KIND_STYLE[kindOf(v.artist)],
    points: [1, 7, 28].filter((n) => v[`views_d${n}`] !== null).map((n) => ({
      day: n, value: v[`views_d${n}`], tooltip: [v.title, meta(v), `${t("day", { n })}: ${fmtNumber(v[`views_d${n}`])}`],
    })),
  })), { label: t("chart_curves"), empty: t("curves_empty"), formatAxis: fmtCompact, dayLabel: (n) => t("day", { n }) });
}

function videoCell(video) {
  const link = el("a", { href: `https://www.youtube.com/watch?v=${encodeURIComponent(video.video_id)}`, rel: "noopener" }, video.title);
  return el("td", {}, link, el("span", { class: "meta" }, meta(video)));
}

function dayCell(video, n, age) {
  const views = video[`views_d${n}`];
  const cell = el("td", { class: "num" });
  if (views === null) {
    cell.append(age < n ? t("pending", { days: n - age }) : t("missing"));
    return cell;
  }
  cell.append(fmtNumber(views));
  const rank = video[`rank_d${n}`];
  if (rank !== null) {
    cell.append(el("span", { class: rank === 1 ? "rank rank-first" : "rank" }, t("rank", { rank, of: video[`compared_d${n}`] })));
  }
  return cell;
}

function renderTables(videos) {
  const snapshot = state.data.snapshot_date;
  const byDate = (a, b) => b.published_at.localeCompare(a.published_at);
  const ranked = videos.filter((v) => v.comparable).sort(byDate);
  const earlier = videos.filter((v) => !v.comparable).sort(byDate);

  document.getElementById("ranked-note").textContent = ranked.length
    ? t("ranked_note_some") : t("ranked_note_none", { date: fmtDate(state.data.first_snapshot_date || snapshot) });
  document.querySelector("#ranked tbody").replaceChildren(...(ranked.length
    ? ranked.map((v) => {
      const age = daysBetween(v.published_at, snapshot);
      return el("tr", {}, videoCell(v), el("td", {}, fmtDate(v.published_at)), ...[1, 7, 28].map((n) => dayCell(v, n, age)));
    })
    : [el("tr", {}, el("td", { class: "empty", colspan: "5" }, "—"))]));

  document.getElementById("earlier-summary").textContent = t("earlier_summary", { n: earlier.length });
  document.querySelector("#earlier tbody").replaceChildren(...(earlier.length
    ? earlier.map((v) => el("tr", {}, videoCell(v), el("td", {}, fmtDate(v.published_at)),
      el("td", { class: "num" }, fmtNumber(daysBetween(v.published_at, snapshot))),
      el("td", { class: "num" }, fmtNumber(v.views_latest))))
    : [el("tr", {}, el("td", { class: "empty", colspan: "4" }, t("empty_earlier")))]));
}

function renderLastfm() {
  const box = document.getElementById("lastfm");
  const linkLine = document.getElementById("lastfm-link");
  linkLine.replaceChildren();
  const [kind, slug] = state.a.split(":");
  if (kind === "family") return box.replaceChildren(el("p", { class: "note" }, t("lastfm_family")));
  const row = state.data.lastfm.find((r) => r.artist === slug);
  if (!row) return box.replaceChildren(el("p", { class: "note" }, t("lastfm_none")));
  const card = (label, value, change) => el("div", {}, el("dt", {}, label), el("dd", {}, fmtNumber(value),
    change === null ? null : el("small", {}, t("change", { sign: change >= 0 ? "+" : "−", value: fmtNumber(Math.abs(change)) }))));
  // Last.fm's API terms ask for a link back to its catalogue page for the artist.
  const name = artistBySlug()[slug].name;
  linkLine.append(el("a", { href: `https://www.last.fm/music/${encodeURIComponent(name)}`, rel: "noopener" }, t("lastfm_link", { name })));
  box.replaceChildren(card(t("listeners"), row.listeners, row.listeners_change), card(t("scrobbles"), row.playcount, row.playcount_change));
}

function renderExplore() {
  const videos = videosOf(state.a);
  renderTiles(videos);
  renderTimeline(videos);
  renderCurves(videos);
  renderTables(videos);
  renderLastfm();
}

// ---- compare view ------------------------------------------------------------
function renderCompare() {
  const sides = [state.a, state.b].map((entity, i) => ({ entity, videos: videosOf(entity), ...SIDE_STYLE[i] }));
  const yearAgo = new Date(Date.parse(state.data.snapshot_date) - 365 * 86400000).toISOString();

  document.getElementById("versus").replaceChildren(
    ...sides.map((s) => {
      const d7 = s.videos.filter((v) => v.comparable && v.views_d7 !== null).map((v) => v.views_d7);
      const m = median(d7);
      const key = el("span", { class: "side-key", style: `background:${s.color}` });
      return el("div", { class: "side" },
        el("h3", {}, key, entityName(s.entity, true)),
        el("div", { class: "tiles" },
          tile(t("tile_releases"), fmtNumber(s.videos.length)),
          tile(t("tile_recent"), fmtNumber(s.videos.filter((v) => v.published_at >= yearAgo).length)),
          tile(t("tile_measured"), fmtNumber(s.videos.filter((v) => v.comparable).length)),
          tile(t("tile_median7"), m === null ? t("none_yet") : fmtCompact(m))));
    }),
    el("p", { class: "note caveat" }, t("compare_caveat")),
  );

  const all = sides.flatMap((s) => s.videos);
  const first = all.length ? Math.min(...all.map((v) => Number(v.published_at.slice(0, 4)))) : 2015;
  const last = Number(state.data.snapshot_date.slice(0, 4));
  const years = Array.from({ length: last - first + 1 }, (_, i) => first + i);
  const series = sides.map((s) => ({
    name: entityName(s.entity, true), color: s.color,
    counts: s.videos.reduce((acc, v) => { const y = v.published_at.slice(0, 4); acc[y] = (acc[y] || 0) + 1; return acc; }, {}),
  }));
  const legendItems = sides.map((s) => ({ label: entityName(s.entity, true), color: s.color, shape: s.shape }));
  Charts.legend(document.getElementById("peryear-legend"), legendItems);
  Charts.bars(document.getElementById("peryear"), years, series,
    { label: t("chart_peryear"), countLabel: (n) => t("count", { n }) });

  const table = document.getElementById("peryear-table");
  table.replaceChildren(
    el("thead", {}, el("tr", {}, el("th", { scope: "col" }, t("col_year")),
      ...series.map((s) => el("th", { scope: "col", class: "num" }, s.name)))),
    el("tbody", {}, ...years.map((yr) => el("tr", {}, el("td", {}, String(yr)),
      ...series.map((s) => el("td", { class: "num" }, String(s.counts[yr] || 0)))))),
  );

  Charts.legend(document.getElementById("overlay-legend"), legendItems);
  Charts.timeline(document.getElementById("overlay"), sides.flatMap((s) => s.videos.map((v) => ({
    date: Date.parse(v.published_at), value: v.views_latest, highlight: false,
    color: s.color, shape: s.shape, tooltip: tooltipLines(v),
  }))), { label: t("chart_timeline"), empty: "—", formatAxis: fmtCompact });
}

// ---- wiring --------------------------------------------------------------------
function render() {
  Charts.hideTip();
  renderStaticText();
  if (!state.data) return;
  renderControls();
  if (state.view === "explore") renderExplore();
  else renderCompare();
}

document.getElementById("lang").addEventListener("click", () => {
  state.lang = state.lang === "en" ? "es" : "en";
  localStorage.setItem("lang", state.lang);
  render();
});
document.getElementById("pick-a").addEventListener("change", (e) => { state.a = e.target.value; render(); });
document.getElementById("pick-b").addEventListener("change", (e) => { state.b = e.target.value; render(); });
for (const tab of document.querySelectorAll("[role=tab]")) {
  tab.addEventListener("click", () => {
    state.view = tab.id.replace("tab-", "");
    if (state.view === "compare" && state.a === state.b) state.b = state.a === "family:triples" ? "family:twice" : "family:triples";
    render();
  });
}
for (const button of document.querySelectorAll("[data-market]")) {
  button.addEventListener("click", () => { state.market = button.dataset.market; render(); });
}

renderStaticText();
fetch("data/latest.json")
  .then((r) => { if (!r.ok) throw new Error(`data/latest.json: HTTP ${r.status}`); return r.json(); })
  .then((data) => {
    state.data = data;
    const families = entities().filter((e) => e.children.length).map((e) => `family:${e.group.slug}`);
    state.a = families[0] || `artist:${entities()[0].group.slug}`;
    state.b = families[1] || state.a;
    render();
  })
  .catch((error) => { document.getElementById("tiles").textContent = error.message; });
