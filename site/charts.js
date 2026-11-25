// Small hand-written SVG charts for the site: a release timeline (dots), launch curves (lines)
// and releases per year (grouped bars). No library, no network. Every mark has a keyboard- and
// mouse-reachable hit target that shows the shared tooltip.
"use strict";

const Charts = (() => {
  const NS = "http://www.w3.org/2000/svg";
  const INK = "#F2F2F2";
  const MUTED = "#A8A8A8";
  const GRID = "#2A2A2A";
  const SURFACE = "#000000";
  const HIGHLIGHT = "#00E5FF";

  function svg(tag, attrs = {}, parent) {
    const node = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, v);
    if (parent) parent.append(node);
    return node;
  }

  function frame(container, width, height, label) {
    const root = svg("svg", { viewBox: `0 0 ${width} ${height}`, role: "img", "aria-label": label, class: "chart-svg" });
    container.replaceChildren(root);
    return root;
  }

  // ---- tooltip -------------------------------------------------------------
  const tip = () => document.getElementById("tooltip");
  function showTip(lines, x, y) {
    const box = tip();
    box.replaceChildren(...lines.map((line, i) => {
      const p = document.createElement("p");
      p.textContent = line;
      if (i === 0) p.className = "tip-title";
      return p;
    }));
    box.hidden = false;
    const pad = 14;
    const w = box.offsetWidth;
    const h = box.offsetHeight;
    const left = Math.min(window.innerWidth - w - 8, Math.max(8, x + pad));
    const top = y - h - pad < 8 ? y + pad : y - h - pad;
    box.style.left = `${left}px`;
    box.style.top = `${top}px`;
  }
  const hideTip = () => { tip().hidden = true; };

  function hit(parent, shape, lines) {
    shape.setAttribute("tabindex", "0");
    shape.setAttribute("role", "img");
    shape.setAttribute("aria-label", lines.join(", "));
    shape.classList.add("hit");
    shape.addEventListener("mousemove", (e) => showTip(lines, e.clientX, e.clientY));
    shape.addEventListener("mouseleave", hideTip);
    shape.addEventListener("focus", () => {
      const r = shape.getBoundingClientRect();
      showTip(lines, r.left + r.width / 2, r.top);
    });
    shape.addEventListener("blur", hideTip);
    parent.append(shape);
  }

  // ---- markers: shape is the secondary encoding of the series ---------------
  function marker(parent, shape, x, y, color) {
    const s = 5;
    const ring = { stroke: SURFACE, "stroke-width": 2, fill: color };
    if (shape === "square") return svg("rect", { x: x - s, y: y - s, width: 2 * s, height: 2 * s, rx: 1.5, ...ring }, parent);
    if (shape === "diamond") {
      const d = s * 1.35;
      return svg("path", { d: `M${x} ${y - d}L${x + d} ${y}L${x} ${y + d}L${x - d} ${y}Z`, ...ring }, parent);
    }
    return svg("circle", { cx: x, cy: y, r: s + 0.5, ...ring }, parent);
  }

  function emptyState(root, width, height, text) {
    svg("text", { x: width / 2, y: height / 2, "text-anchor": "middle", fill: MUTED, "font-size": 15 }, root).textContent = text;
  }

  // ---- release timeline: x = release date, y = views to date (log) ---------
  function timeline(container, points, opts) {
    const W = 960, H = 380, m = { l: 64, r: 20, t: 18, b: 40 };
    const root = frame(container, W, H, opts.label);
    if (!points.length) return emptyState(root, W, H, opts.empty);

    const t0 = new Date(Date.UTC(new Date(Math.min(...points.map((p) => p.date))).getUTCFullYear(), 0, 1)).getTime();
    const t1 = new Date(Date.UTC(new Date(Math.max(...points.map((p) => p.date))).getUTCFullYear() + 1, 0, 1)).getTime();
    const lo = Math.floor(Math.log10(Math.max(1, Math.min(...points.map((p) => p.value)))));
    const hi = Math.ceil(Math.log10(Math.max(...points.map((p) => p.value)) + 1));
    const x = (t) => m.l + ((t - t0) / (t1 - t0)) * (W - m.l - m.r);
    const y = (v) => H - m.b - ((Math.log10(Math.max(v, 1)) - lo) / Math.max(hi - lo, 1)) * (H - m.t - m.b);

    for (let e = lo; e <= hi; e++) {
      svg("line", { x1: m.l, x2: W - m.r, y1: y(10 ** e), y2: y(10 ** e), stroke: GRID, "stroke-width": 1 }, root);
      svg("text", { x: m.l - 10, y: y(10 ** e) + 4, "text-anchor": "end", fill: MUTED, "font-size": 13 }, root)
        .textContent = opts.formatAxis(10 ** e);
    }
    const y0 = new Date(t0).getUTCFullYear(), y1 = new Date(t1).getUTCFullYear();
    const step = y1 - y0 > 8 ? 2 : 1;
    for (let yr = y0; yr <= y1; yr += step) {
      const tx = x(Date.UTC(yr, 0, 1));
      svg("line", { x1: tx, x2: tx, y1: H - m.b, y2: H - m.b + 5, stroke: MUTED, "stroke-width": 1 }, root);
      svg("text", { x: tx, y: H - m.b + 22, "text-anchor": "middle", fill: MUTED, "font-size": 13 }, root).textContent = yr;
    }
    svg("line", { x1: m.l, x2: W - m.r, y1: H - m.b, y2: H - m.b, stroke: "#5A5A5A", "stroke-width": 2 }, root);

    const marks = svg("g", {}, root);
    const hits = svg("g", {}, root);
    for (const p of [...points].sort((a, b) => b.value - a.value)) {
      const px = x(p.date), py = y(p.value);
      if (p.highlight) svg("circle", { cx: px, cy: py, r: 10, fill: "none", stroke: HIGHLIGHT, "stroke-width": 2 }, marks);
      marker(marks, p.shape, px, py, p.color);
      hit(hits, svg("circle", { cx: px, cy: py, r: 12, fill: "transparent" }), p.tooltip);
    }
  }

  // ---- launch curves: day 1, 7, 28 on an ordinal x, views on a linear y -------
  function curves(container, series, opts) {
    const W = 960, H = 320, m = { l: 72, r: 24, t: 18, b: 40 };
    const root = frame(container, W, H, opts.label);
    const values = series.flatMap((s) => s.points.map((p) => p.value));
    if (!values.length) return emptyState(root, W, H, opts.empty);

    const days = [1, 7, 28];
    const x = (d) => m.l + (days.indexOf(d) / (days.length - 1)) * (W - m.l - m.r);
    const max = niceMax(Math.max(...values));
    const y = (v) => H - m.b - (v / max) * (H - m.t - m.b);
    for (let i = 0; i <= 4; i++) {
      const v = (max / 4) * i;
      svg("line", { x1: m.l, x2: W - m.r, y1: y(v), y2: y(v), stroke: GRID, "stroke-width": 1 }, root);
      svg("text", { x: m.l - 10, y: y(v) + 4, "text-anchor": "end", fill: MUTED, "font-size": 13 }, root).textContent = opts.formatAxis(v);
    }
    for (const d of days) {
      svg("text", { x: x(d), y: H - m.b + 22, "text-anchor": "middle", fill: MUTED, "font-size": 13 }, root).textContent = opts.dayLabel(d);
    }
    const hits = svg("g", {});
    for (const s of series) {
      if (s.points.length > 1) {
        svg("polyline", { points: s.points.map((p) => `${x(p.day)},${y(p.value)}`).join(" "), fill: "none",
          stroke: s.color, "stroke-width": 2, "stroke-linejoin": "round", "stroke-linecap": "round" }, root);
      }
      for (const p of s.points) {
        marker(root, s.shape, x(p.day), y(p.value), s.color);
        hit(hits, svg("circle", { cx: x(p.day), cy: y(p.value), r: 12, fill: "transparent" }), p.tooltip);
      }
    }
    root.append(hits);
  }

  // ---- releases per year: two series as grouped columns ----------------------
  function bars(container, years, series, opts) {
    const W = 960, H = 300, m = { l: 48, r: 16, t: 18, b: 40 };
    const root = frame(container, W, H, opts.label);
    const max = Math.max(1, ...series.flatMap((s) => years.map((yr) => s.counts[yr] || 0)));
    const top = Math.max(2, Math.ceil(max / 2) * 2);
    const y = (v) => H - m.b - (v / top) * (H - m.t - m.b);
    for (let v = 0; v <= top; v += Math.max(1, Math.round(top / 4))) {
      svg("line", { x1: m.l, x2: W - m.r, y1: y(v), y2: y(v), stroke: GRID, "stroke-width": 1 }, root);
      svg("text", { x: m.l - 10, y: y(v) + 4, "text-anchor": "end", fill: MUTED, "font-size": 13 }, root).textContent = v;
    }
    const band = (W - m.l - m.r) / years.length;
    const barW = Math.min(18, (band - 10) / series.length - 2);
    const hits = svg("g", {});
    years.forEach((yr, i) => {
      const cx = m.l + band * (i + 0.5);
      svg("text", { x: cx, y: H - m.b + 22, "text-anchor": "middle", fill: MUTED, "font-size": 13 }, root).textContent = yr;
      series.forEach((s, j) => {
        const v = s.counts[yr] || 0;
        const bx = cx - (series.length * (barW + 2)) / 2 + j * (barW + 2) + 1;
        if (v > 0) {
          const by = y(v), r = Math.min(4, barW / 2, H - m.b - by);
          svg("path", {
            d: `M${bx} ${H - m.b}V${by + r}Q${bx} ${by} ${bx + r} ${by}H${bx + barW - r}Q${bx + barW} ${by} ${bx + barW} ${by + r}V${H - m.b}Z`,
            fill: s.color,
          }, root);
        }
        hit(hits, svg("rect", { x: bx - 2, y: m.t, width: barW + 4, height: H - m.t - m.b, fill: "transparent" }),
          [`${s.name} · ${yr}`, opts.countLabel(v)]);
      });
    });
    svg("line", { x1: m.l, x2: W - m.r, y1: H - m.b, y2: H - m.b, stroke: "#5A5A5A", "stroke-width": 2 }, root);
    root.append(hits);
  }

  function niceMax(v) {
    const p = 10 ** Math.floor(Math.log10(v || 1));
    for (const f of [1, 2, 2.5, 5, 10]) if (f * p >= v) return f * p;
    return 10 * p;
  }

  function legend(list, items) {
    list.replaceChildren(...items.map((item) => {
      const li = document.createElement("li");
      const key = svg("svg", { viewBox: "0 0 16 16", width: 16, height: 16, "aria-hidden": "true" });
      if (item.ring) svg("circle", { cx: 8, cy: 8, r: 6, fill: "none", stroke: HIGHLIGHT, "stroke-width": 2 }, key);
      else marker(key, item.shape || "circle", 8, 8, item.color);
      li.append(key, document.createTextNode(item.label));
      return li;
    }));
  }

  return { timeline, curves, bars, legend, hideTip, INK };
})();
