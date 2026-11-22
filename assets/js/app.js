document.addEventListener('click', function (event) {
    const target = event.target.closest('[data-confirm]');
    if (target && !window.confirm(target.dataset.confirm)) {
        event.preventEvent?.();
        event.preventDefault();
    }
});

const sidebar = document.querySelector('.sidebar');
document.querySelector('.sidebar-toggle')?.addEventListener('click', () => sidebar?.classList.add('open'));
document.querySelector('.sidebar-close')?.addEventListener('click', () => sidebar?.classList.remove('open'));

const portfolioData = document.querySelector('#portfolio-data');
const portfolioCanvas = document.querySelector('#portfolioChart');
if (portfolioData && portfolioCanvas && window.Chart) {
    const data = JSON.parse(portfolioData.textContent);
    new Chart(portfolioCanvas, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Current Value',
                data: data.values,
                backgroundColor: '#B8955E',
                borderRadius: 4,
                maxBarThickness: 42
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { display: false }, ticks: { color: '#5B6B82' } },
                y: { beginAtZero: true, grid: { color: '#ECEAE3' }, ticks: { color: '#5B6B82' } }
            }
        }
    });
}
