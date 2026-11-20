/**
 * StockPulse - Interactive Client Script
 */

document.addEventListener('DOMContentLoaded', function () {
    // Mobile sidebar toggle
    const toggleBtn = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', function () {
            sidebar.classList.toggle('show');
        });
    }

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Quick Trade Modal Setup
    const tradeModal = document.getElementById('tradeModal');
    if (tradeModal) {
        tradeModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const stockId = button.getAttribute('data-stock-id');
            const symbol = button.getAttribute('data-symbol');
            const name = button.getAttribute('data-name');
            const price = parseFloat(button.getAttribute('data-price'));
            const action = button.getAttribute('data-action') || 'buy';
            const owned = parseInt(button.getAttribute('data-owned') || '0', 10);

            const form = document.getElementById('tradeModalForm');
            const modalTitle = document.getElementById('tradeModalTitle');
            const symbolEl = document.getElementById('modalStockSymbol');
            const nameEl = document.getElementById('modalStockName');
            const priceEl = document.getElementById('modalStockPrice');
            const stockIdInput = document.getElementById('modalStockId');
            const qtyInput = document.getElementById('modalQuantity');
            const totalEl = document.getElementById('modalTotalAmount');
            const submitBtn = document.getElementById('modalSubmitBtn');
            const ownedContainer = document.getElementById('modalOwnedContainer');
            const ownedCountEl = document.getElementById('modalOwnedCount');

            stockIdInput.value = stockId;
            symbolEl.textContent = symbol;
            nameEl.textContent = name;
            priceEl.textContent = '₹' + price.toLocaleString('en-IN', { minimumFractionDigits: 2 });
            qtyInput.value = 1;

            if (action === 'buy') {
                form.action = '/trade/buy';
                modalTitle.textContent = `Buy ${symbol}`;
                submitBtn.className = 'btn btn-success px-4';
                submitBtn.textContent = 'Confirm Buy';
                ownedContainer.classList.add('d-none');
            } else {
                form.action = '/trade/sell';
                modalTitle.textContent = `Sell ${symbol}`;
                submitBtn.className = 'btn btn-danger px-4';
                submitBtn.textContent = 'Confirm Sell';
                ownedContainer.classList.remove('d-none');
                ownedCountEl.textContent = owned;
                qtyInput.max = owned;
            }

            function updateTotal() {
                const qty = parseInt(qtyInput.value, 10) || 0;
                const total = (qty * price).toLocaleString('en-IN', { minimumFractionDigits: 2 });
                totalEl.textContent = '₹' + total;
            }

            qtyInput.oninput = updateTotal;
            updateTotal();
        });
    }

    // Watchlist Toggle via AJAX
    document.querySelectorAll('.btn-watchlist-toggle').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const stockId = this.getAttribute('data-stock-id');
            const icon = this.querySelector('i');
            
            fetch(`/api/watchlist/toggle/${stockId}`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.in_watchlist) {
                    icon.classList.remove('bi-star');
                    icon.classList.add('bi-star-fill', 'text-warning');
                    this.title = 'Remove from Watchlist';
                } else {
                    icon.classList.remove('bi-star-fill', 'text-warning');
                    icon.classList.add('bi-star');
                    this.title = 'Add to Watchlist';
                }
            })
            .catch(err => console.error('Watchlist toggle error:', err));
        });
    });
});
