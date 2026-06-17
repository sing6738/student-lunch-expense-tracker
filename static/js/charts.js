(function () {
  // Purple theme color scale
  const colors = [
    "#8b5cf6", // purple-500
    "#c4b5fd", // purple-400
    "#7c3aed", // purple-600
    "#d8b4fe", // purple-200
    "#a78bfa", // purple-300
    "#4c1d95", // purple-900
    "#6d28d9"  // purple-700
  ];

  const defaultOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: {
      duration: 2000,
      easing: 'easeOutQuart'
    },
    plugins: {
      legend: {
        labels: {
          color: 'rgba(255, 255, 255, 0.7)',
          font: { family: 'Sarabun' }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: { color: 'rgba(255, 255, 255, 0.05)' },
        ticks: { color: 'rgba(255, 255, 255, 0.5)' }
      },
      x: {
        grid: { display: false },
        ticks: { color: 'rgba(255, 255, 255, 0.5)' }
      }
    }
  };

  function makeChart(id, config) {
    const element = document.getElementById(id);
    if (!element || typeof Chart === "undefined") {
      return;
    }
    
    // Improved merge: only apply defaults for missing keys at the top level
    // and specifically handle nested objects like plugins and scales if needed.
    // For simplicity here, we'll just ensure defaultOptions are the base.
    const mergedOptions = JSON.parse(JSON.stringify(defaultOptions));
    if (config.options) {
      Object.keys(config.options).forEach(key => {
        if (typeof config.options[key] === 'object' && config.options[key] !== null && !Array.isArray(config.options[key])) {
          mergedOptions[key] = Object.assign({}, mergedOptions[key], config.options[key]);
        } else {
          mergedOptions[key] = config.options[key];
        }
      });
    }
    config.options = mergedOptions;
    
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
          borderColor: "#8b5cf6",
          backgroundColor: "rgba(139, 92, 246, 0.15)",
          fill: true,
          tension: 0.4,
          pointBackgroundColor: "#8b5cf6",
          pointBorderColor: "#fff",
          pointHoverRadius: 6
        }]
      },
      options: {
        maintainAspectRatio: true,
        plugins: { legend: { display: false } }
      }
    });
  }

  if (window.analyticsData) {
    const data = window.analyticsData;

    makeChart("restaurantPie", {
      type: "doughnut", // Switched to doughnut for modern feel
      data: {
        labels: data.pie.labels,
        datasets: [{ 
          data: data.pie.values, 
          backgroundColor: colors,
          borderWidth: 0,
          hoverOffset: 15
        }]
      },
      options: {
        cutout: '70%',
        plugins: {
          legend: { position: 'bottom' }
        }
      }
    });

    makeChart("monthlyBar", {
      type: "bar",
      data: {
        labels: data.bar.labels,
        datasets: [{ 
          label: "บาท", 
          data: data.bar.values, 
          backgroundColor: "rgba(139, 92, 246, 0.6)",
          borderRadius: 8,
          hoverBackgroundColor: "#8b5cf6"
        }]
      },
      options: {
        plugins: { legend: { display: false } }
      }
    });

    makeChart("dailyLine", {
      type: "line",
      data: {
        labels: data.line.labels,
        datasets: [{
          label: "บาท",
          data: data.line.values,
          borderColor: "#c4b5fd",
          backgroundColor: "rgba(196, 181, 253, 0.12)",
          fill: true,
          tension: 0.4,
          pointRadius: 0,
          pointHoverRadius: 5
        }]
      },
      options: {
        plugins: { legend: { display: false } }
      }
    });
  }
})();
