/*
 * J-Curve India — Unified Verdict
 * Combines J-Curve (inflection) with Sector-Screen (quality & momentum).
 *
 * Data sources (configurable in data/config.json):
 *   - J-Curve:   raw JSON list of tickers, each with stage, score, trigger, redFlags
 *   - Sector:    array of { symbol, score, momentum, action, reason }
 *                or { scores: [...] } or { data: [...] } shapes supported.
 *
 * If Sector-Screen URL is unreachable, the app still renders using J-Curve
 * alone; "Sector-Screen" column will show "—" and verdict falls back to
 * J-Curve-derived.
 */

const STATE = {
  jcurve: [],
  sector: {},
  config: null,
  rows: [],
  filter: { search: "", sector: "", verdict: "", sort: "verdict" },
  selected: null,
};

const $ = (id) => document.getElementById(id);
const escape = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
}[c]));

async function loadConfig() {
  // config.json sits alongside the HTML in the deployed site.
  const r = await fetch("data/config.json");
  return await r.json();
}

async function loadJCurve(url) {
  const r = await fetch(url, { cache: "no-store" });
  if (!r.ok) throw new Error(`J-Curve fetch failed: ${r.status}`);
  return await r.json();
}

async function loadSector(url) {
  // Returns a map { SYMBOL: { score, momentum, action, reason, source } }.
  // 1) Try the configured URL.
  // 2) Fall back to a local snapshot.
  // Supports two response shapes:
  //   A) Flat array of { symbol, score, momentum, action, reason }
  //   B) SectorScreenWeb nested: { as_of, sectors: { "Pharma": { modes: { quality_first: [...] } } } }
  //      → flattened; each row gets q_score, mom_score, composite, category.
  try {
    const r = await fetch(url, { cache: "no-store" });
    if (r.ok) {
      const j = await r.json();
      const map = sectorArrayToMap(j);
      if (Object.keys(map).length > 0) return map;
    }
  } catch (e) {
    console.warn("Sector-Screen fetch failed, using fallback snapshot:", e);
  }
  try {
    const r = await fetch("data/sector-snapshot.json", { cache: "no-store" });
    if (r.ok) {
      const j = await r.json();
      return sectorArrayToMap(j);
    }
  } catch (e) {
    console.warn("Sector-Screen snapshot fallback also failed:", e);
  }
  return {};
}

function sectorArrayToMap(j) {
  // Shape A: flat list
  if (Array.isArray(j)) return flatListToMap(j);
  // Shape B: SectorScreenWeb nested (has "sectors" key)
  if (j && j.sectors && typeof j.sectors === "object") {
    const all = [];
    for (const sector of Object.values(j.sectors)) {
      const modes = sector.modes || {};
      // Prefer quality_first (richer scoring), fall back to strict.
      const rows = modes.quality_first || modes.strict || [];
      for (const r of rows) {
        all.push({
          symbol: (r.ticker || "").replace(/\.NS$/i, "").toUpperCase(),
          score: r.composite ?? r.q_score ?? null,
          momentum: r.mom_score ?? null,
          action: r.category || null,
          reason: r.company || null,
          as_of: j.as_of || null,
          mode: modes.quality_first ? "quality_first" : "strict",
        });
      }
    }
    return flatListToMap(all);
  }
  // Shape C: { scores: [...] } or { data: [...] }
  if (j && Array.isArray(j.scores)) return flatListToMap(j.scores);
  if (j && Array.isArray(j.data))    return flatListToMap(j.data);
  return {};
}

function flatListToMap(arr) {
  const out = {};
  for (const row of arr) {
    const sym = (row.symbol || row.ticker || row.sym || "").toUpperCase().replace(/\.NS$/i, "");
    if (!sym) continue;
    out[sym] = {
      score: row.score ?? row.quality ?? row.composite ?? row.q_score ?? null,
      momentum: row.momentum ?? row.trend ?? row.mom_score ?? null,
      action: row.action ?? row.rating ?? row.category ?? null,
      reason: row.reason ?? row.note ?? row.company ?? null,
      as_of: row.as_of || null,
    };
  }
  return out;
}

function normalizeSymbol(s) {
  return String(s || "").toUpperCase().replace(/[^A-Z0-9&\-]/g, "");
}

function computeVerdict(j, s) {
  const has = (k) => j && j[k] != null;
  const stage = j?.stage ?? null;
  const jScore = j?.score ?? null;
  const ssScore = s?.score ?? null;
  const ssMomentum = s?.momentum ?? null;
  const ssAction = s?.action?.toUpperCase() || null;
  const redFlags = Array.isArray(j?.redFlags) && j.redFlags.length > 0;

  let base, why;

  // J-Curve primary
  if (stage === 2 && jScore != null && jScore >= 75) {
    base = "BUY";
    why = `J-Curve inflection (stage 2, score ${jScore}) — operating leverage becoming visible.`;
  } else if (stage === 2 && jScore != null && jScore >= 65) {
    base = "WATCH";
    why = `J-Curve stage 2, but score ${jScore} is below the 75 buy bar.`;
  } else if (stage === 1 && jScore != null && jScore >= 70) {
    base = "WATCH";
    why = `J-Curve stage 1, score ${jScore} — catalyst is forming, wait for the inflection.`;
  } else if (stage === 3) {
    base = "HOLD";
    why = `J-Curve stage 3 — already re-rated, late entry.`;
  } else if (jScore != null && jScore < 60) {
    base = "AVOID";
    why = `J-Curve score ${jScore} too low — thesis weak.`;
  } else {
    base = "WATCH";
    why = `J-Curve inconclusive (stage ${stage}, score ${jScore}).`;
  }

  // Sector-Screen overlay
  let disagree = false;
  if (s && ssAction) {
    const a = ssAction;
    if (a === "AVOID" || a === "SELL") {
      if (base === "BUY") { base = "WATCH"; disagree = true; why += ` Sector-Screen says AVOID — confirmed concern.`; }
      else if (base === "WATCH") { base = "AVOID"; why += ` Sector-Screen says AVOID — overriding.`; }
      else why += ` Sector-Screen says AVOID.`;
    } else if (a === "BUY" || a === "STRONG BUY" || a === "ACCUMULATE") {
      if (base === "AVOID") { base = "WATCH"; disagree = true; why += ` Sector-Screen says BUY — partial offset.`; }
      else if (base === "HOLD") { base = "WATCH"; why += ` Sector-Screen strength keeps it on watch.`; }
      else if (base === "WATCH") { base = "BUY"; why += ` Sector-Screen confirms the BUY.`; }
    } else if (a === "HOLD") {
      // no change
    }
  }

  if (redFlags && base !== "AVOID") {
    base = base === "BUY" ? "WATCH" : "AVOID";
    why += ` One-off item in red flags — treated with caution.`;
  }

  return { verdict: base, why, disagree };
}

function buildRows() {
  const rows = [];
  for (const j of STATE.jcurve) {
    const sym = normalizeSymbol(j.symbol);
    const s = STATE.sector[sym] || null;
    const v = computeVerdict(j, s);
    rows.push({
      symbol: j.symbol,
      company: j.name || j.symbol,
      sector: j.sector || "—",
      subIndustry: j.subIndustry || j.sector || "—",
      stage: j.stage,
      jScore: j.score,
      ssScore: s?.score ?? null,
      ssAction: s?.action ?? null,
      ssMomentum: s?.momentum ?? null,
      ssReason: s?.reason ?? null,
      trigger: j.trigger,
      redFlags: j.redFlags || [],
      invalidation: j.invalidation,
      price: j.price,
      ...v,
    });
  }
  STATE.rows = rows;
  populateSectorFilter();
  render();
}

function populateSectorFilter() {
  const sectors = [...new Set(STATE.rows.map((r) => r.subIndustry))].sort();
  const sel = $("sector");
  sel.innerHTML = '<option value="">All sub-industries</option>' +
    sectors.map((s) => `<option value="${escape(s)}">${escape(s)}</option>`).join("");
}

function passesFilter(r) {
  const q = STATE.filter.search.toLowerCase();
  if (q && !(r.symbol.toLowerCase().includes(q) || r.company.toLowerCase().includes(q))) return false;
  if (STATE.filter.sector && r.subIndustry !== STATE.filter.sector) return false;
  if (STATE.filter.verdict && r.verdict !== STATE.filter.verdict) return false;
  return true;
}

const VERDICT_RANK = { BUY: 0, WATCH: 1, HOLD: 2, AVOID: 3 };

function sortRows(rows) {
  const k = STATE.filter.sort;
  if (k === "verdict")      return rows.sort((a, b) => VERDICT_RANK[a.verdict] - VERDICT_RANK[b.verdict] || (b.jScore || 0) - (a.jScore || 0));
  if (k === "jcurve")       return rows.sort((a, b) => (b.jScore || 0) - (a.jScore || 0));
  if (k === "sectorScreen") return rows.sort((a, b) => (b.ssScore || 0) - (a.ssScore || 0));
  if (k === "symbol")       return rows.sort((a, b) => a.symbol.localeCompare(b.symbol));
  return rows;
}

function render() {
  const rows = sortRows(STATE.rows.filter(passesFilter));
  $("cTotal").textContent = STATE.rows.length;
  $("cBuy").textContent    = STATE.rows.filter((r) => r.verdict === "BUY").length;
  $("cWatch").textContent  = STATE.rows.filter((r) => r.verdict === "WATCH").length;
  $("cHold").textContent   = STATE.rows.filter((r) => r.verdict === "HOLD").length;
  $("cAvoid").textContent  = STATE.rows.filter((r) => r.verdict === "AVOID").length;
  $("cDis").textContent    = STATE.rows.filter((r) => r.disagree).length;
  $("asOf").textContent = new Date().toLocaleString();

  const tbody = $("rows");
  if (rows.length === 0) {
    tbody.innerHTML = "";
    $("empty").hidden = false;
    return;
  }
  $("empty").hidden = true;
  tbody.innerHTML = rows.map((r) => {
    const jPill = r.jScore == null ? "—" : r.jScore;
    const sPill = r.ssScore == null ? "—" : r.ssScore;
    const sAct  = r.ssAction ? `<span class="score-pill none">${escape(r.ssAction)}</span>` : "—";
    return `
      <tr data-sym="${escape(r.symbol)}">
        <td><b>${escape(r.symbol)}</b></td>
        <td>
          <div>${escape(r.company)}</div>
          <div class="muted" style="font-size:11px">${escape(r.subIndustry)}</div>
        </td>
        <td>${escape(r.sector)}</td>
        <td>
          <span class="score-pill ${verdictClass(r.verdict)}">${escape(jPill)}</span>
          ${r.stage ? `<span class="stage-badge s${r.stage}">S${r.stage}</span>` : ""}
        </td>
        <td>${sPill} ${sAct}</td>
        <td><span class="score-pill ${verdictClass(r.verdict)} ${r.disagree ? "dis" : ""}">${r.disagree ? "⚠ " : ""}${escape(r.verdict)}</span></td>
        <td class="muted">${escape(r.why)}</td>
      </tr>
    `;
  }).join("");
  tbody.querySelectorAll("tr").forEach((tr) => {
    tr.addEventListener("click", () => selectRow(tr.dataset.sym));
  });
  if (STATE.selected) selectRow(STATE.selected, true);
}

function verdictClass(v) {
  return ({ BUY: "buy", WATCH: "watch", HOLD: "hold", AVOID: "avoid" })[v] || "none";
}

function selectRow(sym, keepIfSame = false) {
  const r = STATE.rows.find((x) => x.symbol === sym);
  if (!r) return;
  if (!keepIfSame) STATE.selected = sym;
  document.querySelectorAll("#rows tr").forEach((tr) => {
    tr.classList.toggle("selected", tr.dataset.sym === sym);
  });
  const t = $("thesis");
  t.innerHTML = `
    <h3>${escape(r.company)} <span class="score-pill ${verdictClass(r.verdict)}">${r.disagree ? "⚠ " : ""}${escape(r.verdict)}</span></h3>
    <div class="muted">${escape(r.symbol)} · ${escape(r.sector)}</div>
    <div class="why">${escape(r.why)}</div>
    <div class="row"><b>J-Curve score</b><span>${r.jScore ?? "—"} (stage ${r.stage ?? "—"})</span></div>
    <div class="row"><b>Sector-Screen score</b><span>${r.ssScore ?? "—"} ${r.ssAction ? `(${escape(r.ssAction)})` : ""}</span></div>
    <div class="row"><b>Price (yfinance)</b><span>${r.price ?? "—"}</span></div>
    <div class="row"><b>Trigger</b><span style="text-align:right;max-width:60%">${escape(r.trigger || "—")}</span></div>
    <div class="row"><b>Invalidation</b><span style="text-align:right;max-width:60%">${escape(r.invalidation || "—")}</span></div>
    ${r.ssReason ? `<div class="row"><b>Sector-Screen note</b><span style="text-align:right;max-width:60%">${escape(r.ssReason)}</span></div>` : ""}
    <div class="flag ${r.redFlags.length === 0 ? "empty" : ""}">
      <b>Red flags (${r.redFlags.length}):</b>
      <ul style="margin:4px 0 0 18px;padding:0">${r.redFlags.map((f) => `<li>${escape(f)}</li>`).join("") || "<li>None</li>"}</ul>
    </div>
  `;
}

function bindFilters() {
  $("search").addEventListener("input", (e) => { STATE.filter.search = e.target.value; render(); });
  $("sector").addEventListener("change", (e) => { STATE.filter.sector = e.target.value; render(); });
  $("verdict").addEventListener("change", (e) => { STATE.filter.verdict = e.target.value; render(); });
  $("sort").addEventListener("change", (e) => { STATE.filter.sort = e.target.value; render(); });
  $("refresh").addEventListener("click", () => loadAll(true));
}

async function loadAll(force = false) {
  $("rows").innerHTML = `<tr><td colspan="7" class="muted" style="text-align:center;padding:30px">Loading…</td></tr>`;
  STATE.config = await loadConfig();
  const [jc, sc] = await Promise.all([
    loadJCurve(STATE.config.jcurve.url),
    loadSector(STATE.config.sectorScreen.url),
  ]);
  STATE.jcurve = jc;
  STATE.sector = sc;
  buildRows();
}

window.addEventListener("DOMContentLoaded", () => {
  bindFilters();
  loadAll();
});
