/* ═══════════════════════════════════════════════════════════════
   FieldSense — Frontend Logic
   ═══════════════════════════════════════════════════════════════ */

const form    = document.getElementById('predict-form');
const btn     = document.getElementById('predict-btn');
const label   = document.getElementById('btn-label');
const spinner = document.getElementById('btn-spinner');
const section = document.getElementById('results-section');

let chart = null;

/* ── Form submit ──────────────────────────────────────────────── */
form.addEventListener('submit', async (e) => {
  e.preventDefault();

  const payload = {
    x: parseFloat(document.getElementById('input-x').value),
    H: parseFloat(document.getElementById('input-H').value),
    d: parseFloat(document.getElementById('input-d').value),
    V: parseFloat(document.getElementById('input-V').value),
  };

  setLoading(true);

  try {
    const res = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (data.error) { alert('Error: ' + data.error); return; }
    showResults(data);
  } catch (err) {
    alert('Request failed — ' + err.message);
  } finally {
    setLoading(false);
  }
});

function setLoading(on) {
  btn.classList.toggle('loading', on);
  label.textContent = on ? 'Computing…' : 'Run Prediction';
  spinner.hidden = !on;
  document.querySelector('.btn-icon').style.display = on ? 'none' : '';
}

/* ── Render results ───────────────────────────────────────────── */
function showResults(d) {
  section.hidden = false;
  section.classList.remove('fade-in');
  void section.offsetHeight;
  section.classList.add('fade-in');

  // ML card
  animateNumber('metric-ml-val', d.E_ml, 4);
  document.getElementById('metric-model-name').textContent = d.ml_name;
  setBadge('badge-ml', d.safe_ml);

  // Analytical card
  animateNumber('metric-an-val', d.E_an, 4);
  setBadge('badge-an', d.safe_an);

  // Info card
  document.getElementById('info-req').textContent  = d.r_eq.toFixed(6) + ' m';
  const diff = Math.abs(d.E_ml - d.E_an);
  document.getElementById('info-diff').textContent = diff.toFixed(5) + ' kV/m';
  const pct = d.E_an !== 0 ? ((diff / d.E_an) * 100).toFixed(3) : '—';
  document.getElementById('info-pct').textContent  = pct + '%';

  drawChart(d);

  // Smooth scroll to results
  section.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/* ── Animated number counter ──────────────────────────────────── */
function animateNumber(elId, target, decimals) {
  const el = document.getElementById(elId);
  const duration = 600;
  const start = performance.now();
  const from = parseFloat(el.textContent) || 0;

  function tick(now) {
    const t = Math.min((now - start) / duration, 1);
    const ease = 1 - Math.pow(1 - t, 3);          // ease-out cubic
    el.textContent = (from + (target - from) * ease).toFixed(decimals);
    if (t < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

/* ── Badge helper ─────────────────────────────────────────────── */
function setBadge(id, safe) {
  const el = document.getElementById(id);
  el.className = 'metric-badge ' + (safe ? 'badge-safe' : 'badge-danger');
  el.textContent = safe ? '✓ Within WHO Limit' : '⚠ Exceeds WHO Limit';
}

/* ── Chart ────────────────────────────────────────────────────── */
function drawChart(d) {
  const ctx = document.getElementById('profile-chart').getContext('2d');
  if (chart) chart.destroy();

  const whoLine = d.profile_x.map(() => 5.0);

  chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: d.profile_x,
      datasets: [
        {
          label: 'Analytical',
          data: d.profile_an,
          borderColor: '#fbbf24',
          backgroundColor: createGradient(ctx, '#fbbf24', .12),
          borderWidth: 2.5,
          pointRadius: 0,
          pointHoverRadius: 4,
          tension: .35,
          fill: true,
        },
        {
          label: 'ML — ' + d.ml_name,
          data: d.profile_ml,
          borderColor: '#22d3ee',
          backgroundColor: createGradient(ctx, '#22d3ee', .1),
          borderWidth: 2.5,
          pointRadius: 0,
          pointHoverRadius: 4,
          tension: .35,
          fill: true,
        },
        {
          label: 'WHO Limit (5 kV/m)',
          data: whoLine,
          borderColor: '#fb7185',
          borderWidth: 1.8,
          borderDash: [8, 5],
          pointRadius: 0,
          fill: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      animation: { duration: 800, easing: 'easeOutQuart' },
      plugins: {
        legend: {
          position: 'top',
          align: 'end',
          labels: {
            color: '#8892b0',
            font: { family: "'Inter', sans-serif", size: 12, weight: '500' },
            boxWidth: 14,
            boxHeight: 3,
            useBorderRadius: true,
            borderRadius: 2,
            padding: 16,
          },
        },
        tooltip: {
          backgroundColor: 'rgba(15, 21, 41, .95)',
          titleColor: '#f1f5f9',
          bodyColor: '#cbd5e1',
          borderColor: 'rgba(99,102,241,.25)',
          borderWidth: 1,
          padding: 12,
          cornerRadius: 10,
          titleFont: { family: "'Inter'", weight: '600', size: 13 },
          bodyFont: { family: "'JetBrains Mono'", size: 12 },
          callbacks: {
            title: (items) => 'x = ' + items[0].label + ' m',
            label: (item) => ' ' + item.dataset.label + ':  ' + Number(item.raw).toFixed(4) + ' kV/m',
          },
        },
      },
      scales: {
        x: {
          title: {
            display: true,
            text: 'Lateral Distance x (m)',
            color: '#8892b0',
            font: { size: 12, weight: '500' },
          },
          ticks: { color: '#4a5578', maxTicksLimit: 13, font: { size: 11 } },
          grid: { color: 'rgba(255,255,255,.03)', drawBorder: false },
        },
        y: {
          title: {
            display: true,
            text: 'Eᵥ (kV/m)',
            color: '#8892b0',
            font: { size: 12, weight: '500' },
          },
          ticks: { color: '#4a5578', font: { size: 11 } },
          grid: { color: 'rgba(255,255,255,.03)', drawBorder: false },
          beginAtZero: true,
        },
      },
    },
  });
}

/* Create a vertical gradient fill for chart datasets */
function createGradient(ctx, hex, alpha) {
  const g = ctx.createLinearGradient(0, 0, 0, 380);
  g.addColorStop(0, hexToRgba(hex, alpha));
  g.addColorStop(1, hexToRgba(hex, 0));
  return g;
}

function hexToRgba(hex, a) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r},${g},${b},${a})`;
}
