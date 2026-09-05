/*
 * Portfolio tracker — stores positions in localStorage, fetches live prices
 * from J-Curve data feed (re-uses the public stocks.json), computes P&L.
 */

const STORAGE_KEY = "jcurve_portfolio_v1";
const $ = (id) => document.getElementById(id);

const STATE = {
  positions: [],
  jcurveBySym: {},
  jcurveSectors: {},
};

const VERDICT_LABEL = {
  2: { label: "BUY", cls: "buy" },
  1: { label: "WATCH", cls: "watch" },
  3: { label: "HOLD", cls: "hold" },
};

function loadPositions() {
  try {
    STATE.positions = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
  } catch { STATE.positions = []; }
  return STATE.positions;
}
function savePositions() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(STATE.positions));
}

async function loadJCurve() {
  const r = await fetch("https://raw.githubusercontent.com/varshabhagat45-commits/J-Curve-India-Stock-Scanner/main/data/stocks.json", { cache: "no-store" });
  const arr = await r.json();
  STATE.jcurveBySym = {};
  for (const s of arr) {
    STATE.jcurveBySym[s.symbol] = s;
    STATE.jcurveSectors[s.symbol] = s.subIndustry || s.sector || "—";
  }
}

function fmt(n) {
  if (n == null || isNaN(n)) return "—";
  return Number(n).toLocaleString("en-IN", { maximumFractionDigits: 2 });
}
function fmtPct(n) {
  if (n == null || isNaN(n)) return "—";
  const s = (n >= 0 ? "+" : "") + n.toFixed(2) + "%";
  return s;
}
function daysAgo(dateStr) {
  if (!dateStr) return "—";
  const d = new Date(dateStr);
  const ms = Date.now() - d.getTime();
  return Math.floor(ms / 86400000) + "d";
}

function renderCounters() {
  let totalCost = 0, totalValue = 0;
  for (const p of STATE.positions) {
    const jc = STATE.jcurveBySym[p.symbol];
    const cur = jc?.price || p.avgCost;
    totalCost += p.qty * p.avgCost;
    totalValue += p.qty * cur;
  }
  const pnl = totalValue - totalCost;
  const ret = totalCost > 0 ? (pnl / totalCost) * 100 : 0;
  const winners = STATE.positions.filter((p) => {
    const jc = STATE.jcurveBySym[p.symbol];
    return (jc?.price || p.avgCost) > p.avgCost;
  }).length;
  const losers = STATE.positions.length - winners;
  const cards = [
    { lbl: "INVESTED", val: "₹" + fmt(totalCost), sub: STATE.positions.length + " positions" },
    { lbl: "CURRENT VALUE", val: "₹" + fmt(totalValue), sub: winners + " winners · " + losers + " losers" },
    { lbl: "P&L", val: (pnl >= 0 ? "+" : "") + "₹" + fmt(pnl), sub: "", klass: pnl >= 0 ? "pos" : "neg" },
    { lbl: "RETURN", val: fmtPct(ret), sub: "", klass: ret >= 0 ? "pos" : "neg" },
  ];
  $("counters").innerHTML = cards.map((c) =>
    `<div class="card"><div class="lbl">${c.lbl}</div><div class="val ${c.klass || ""}">${c.val}</div><div class="sub">${c.sub}</div></div>`
  ).join("");
}

function suggestAction(p, jc) {
  if (!jc) return { label: "—", cls: "partial" };
  const stage = jc.stage;
  if (stage === 1) {
    if (jc.score >= 70) return { label: "HOLD · thesis building", cls: "watch" };
    return { label: "REVIEW · low score", cls: "avoid" };
  }
  if (stage === 2) {
    if (jc.score >= 75) return { label: "HOLD · sweet spot", cls: "buy" };
    return { label: "HOLD · monitor", cls: "watch" };
  }
  if (stage === 3) {
    return { label: "TRIM · already re-rated", cls: "hold" };
  }
  return { label: "—", cls: "partial" };
}

function renderPositions() {
  if (STATE.positions.length === 0) {
    $("empty").hidden = false;
    $("positions").innerHTML = "";
    return;
  }
  $("empty").hidden = true;
  $("positions").innerHTML = STATE.positions.map((p, i) => {
    const jc = STATE.jcurveBySym[p.symbol];
    const cur = jc?.price;
    const cost = p.qty * p.avgCost;
    const value = cur ? p.qty * cur : null;
    const pnl = value != null ? value - cost : null;
    const ret = pnl != null ? (pnl / cost) * 100 : null;
    const verdict = jc ? VERDICT_LABEL[jc.stage] || { label: `S${jc.stage}`, cls: "partial" } : { label: "—", cls: "partial" };
    const action = suggestAction(p, jc);
    return `<tr>
      <td><b>${escape(p.symbol)}</b><div class="muted" style="font-size:11px">${escape(STATE.jcurveSectors[p.symbol] || "")}</div></td>
      <td>${p.qty}</td>
      <td>₹${fmt(p.avgCost)}</td>
      <td>${cur ? "₹" + fmt(cur) : "—"}</td>
      <td class="${pnl == null ? "" : (pnl >= 0 ? "pnl-pos" : "pnl-neg")}">${pnl == null ? "—" : (pnl >= 0 ? "+" : "") + "₹" + fmt(pnl)}</td>
      <td class="${ret == null ? "" : (ret >= 0 ? "pnl-pos" : "pnl-neg")}">${fmtPct(ret)}</td>
      <td>${daysAgo(p.date)}</td>
      <td><span class="pill ${verdict.cls}">${verdict.label}</span></td>
      <td><span class="pill ${action.cls}">${action.label}</span></td>
      <td>
        <button data-i="${i}" class="edit">Edit</button>
        <button data-i="${i}" class="del" style="color:var(--avoid);border-color:rgba(231,76,60,.4)">×</button>
      </td>
    </tr>`;
  }).join("");

  $("positions").querySelectorAll(".del").forEach((b) => b.addEventListener("click", (e) => {
    const i = +e.target.dataset.i;
    if (confirm("Delete " + STATE.positions[i].symbol + "?")) {
      STATE.positions.splice(i, 1);
      savePositions();
      renderAll();
    }
  }));
  $("positions").querySelectorAll(".edit").forEach((b) => b.addEventListener("click", (e) => {
    openModal(+e.target.dataset.i);
  }));
}

function renderAllocation() {
  const sectorVals = {};
  for (const p of STATE.positions) {
    const jc = STATE.jcurveBySym[p.symbol];
    const cur = jc?.price || p.avgCost;
    const v = p.qty * cur;
    const sec = STATE.jcurveSectors[p.symbol] || "Other";
    sectorVals[sec] = (sectorVals[sec] || 0) + v;
  }
  const total = Object.values(sectorVals).reduce((a, b) => a + b, 0);
  const entries = Object.entries(sectorVals).sort((a, b) => b[1] - a[1]);
  if (entries.length === 0) {
    $("alloc").innerHTML = '<p class="muted" style="font-size:12px">Add positions to see sector exposure.</p>';
    return;
  }
  $("alloc").innerHTML = entries.map(([sec, v]) => {
    const pct = total ? (v / total) * 100 : 0;
    return `<div class="alloc-row">
      <div style="flex:1">
        <div style="display:flex;justify-content:space-between">
          <span>${escape(sec)}</span>
          <span>${pct.toFixed(0)}%</span>
        </div>
        <div class="alloc-bar"><div style="width:${pct.toFixed(1)}%"></div></div>
      </div>
    </div>`;
  }).join("");
}

function renderAll() {
  renderCounters();
  renderPositions();
  renderAllocation();
  $("asOf").textContent = new Date().toLocaleString();
}

function escape(s) { return String(s ?? "").replace(/[&<>"']/g, (c) => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[c])); }

function openModal(i = -1) {
  const modal = $("modal");
  if (i >= 0) {
    const p = STATE.positions[i];
    $("fSymbol").value = p.symbol;
    $("fQty").value = p.qty;
    $("fPrice").value = p.avgCost;
    $("fDate").value = p.date || "";
    $("fNote").value = p.note || "";
    $("saveBtn").dataset.idx = i;
  } else {
    $("fSymbol").value = "";
    $("fQty").value = "";
    $("fPrice").value = "";
    $("fDate").value = new Date().toISOString().slice(0, 10);
    $("fNote").value = "";
    delete $("saveBtn").dataset.idx;
  }
  modal.classList.remove("hidden");
  $("fSymbol").focus();
}
function closeModal() { $("modal").classList.add("hidden"); }
function saveModal() {
  const sym = $("fSymbol").value.trim().toUpperCase();
  const qty = parseInt($("fQty").value, 10);
  const price = parseFloat($("fPrice").value);
  const date = $("fDate").value;
  const note = $("fNote").value;
  if (!sym || !qty || !price) { alert("Symbol, qty, and price are required."); return; }
  const rec = { symbol: sym, qty, avgCost: price, date, note };
  const idx = $("saveBtn").dataset.idx;
  if (idx != null) {
    STATE.positions[+idx] = rec;
  } else {
    STATE.positions.push(rec);
  }
  savePositions();
  closeModal();
  renderAll();
}

function exportPositions() {
  const blob = new Blob([JSON.stringify(STATE.positions, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "jcurve-portfolio-" + new Date().toISOString().slice(0, 10) + ".json";
  a.click();
  URL.revokeObjectURL(url);
}

async function init() {
  loadPositions();
  try {
    await loadJCurve();
  } catch (e) {
    console.warn("Could not load J-Curve data:", e);
  }
  $("addBtn").addEventListener("click", () => openModal());
  $("cancelBtn").addEventListener("click", closeModal);
  $("saveBtn").addEventListener("click", saveModal);
  $("exportBtn").addEventListener("click", exportPositions);
  $("modal").addEventListener("click", (e) => { if (e.target === $("modal")) closeModal(); });
  renderAll();
}

window.addEventListener("DOMContentLoaded", init);
