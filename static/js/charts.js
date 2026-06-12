(function () {
  const colors = ["#2f8f83", "#e0a53b", "#6c7bd9", "#d86969", "#5aa0c8", "#8a9a5b"];

  function makeChart(id, config) {
    const element = document.getElementById(id);
    if (!element || typeof Chart === "undefined") {
      return;
    }
    return new Chart(element, config);
  }

  if (window.dashboardChartData) {
    makeChart("dashboardChart", {
      type: "line",
      data: {
        labels: window.dashboardChartData.labels,
        datasets: [{
          label: "รายจ่าย",
          data: window.dashboardChartData.values,
          borderColor: "#2f8f83",
          backgroundColor: "rgba(47, 143, 131, 0.14)",
          fill: true,
          tension: 0.35
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } }
      }
    });
  }

  if (window.analyticsData) {
    const data = window.analyticsData;

    makeChart("restaurantPie", {
      type: "pie",
      data: {
        labels: data.pie.labels,
        datasets: [{ data: data.pie.values, backgroundColor: colors }]
      },
      options: { responsive: true }
    });

    makeChart("monthlyBar", {
      type: "bar",
      data: {
        labels: data.bar.labels,
        datasets: [{ label: "บาท", data: data.bar.values, backgroundColor: "#6c7bd9" }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } }
      }
    });

    makeChart("dailyLine", {
      type: "line",
      data: {
        labels: data.line.labels,
        datasets: [{
          label: "บาท",
          data: data.line.values,
          borderColor: "#e0a53b",
          backgroundColor: "rgba(224, 165, 59, 0.16)",
          fill: true,
          tension: 0.35
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } }
      }
    });
  }
})();
