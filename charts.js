/* charts.js — Dark Purple Theme */

// Shared Chart.js defaults for dark theme
Chart.defaults.color = '#6b7280';
Chart.defaults.borderColor = 'rgba(46,41,82,0.8)';
Chart.defaults.font.family = "'Sarabun', 'Inter', sans-serif";

const PALETTE = [
  '#8b5cf6', '#a78bfa', '#6d28d9',
  '#ec4899', '#38bdf8', '#34d399', '#fbbf24'
];

const gridOpts = {
  color: 'rgba(46,41,82,0.7)',
  drawBorder: false,
};

const tickOpts = {
  color: '#6b7280',
  font: { size: 11 },
};

const tooltipOpts = {
  backgroundColor: '#221e38',
  borderColor: '#2e2952',
  borderWidth: 1,
  titleColor: '#ede9fe',
  bodyColor: '#9ca3af',
  padding: 10,
  cornerRadius: 8,
  callbacks: {
    label: (ctx) => ` ${Number(ctx.raw).toLocaleString('th-TH', { minimumFractionDigits: 2 })} บาท`,
  },
};

/* ── Dashboard: bar chart (7-day) ── */
const dashCanvas = document.getElementById('dashboardChart');
if (dashCanvas && window.dashboardChartData) {
  const d = window.dashboardChartData;
  new Chart(dashCanvas, {
    type: 'bar',
    data: {
      labels: d.labels,
      datasets: [{
        label: 'รายจ่าย (บาท)',
        data: d.values,
        backgroundColor: 'rgba(139,92,246,0.25)',
        borderColor: '#8b5cf6',
        borderWidth: 2,
        borderRadius: 6,
        borderSkipped: false,
        hoverBackgroundColor: 'rgba(139,92,246,0.45)',
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { display: false },
        tooltip: tooltipOpts,
      },
      scales: {
        x: { grid: gridOpts, ticks: tickOpts },
        y: {
          grid: gridOpts,
          ticks: { ...tickOpts, callback: (v) => v.toLocaleString() },
          beginAtZero: true,
        },
      },
    },
  });
}

/* ── Analytics: Pie (restaurant share) ── */
const pieCanvas = document.getElementById('restaurantPie');
if (pieCanvas && window.analyticsData) {
  const pie = window.analyticsData.pie;
  new Chart(pieCanvas, {
    type: 'doughnut',
    data: {
      labels: pie.labels,
      datasets: [{
        data: pie.values,
        backgroundColor: PALETTE,
        borderColor: '#19162b',
        borderWidth: 3,
        hoverOffset: 6,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: { color: '#9ca3af', boxWidth: 12, padding: 14, font: { size: 11 } },
        },
        tooltip: {
          ...tooltipOpts,
          callbacks: {
            label: (ctx) => ` ${Number(ctx.raw).toLocaleString('th-TH', { minimumFractionDigits: 2 })} บาท`,
          },
        },
      },
      cutout: '60%',
    },
  });
}

/* ── Analytics: Bar (monthly) ── */
const barCanvas = document.getElementById('monthlyBar');
if (barCanvas && window.analyticsData) {
  const bar = window.analyticsData.bar;
  new Chart(barCanvas, {
    type: 'bar',
    data: {
      labels: bar.labels,
      datasets: [{
        label: 'รวม (บาท)',
        data: bar.values,
        backgroundColor: 'rgba(167,139,250,0.28)',
        borderColor: '#a78bfa',
        borderWidth: 2,
        borderRadius: 6,
        borderSkipped: false,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: tooltipOpts,
      },
      scales: {
        x: { grid: { display: false }, ticks: tickOpts },
        y: {
          grid: gridOpts,
          ticks: { ...tickOpts, callback: (v) => v.toLocaleString() },
          beginAtZero: true,
        },
      },
    },
  });
}

/* ── Analytics: Line (daily trend) ── */
const lineCanvas = document.getElementById('dailyLine');
if (lineCanvas && window.analyticsData) {
  const line = window.analyticsData.line;
  new Chart(lineCanvas, {
    type: 'line',
    data: {
      labels: line.labels,
      datasets: [{
        label: 'รายจ่าย (บาท)',
        data: line.values,
        borderColor: '#8b5cf6',
        backgroundColor: 'rgba(139,92,246,0.12)',
        borderWidth: 2,
        pointRadius: 3,
        pointBackgroundColor: '#8b5cf6',
        fill: true,
        tension: 0.35,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: tooltipOpts,
      },
      scales: {
        x: { grid: { display: false }, ticks: tickOpts },
        y: {
          grid: gridOpts,
          ticks: { ...tickOpts, callback: (v) => v.toLocaleString() },
          beginAtZero: true,
        },
      },
    },
  });
}
