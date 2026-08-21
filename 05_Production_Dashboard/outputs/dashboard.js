// dashboard.js
// Renders KPI strip + well table from WELLS data (injected inline in index.html),
// draws inline sparklines on canvas, handles filter/sort, and expands per-well
// detail charts (Chart.js) on row click.

const STATUS_COLOR = { Normal: '#2FBF8F', Watch: '#E8A33D', Critical: '#E5533D' };

function fmt1(x) { return x === null || x === undefined ? '—' : x.toFixed(1); }
function fmtPct(x) { return x === null || x === undefined ? '—' : (x * 100).toFixed(0) + '%'; }
function fmt0(x) { return x === null || x === undefined ? '—' : Math.round(x).toString(); }

// ---------------------------------------------------------------- KPIs ---
function renderKPIs() {
  const totalOil = WELLS.reduce((s, w) => s + w.current_oil_bopd, 0);
  const activeWells = WELLS.length;
  const attention = WELLS.filter(w => w.status !== 'Normal').length;
  const avgWC = WELLS.reduce((s, w) => s + w.current_water_cut, 0) / WELLS.length;

  const kpis = [
    { label: 'Total Field Oil Rate', value: fmt0(totalOil), unit: 'bopd' },
    { label: 'Active Wells', value: activeWells, unit: 'wells' },
    { label: 'Wells Needing Attention', value: attention, unit: `/ ${activeWells}`, attention: attention > 0 },
    { label: 'Field Avg Water Cut', value: (avgWC * 100).toFixed(0), unit: '%' },
  ];

  document.getElementById('kpiStrip').innerHTML = kpis.map(k => `
    <div class="kpi">
      <div class="label">${k.label}</div>
      <div class="value ${k.attention ? 'attention' : ''}">${k.value}<span class="unit">${k.unit}</span></div>
    </div>`).join('');
}

// ------------------------------------------------------------ sparkline ---
function drawSparkline(canvas, series, color) {
  const ctx = canvas.getContext('2d');
  const w = canvas.width, h = canvas.height;
  ctx.clearRect(0, 0, w, h);
  const min = Math.min(...series), max = Math.max(...series);
  const range = (max - min) || 1;
  const pad = 3;
  const stepX = (w - pad * 2) / (series.length - 1);

  ctx.beginPath();
  series.forEach((v, i) => {
    const x = pad + i * stepX;
    const y = h - pad - ((v - min) / range) * (h - pad * 2);
    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  });
  ctx.strokeStyle = color;
  ctx.lineWidth = 1.6;
  ctx.stroke();

  // endpoint dot
  const lastX = pad + (series.length - 1) * stepX;
  const lastY = h - pad - ((series[series.length - 1] - min) / range) * (h - pad * 2);
  ctx.beginPath();
  ctx.arc(lastX, lastY, 2.2, 0, Math.PI * 2);
  ctx.fillStyle = color;
  ctx.fill();
}

// --------------------------------------------------------------- table ---
let currentFilter = 'All';
let currentSort = 'attention';
let expandedWell = null;
let detailChart = null;

function statusRank(s) { return { Critical: 0, Watch: 1, Normal: 2 }[s]; }

function getFilteredSorted() {
  let rows = WELLS.filter(w => currentFilter === 'All' || w.status === currentFilter);
  if (currentSort === 'attention') rows.sort((a, b) => statusRank(a.status) - statusRank(b.status) || b.current_oil_bopd - a.current_oil_bopd);
  else if (currentSort === 'oil_desc') rows.sort((a, b) => b.current_oil_bopd - a.current_oil_bopd);
  else if (currentSort === 'wc_desc') rows.sort((a, b) => b.current_water_cut - a.current_water_cut);
  else if (currentSort === 'name') rows.sort((a, b) => a.name.localeCompare(b.name));
  return rows;
}

function renderTable() {
  const rows = getFilteredSorted();
  const table = document.getElementById('wellTable');
  // remove all but header
  [...table.querySelectorAll('.well-row:not(.head)')].forEach(el => el.remove());
  [...table.querySelectorAll('.detail-panel')].forEach(el => el.remove());

  rows.forEach(w => {
    const row = document.createElement('div');
    row.className = 'well-row';
    row.dataset.name = w.name;
    row.innerHTML = `
      <div class="status-chip ${w.status}">${w.status}</div>
      <div class="well-name-cell">
        <div class="name">${w.name}</div>
        <div class="story">${w.story}</div>
      </div>
      <div class="metric">${fmt0(w.current_oil_bopd)}<span class="sub">bopd</span></div>
      <div class="metric">${fmtPct(w.current_water_cut)}<span class="sub">water</span></div>
      <div class="metric">${fmt0(w.current_gor)}<span class="sub">scf/stb</span></div>
      <div class="metric ${w.current_pump_eff === null ? 'dim' : ''}">${w.current_pump_eff === null ? '— N/A' : fmt0(w.current_pump_eff) + '%'}<span class="sub">${w.current_pump_eff === null ? 'no SRP' : 'pump eff'}</span></div>
      <div class="spark-cell"><canvas width="120" height="34"></canvas></div>
      <div class="chevron">▸</div>
    `;
    table.appendChild(row);

    const canvas = row.querySelector('canvas');
    drawSparkline(canvas, w.oil_bopd, STATUS_COLOR[w.status]);

    const detail = document.createElement('div');
    detail.className = 'detail-panel';
    detail.id = `detail-${w.name}`;
    detail.innerHTML = `
      <div class="detail-grid">
        <div class="chart-box"><canvas id="chart-${w.name}"></canvas></div>
        <div class="detail-reasons">
          <div class="h">Surveillance notes</div>
          <ul>${w.reasons.map(r => `<li>${r}</li>`).join('')}</ul>
        </div>
      </div>
    `;
    row.after(detail);

    row.addEventListener('click', () => toggleDetail(w));
  });
}

function toggleDetail(w) {
  const allRows = document.querySelectorAll('.well-row:not(.head)');
  const allPanels = document.querySelectorAll('.detail-panel');

  if (expandedWell === w.name) {
    allPanels.forEach(p => p.classList.remove('open'));
    allRows.forEach(r => r.classList.remove('expanded'));
    expandedWell = null;
    if (detailChart) { detailChart.destroy(); detailChart = null; }
    return;
  }

  allPanels.forEach(p => p.classList.remove('open'));
  allRows.forEach(r => r.classList.remove('expanded'));
  if (detailChart) { detailChart.destroy(); detailChart = null; }

  expandedWell = w.name;
  const panel = document.getElementById(`detail-${w.name}`);
  const row = document.querySelector(`.well-row[data-name="${w.name}"]`);
  panel.classList.add('open');
  row.classList.add('expanded');

  const ctx = document.getElementById(`chart-${w.name}`).getContext('2d');
  const weeks = w.oil_bopd.map((_, i) => `W${i + 1}`);
  const datasets = [
    { label: 'Oil (bopd)', data: w.oil_bopd, borderColor: '#4FA3D1', backgroundColor: 'transparent', yAxisID: 'y', tension: 0.25, pointRadius: 0, borderWidth: 2 },
    { label: 'Water cut (%)', data: w.water_cut.map(v => v * 100), borderColor: '#E8A33D', backgroundColor: 'transparent', yAxisID: 'y1', tension: 0.25, pointRadius: 0, borderWidth: 1.6 },
  ];
  if (w.pump_eff_pct.some(v => v !== null)) {
    datasets.push({ label: 'Pump eff. (%)', data: w.pump_eff_pct, borderColor: '#2FBF8F', backgroundColor: 'transparent', yAxisID: 'y1', tension: 0.25, pointRadius: 0, borderWidth: 1.6, borderDash: [4, 3] });
  }

  detailChart = new Chart(ctx, {
    type: 'line',
    data: { labels: weeks, datasets },
    options: {
      responsive: true, maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { labels: { color: '#7C8896', font: { family: 'IBM Plex Mono', size: 10 }, boxWidth: 12 } },
        tooltip: { backgroundColor: '#161D25', titleColor: '#E7ECF2', bodyColor: '#E7ECF2', borderColor: '#232C37', borderWidth: 1 },
      },
      scales: {
        x: { ticks: { color: '#4E5A68', maxTicksLimit: 8, font: { size: 10 } }, grid: { color: '#1C2531' } },
        y: { position: 'left', ticks: { color: '#4FA3D1', font: { size: 10 } }, grid: { color: '#1C2531' }, title: { display: true, text: 'bopd', color: '#4FA3D1', font: { size: 10 } } },
        y1: { position: 'right', ticks: { color: '#E8A33D', font: { size: 10 } }, grid: { display: false }, title: { display: true, text: '%', color: '#E8A33D', font: { size: 10 } }, min: 0, max: 100 },
      },
    },
  });
}

// -------------------------------------------------------------- events ---
document.querySelectorAll('.filter-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentFilter = btn.dataset.filter;
    expandedWell = null;
    renderTable();
  });
});

document.getElementById('sortSelect').addEventListener('change', (e) => {
  currentSort = e.target.value;
  expandedWell = null;
  renderTable();
});

renderKPIs();
renderTable();
