document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".js-dashboard-filter-select").forEach(function (element) {
    if (typeof TomSelect !== "undefined" && !element.tomselect) {
      new TomSelect(element, {
        create: false,
        allowEmptyOption: true,
        controlInput: null,
        searchField: [],
        maxOptions: null,
      });
    }
  });

  const dataElement = document.getElementById("dashboardChartsData");

  if (!dataElement || typeof Chart === "undefined") {
    return;
  }

  const dashboardData = JSON.parse(dataElement.textContent);

  const gridColor = "rgba(255, 255, 255, 0.08)";
  const tickColor = "rgba(229, 231, 235, 0.62)";
  const labelColor = "rgba(229, 231, 235, 0.88)";

  const tooltipOptions = {
    backgroundColor: "rgba(15, 23, 42, 0.96)",
    titleColor: "#ffffff",
    bodyColor: "rgba(229, 231, 235, 0.88)",
    borderColor: "rgba(255, 255, 255, 0.10)",
    borderWidth: 1,
    padding: 12,
    displayColors: true,
  };

  function criarGradiente(ctx, corInicio, corFim) {
    const gradient = ctx.createLinearGradient(0, 0, 0, 360);
    gradient.addColorStop(0, corInicio);
    gradient.addColorStop(1, corFim);
    return gradient;
  }

  function formatarMoeda(valor) {
    return new Intl.NumberFormat("pt-BR", {
      style: "currency",
      currency: "BRL",
    }).format(valor || 0);
  }

  const mainCanvas = document.getElementById("dashboardMainChart");

  if (mainCanvas) {
    const ctx = mainCanvas.getContext("2d");

    new Chart(ctx, {
      type: "line",
      data: {
        labels: dashboardData.resumoLabels,
        datasets: [
          {
            label: "Vendas",
            data: dashboardData.resumoVendas,
            borderColor: "#22d3ee",
            backgroundColor: criarGradiente(
              ctx,
              "rgba(34, 211, 238, 0.28)",
              "rgba(34, 211, 238, 0.00)"
            ),
            fill: true,
            tension: 0.42,
            borderWidth: 3,
            pointRadius: 4,
            pointHoverRadius: 6,
          },
          {
            label: "Despesas",
            data: dashboardData.resumoDespesas,
            borderColor: "#ff2fcf",
            backgroundColor: criarGradiente(
              ctx,
              "rgba(255, 47, 207, 0.22)",
              "rgba(255, 47, 207, 0.00)"
            ),
            fill: true,
            tension: 0.42,
            borderWidth: 3,
            pointRadius: 4,
            pointHoverRadius: 6,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: "index",
          intersect: false,
        },
        plugins: {
          legend: {
            labels: {
              color: labelColor,
              usePointStyle: true,
              boxWidth: 8,
              boxHeight: 8,
            },
          },
          tooltip: {
            ...tooltipOptions,
            callbacks: {
              label: function (context) {
                return `${context.dataset.label}: ${formatarMoeda(context.raw)}`;
              },
            },
          },
        },
        scales: {
          x: {
            grid: {
              color: gridColor,
            },
            ticks: {
              color: tickColor,
            },
          },
          y: {
            beginAtZero: true,
            grid: {
              color: gridColor,
            },
            ticks: {
              color: tickColor,
              callback: function (value) {
                return formatarMoeda(value);
              },
            },
          },
        },
      },
    });
  }

  const serviceBarCanvas = document.getElementById("dashboardServiceBarChart");

  if (serviceBarCanvas) {
    const ctx = serviceBarCanvas.getContext("2d");

    new Chart(ctx, {
      type: "bar",
      data: {
        labels: dashboardData.servicosLabels,
        datasets: [
          {
            label: "Serviços",
            data: dashboardData.servicosData,
            backgroundColor: criarGradiente(
              ctx,
              "rgba(34, 211, 238, 0.92)",
              "rgba(168, 85, 247, 0.52)"
            ),
            borderRadius: 10,
            borderSkipped: false,
            maxBarThickness: 34,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false,
          },
          tooltip: tooltipOptions,
        },
        scales: {
          x: {
            grid: {
              display: false,
            },
            ticks: {
              color: tickColor,
            },
          },
          y: {
            beginAtZero: true,
            precision: 0,
            grid: {
              color: gridColor,
            },
            ticks: {
              color: tickColor,
              stepSize: 1,
            },
          },
        },
      },
    });
  }

  const statusCanvas = document.getElementById("dashboardStatusChart");

  if (statusCanvas) {
    const hasData = dashboardData.servicosStatusData.some(function (value) {
      return value > 0;
    });

    new Chart(statusCanvas, {
      type: "doughnut",
      data: {
        labels: hasData ? dashboardData.servicosStatusLabels : ["Sem dados"],
        datasets: [
          {
            data: hasData ? dashboardData.servicosStatusData : [1],
            backgroundColor: hasData
              ? ["#22d3ee", "#a855f7", "#ff2fcf", "#24c16b", "#fb923c", "#3b82f6"]
              : ["rgba(255, 255, 255, 0.10)"],
            borderColor: "rgba(15, 23, 42, 0.90)",
            borderWidth: 4,
            hoverOffset: 6,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: "68%",
        plugins: {
          legend: {
            position: "bottom",
            labels: {
              color: labelColor,
              usePointStyle: true,
              boxWidth: 8,
              boxHeight: 8,
              padding: 14,
            },
          },
          tooltip: tooltipOptions,
        },
      },
    });
  }

  const stockCanvas = document.getElementById("dashboardStockChart");

  if (stockCanvas) {
    const hasData = dashboardData.estoqueData.some(function (value) {
      return value > 0;
    });

    new Chart(stockCanvas, {
      type: "doughnut",
      data: {
        labels: hasData ? dashboardData.estoqueLabels : ["Sem dados"],
        datasets: [
          {
            data: hasData ? dashboardData.estoqueData : [1],
            backgroundColor: hasData
              ? ["#22d3ee", "#24c16b", "#ff2fcf"]
              : ["rgba(255, 255, 255, 0.10)"],
            borderColor: "rgba(15, 23, 42, 0.90)",
            borderWidth: 4,
            hoverOffset: 6,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: "66%",
        plugins: {
          legend: {
            position: "bottom",
            labels: {
              color: labelColor,
              usePointStyle: true,
              boxWidth: 8,
              boxHeight: 8,
              padding: 14,
            },
          },
          tooltip: tooltipOptions,
        },
      },
    });
  }
});