const STATE = {
  data: null,
  filter: { status: "", group: "", search: "" },
  selected: null,
};

const $ = (id) => document.getElementById(id);
const escape = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
}[c]));

const STATUS_LABEL = {
  covered: "✅ Covered",
  partial: "⚠ Partial",
  missing: "❌ Missing",
};

async function load() {
  $("asOf").textContent = new Date().toLocaleString();
  const r = await fetch("data.json", { cache: "no-store" });
  STATE.data = await r.json();
  populateGroupFilter();
  render();
  if (STATE.data.as_of) $("footerDate").textContent = STATE.data.as_of;
}

function populateGroupFilter() {
  const sel = $("group");
  const groups = STATE.data.sections.map((s) => s.group);
  sel.innerHTML = '<option value="">All groups</option>' +
    groups.map((g) => `<option value="${escape(g)}">${escape(g)}</option>`).join("");
}

function passesFilter(s) {
  if (STATE.filter.status && s.status !== STATE.filter.status) return false;
  if (STATE.filter.group && s._group !== STATE.filter.group) return false;
  const q = STATE.filter.search.toLowerCase();
  if (q && !s.name.toLowerCase().includes(q)) return false;
  return true;
}

function render() {
  const all = [];
  for (const sec of STATE.data.sections) {
    for (const sub of sec.subsectors) {
      sub._group = sec.group;
      all.push(sub);
    }
  }
  const filtered = all.filter(passesFilter);

  $("cCovered").textContent = all.filter((s) => s.status === "covered").length;
  $("cPartial").textContent = all.filter((s) => s.status === "partial").length;
  $("cMissing").textContent = all.filter((s) => s.status === "missing").length;
  $("cUniverse").textContent = "165";

  const tbody = $("rows");
  let html = "";
  for (const sec of STATE.data.sections) {
    const subs = sec.subsectors.filter((s) => passesFilter(s));
    if (subs.length === 0) continue;
    html += `<tr class="group-row"><td colspan="4">${escape(sec.group)} · ${subs.length} sub-sector${subs.length > 1 ? "s" : ""}</td></tr>`;
    for (const sub of subs) {
      const tickers = (sub.tickers || []).map((t) => `<span class="ticker-pill">${escape(t)}</span>`).join(" ");
      const missing = (sub.missing || []).map((t) => `<span class="missing-pill">${escape(t)}</span>`).join(" ");
      const sel = sub.name === STATE.selected ? " selected" : "";
      html += `
        <tr class="data-row${sel}" data-name="${escape(sub.name)}">
          <td><div class="sub-name">${escape(sub.name)}</div></td>
          <td><span class="status-pill ${sub.status}">${escape(STATUS_LABEL[sub.status])}</span></td>
          <td>${tickers || '<span class="muted">none</span>'}</td>
          <td>${missing || '<span class="muted">—</span>'}</td>
        </tr>
      `;
    }
  }
  tbody.innerHTML = html;
  tbody.querySelectorAll("tr.data-row").forEach((tr) => {
    tr.addEventListener("click", () => selectRow(tr.dataset.name));
  });
}

function selectRow(name) {
  STATE.selected = name;
  document.querySelectorAll("#rows tr.data-row").forEach((tr) => {
    tr.classList.toggle("selected", tr.dataset.name === name);
  });
  const sub = STATE.data.sections
    .flatMap((s) => s.subsectors)
    .find((s) => s.name === name);
  if (!sub) return;
  const t = $("thesis");
  t.innerHTML = `
    <h3>${escape(sub.name)}</h3>
    <div class="muted">${escape(sub._group)}</div>
    <div class="row"><b>Status</b><span><span class="status-pill ${sub.status}">${escape(STATUS_LABEL[sub.status])}</span></span></div>
    <div class="row"><b>Your tickers</b><span style="text-align:right">${(sub.tickers || []).length}</span></div>
    <div class="row"><b>Missing tickers</b><span style="text-align:right">${(sub.missing || []).length}</span></div>
    <div style="margin-top:12px">
      <b class="muted" style="font-size:11px;letter-spacing:1px">YOUR TICKERS</b>
      <div style="margin-top:6px">${(sub.tickers || []).map((x) => `<span class="ticker-pill">${escape(x)}</span>`).join(" ") || '<span class="muted">none</span>'}</div>
    </div>
    <div style="margin-top:12px">
      <b class="muted" style="font-size:11px;letter-spacing:1px">SUGGESTED ADDS</b>
      <div style="margin-top:6px">${(sub.missing || []).map((x) => `<span class="missing-pill">${escape(x)}</span>`).join(" ") || '<span class="muted">none</span>'}</div>
    </div>
  `;
}

function bindFilters() {
  $("status").addEventListener("change", (e) => { STATE.filter.status = e.target.value; render(); });
  $("group").addEventListener("change", (e) => { STATE.filter.group = e.target.value; render(); });
  $("search").addEventListener("input", (e) => { STATE.filter.search = e.target.value; render(); });
}

window.addEventListener("DOMContentLoaded", () => {
  bindFilters();
  load();
});
