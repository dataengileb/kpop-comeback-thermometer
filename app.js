// Comeback Thermometer site. Reads data/latest.json (copied from the daily export) and
// never calls AWS. Titles come from YouTube, so they are always set with textContent.
"use strict";

const TEXT = {
  en: {
    title: "Comeback Thermometer",
    question: "How strong was the start of each comeback by TWICE, NMIXX and tripleS, their units and soloists, compared with the artist's previous ones?",
    asof: "Data as of",
    artist: "Artist",
    market: "Market",
    kr: "Korea",
    jp: "Japan",
    unit: "unit",
    solo: "solo",
    ranked_title: "Launches measured from day 1",
    ranked_note_some: "Ranked against this artist's other launches in the same market. Views are cumulative YouTube views at each day after release.",
    ranked_note_none: "No release by this artist in this market since tracking began on {date}. The next one will appear here with its day 1, 7 and 28 views.",
    earlier_title: "Earlier releases (not comparable)",
    earlier_note: "Released before tracking began, so their first days were never observed. Shown with views to date only.",
    col_mv: "Music video",
    col_released: "Released",
    col_d1: "Day 1",
    col_d7: "Day 7",
    col_d28: "Day 28",
    col_age: "Age (days)",
    col_views: "Views to date",
    rank: "#{rank} of {of}",
    pending: "in {days} d",
    missing: "missed",
    copy: "Re-upload; the most viewed copy is used",
    empty_earlier: "None.",
    lastfm_title: "Last.fm",
    listeners: "Listeners",
    scrobbles: "Scrobbles",
    change: "{sign}{value} since the previous snapshot",
    lastfm_none: "Not tracked on Last.fm for this artist.",
    scope_title: "What it is and what it isn't",
    scope: [
      "It measures attention on YouTube and Last.fm, not sales, chart positions or streams on other platforms.",
      "Day-N values exist only for videos released after tracking began. Older videos are shown but not ranked.",
      "Each release is compared only with the same artist's releases for the same market: a Japanese MV or a solo debut is not measured against a TWICE title track.",
      "Last.fm users skew toward Western listeners; Korean domestic listening is under-represented.",
      "This page is a dated snapshot. It is refreshed by hand from the daily pipeline, not live.",
    ],
    footer_data: "Built from a daily batch pipeline on AWS. This page only reads a dated JSON file.",
    footer_repo: "Source code",
    footer_sources: "Data:",
    switch_to: "Español",
  },
  es: {
    title: "Termómetro de comebacks",
    question: "¿Qué tan fuerte arrancó cada comeback de TWICE, NMIXX y tripleS, sus unidades y solistas, comparado con los anteriores del mismo artista?",
    asof: "Datos al",
    artist: "Artista",
    market: "Mercado",
    kr: "Corea",
    jp: "Japón",
    unit: "unidad",
    solo: "solista",
    ranked_title: "Lanzamientos medidos desde el día 1",
    ranked_note_some: "Ranking contra los demás lanzamientos del artista en el mismo mercado. Las vistas son acumuladas en YouTube a cada día del lanzamiento.",
    ranked_note_none: "Este artista no ha lanzado nada en este mercado desde que empezó el seguimiento el {date}. El próximo lanzamiento aparecerá aquí con sus vistas al día 1, 7 y 28.",
    earlier_title: "Lanzamientos anteriores (no comparables)",
    earlier_note: "Salieron antes de que empezara el seguimiento, así que sus primeros días no se observaron. Solo se muestran las vistas a la fecha.",
    col_mv: "Video musical",
    col_released: "Lanzamiento",
    col_d1: "Día 1",
    col_d7: "Día 7",
    col_d28: "Día 28",
    col_age: "Edad (días)",
    col_views: "Vistas a la fecha",
    rank: "#{rank} de {of}",
    pending: "en {days} d",
    missing: "sin dato",
    copy: "Resubida; se usa la copia con más vistas",
    empty_earlier: "Ninguno.",
    lastfm_title: "Last.fm",
    listeners: "Oyentes",
    scrobbles: "Reproducciones",
    change: "{sign}{value} desde la foto anterior",
    lastfm_none: "Este artista no se mide en Last.fm.",
    scope_title: "Lo que sí es y lo que no",
    scope: [
      "Mide atención en YouTube y Last.fm, no ventas, posiciones en charts ni streams en otras plataformas.",
      "Los valores al día N solo existen para videos publicados después de que empezó el seguimiento. Los anteriores se muestran, pero no se comparan.",
      "Cada lanzamiento se compara solo con los del mismo artista para el mismo mercado: un MV japonés o un debut en solitario no se mide contra un sencillo principal de TWICE.",
      "Los usuarios de Last.fm son sobre todo occidentales; el consumo en Corea está subrepresentado.",
      "Esta página es un corte fechado. Se actualiza a mano desde el pipeline diario, no en vivo.",
    ],
    footer_data: "Construido con un pipeline batch diario en AWS. Esta página solo lee un archivo JSON fechado.",
    footer_repo: "Código fuente",
    footer_sources: "Datos:",
    switch_to: "English",
  },
};

const state = { lang: pickLanguage(), data: null, artist: null, market: "kr" };

function pickLanguage() {
  const fromUrl = new URLSearchParams(location.search).get("lang");
  const saved = localStorage.getItem("lang");
  const chosen = fromUrl || saved || (navigator.language || "en").slice(0, 2);
  return chosen === "es" ? "es" : "en";
}

const t = (key, vars = {}) =>
  String(TEXT[state.lang][key]).replace(/\{(\w+)\}/g, (_, name) => vars[name] ?? "");

const fmtNumber = (n) => new Intl.NumberFormat(state.lang).format(n);
const fmtDate = (iso) =>
  new Intl.DateTimeFormat(state.lang, { year: "numeric", month: "short", day: "numeric", timeZone: "UTC" })
    .format(new Date(iso.length === 10 ? `${iso}T00:00:00Z` : iso));
const daysBetween = (fromIso, toIso) =>
  Math.round((Date.parse(toIso.slice(0, 10)) - Date.parse(fromIso.slice(0, 10))) / 86400000);

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (key === "class") node.className = value;
    else node.setAttribute(key, value);
  }
  for (const child of children) node.append(child);
  return node;
}

function videosFor(artist, market) {
  return state.data.videos.filter((v) => v.artist === artist && v.market === market && !v.is_duplicate);
}

function renderStaticText() {
  document.documentElement.lang = state.lang;
  document.title = t("title");
  for (const node of document.querySelectorAll("[data-i18n]")) node.textContent = t(node.dataset.i18n);
  const lang = document.getElementById("lang");
  lang.textContent = state.lang === "en" ? "ES" : "EN";
  lang.setAttribute("aria-label", t("switch_to"));
  const scope = document.getElementById("scope");
  scope.replaceChildren(...TEXT[state.lang].scope.map((line) => el("li", {}, line)));
  if (state.data) document.getElementById("snapshot-date").textContent = fmtDate(state.data.snapshot_date);
}

function renderArtistSelect() {
  const select = document.getElementById("artist");
  const withVideos = new Set(state.data.videos.map((v) => v.artist));
  const artists = state.data.artists.filter((a) => withVideos.has(a.slug));
  const groups = artists.filter((a) => a.parent === null);
  select.replaceChildren(
    ...groups.map((group) =>
      el(
        "optgroup",
        { label: group.name },
        el("option", { value: group.slug }, group.name),
        ...artists
          .filter((a) => a.parent === group.slug)
          .map((a) => el("option", { value: a.slug }, `${a.name} (${t(a.kind)})`)),
      ),
    ),
  );
  select.value = state.artist;
}

function renderMarkets() {
  for (const button of document.querySelectorAll("[data-market]")) {
    const market = button.dataset.market;
    button.disabled = videosFor(state.artist, market).length === 0;
    button.setAttribute("aria-checked", String(market === state.market));
  }
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

function titleCell(video) {
  const link = el("a", { href: `https://www.youtube.com/watch?v=${encodeURIComponent(video.video_id)}`, rel: "noopener" }, video.title);
  return el("td", {}, link);
}

function renderTables() {
  const all = state.data.videos.filter((v) => v.artist === state.artist && v.market === state.market);
  const ranked = all.filter((v) => v.comparable && !v.is_duplicate);
  const earlier = all.filter((v) => !v.comparable && !v.is_duplicate);
  const snapshot = state.data.snapshot_date;

  document.getElementById("ranked-note").textContent = ranked.length
    ? t("ranked_note_some")
    : t("ranked_note_none", { date: fmtDate(state.data.first_snapshot_date || snapshot) });
  document.querySelector("#ranked tbody").replaceChildren(
    ...(ranked.length
      ? ranked.map((v) => {
          const age = daysBetween(v.published_at, snapshot);
          const row = el("tr", {}, titleCell(v), el("td", {}, fmtDate(v.published_at)));
          for (const n of [1, 7, 28]) row.append(dayCell(v, n, age));
          return row;
        })
      : [el("tr", {}, el("td", { class: "empty", colspan: "5" }, "—"))]),
  );

  document.querySelector("#earlier tbody").replaceChildren(
    ...(earlier.length
      ? earlier.map((v) =>
          el(
            "tr",
            {},
            titleCell(v),
            el("td", {}, fmtDate(v.published_at)),
            el("td", { class: "num" }, fmtNumber(daysBetween(v.published_at, snapshot))),
            el("td", { class: "num" }, fmtNumber(v.views_latest)),
          ),
        )
      : [el("tr", {}, el("td", { class: "empty", colspan: "4" }, t("empty_earlier")))]),
  );
}

function renderLastfm() {
  const box = document.getElementById("lastfm");
  const row = state.data.lastfm.find((r) => r.artist === state.artist);
  if (!row) {
    box.replaceChildren(el("p", { class: "note" }, t("lastfm_none")));
    return;
  }
  const card = (label, value, change) => {
    const dd = el("dd", {}, fmtNumber(value));
    if (change !== null) {
      dd.append(el("small", {}, t("change", { sign: change >= 0 ? "+" : "−", value: fmtNumber(Math.abs(change)) })));
    }
    return el("div", {}, el("dt", {}, label), dd);
  };
  box.replaceChildren(
    card(t("listeners"), row.listeners, row.listeners_change),
    card(t("scrobbles"), row.playcount, row.playcount_change),
  );
}

function render() {
  renderStaticText();
  if (!state.data) return;
  renderArtistSelect();
  renderMarkets();
  renderTables();
  renderLastfm();
}

function chooseMarket() {
  if (videosFor(state.artist, state.market).length === 0) {
    state.market = videosFor(state.artist, "kr").length ? "kr" : "jp";
  }
}

document.getElementById("lang").addEventListener("click", () => {
  state.lang = state.lang === "en" ? "es" : "en";
  localStorage.setItem("lang", state.lang);
  render();
});

document.getElementById("artist").addEventListener("change", (event) => {
  state.artist = event.target.value;
  chooseMarket();
  render();
});

for (const button of document.querySelectorAll("[data-market]")) {
  button.addEventListener("click", () => {
    state.market = button.dataset.market;
    render();
  });
}

renderStaticText();
fetch("data/latest.json")
  .then((response) => {
    if (!response.ok) throw new Error(`data/latest.json: HTTP ${response.status}`);
    return response.json();
  })
  .then((data) => {
    state.data = data;
    state.artist = data.artists.find((a) => data.videos.some((v) => v.artist === a.slug))?.slug;
    chooseMarket();
    render();
  })
  .catch((error) => {
    document.getElementById("ranked-note").textContent = error.message;
  });
