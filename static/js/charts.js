/**
 * StockPulse - Chart.js Rendering Utilities
 */

const ChartColors = [
    '#3a86ff', '#00b4d8', '#10b981', '#f59e0b', '#ec4899', 
    '#8b5cf6', '#14b8a6', '#6366f1', '#f97316', '#06b6d4'
];

function initPortfolioCharts(sectorData, assetData) {
    // 1. Sector Allocation Donut Chart
    const sectorCtx = document.getElementById('sectorChart');
    if (sectorCtx && Object.keys(sectorData).length > 0) {
        const labels = Object.keys(sectorData);
        const values = Object.values(sectorData);

        new Chart(sectorCtx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: ChartColors.slice(0, labels.length),
                    borderColor: '#1e293b',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#94a3b8', font: { size: 12 }, padding: 15 }
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                const val = context.raw || 0;
                                return `${context.label}: ₹${val.toLocaleString('en-IN')}`;
                            }
                        }
                    }
                },
                cutout: '70%'
            }
        });
    }

    // 2. Asset Allocation Bar Chart
    const assetCtx = document.getElementById('assetChart');
    if (assetCtx && Object.keys(assetData).length > 0) {
        const labels = Object.keys(assetData);
        const values = Object.values(assetData);

        new Chart(assetCtx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Holding Value (₹)',
                    data: values,
                    backgroundColor: '#3a86ff',
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        ticks: { color: '#94a3b8' },
                        grid: { display: false }
                    },
                    y: {
                        ticks: {
                            color: '#94a3b8',
                            callback: function(value) {
                                return '₹' + value.toLocaleString('en-IN');
                            }
                        },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' }
                    }
                }
            }
        });
    }
}

function initStockHistoryChart(canvasId, labels, prices, symbol) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const isPositive = prices.length >= 2 ? (prices[prices.length - 1] >= prices[0]) : true;
    const strokeColor = isPositive ? '#10b981' : '#ef4444';
    const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, isPositive ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)');
    gradient.addColorStop(1, 'rgba(15, 23, 42, 0)');

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: `${symbol} Price (₹)`,
                data: prices,
                borderColor: strokeColor,
                backgroundColor: gradient,
                borderWidth: 2.5,
                fill: true,
                tension: 0.3,
                pointRadius: 3,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function (ctx) {
                            return `Price: ₹${ctx.raw.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#94a3b8', maxTicksLimit: 7 },
                    grid: { display: false }
                },
                y: {
                    ticks: {
                        color: '#94a3b8',
                        callback: function(value) { return '₹' + value.toLocaleString('en-IN'); }
                    },
                    grid: { color: 'rgba(255, 255, 255, 0.05)' }
                }
            }
        }
    });
}
