document.addEventListener('DOMContentLoaded', function () {

    // ==========================================================================
    // Data Retrieval
    // Safely parse the JSON data embedded in the HTML.
    // ==========================================================================
    const initialDataElement = document.getElementById('initial-data');
    if (!initialDataElement) {
        console.error('Initial data script tag not found!');
        return;
    }
    const initialData = JSON.parse(initialDataElement.textContent);

    // ==========================================================================
    // Debounce Helper Function
    // ==========================================================================
    function debounce(func, delay) {
        let timeoutId;
        return function(...args) {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {
                func.apply(this, args);
            }, delay);
        };
    }

    // ==========================================================================
    // Chart.js Global Configuration
    // ==========================================================================
    Chart.defaults.color = '#9CA3AF';
    Chart.defaults.borderColor = '#374151';

    // ==========================================================================
    // DOM Element Selectors
    // ==========================================================================
    const filters = {
        search: document.getElementById('search-influencer'),
        brand: document.getElementById('brand-filter'),
        platform: document.getElementById('platform-filter'),
        category: document.getElementById('category-filter'),
    };

    const kpiElements = {
        revenue: document.getElementById('kpi-revenue'),
        cost: document.getElementById('kpi-cost'),
        roas: document.getElementById('kpi-roas'),
        iroas: document.getElementById('kpi-iroas'),
        orders: document.getElementById('kpi-orders'),
    };

    const tableBody = document.getElementById('influencer-table-body');
    const noDataMessage = document.getElementById('no-data-message');
    const exportBtn = document.getElementById('export-csv-btn');

    // ==========================================================================
    // Chart Initialization
    // ==========================================================================
    let platformChart, topInfluencersChart;

    function createCharts(data) {
        const platformCtx = document.getElementById('platform-chart')?.getContext('2d');
        const topInfluencersCtx = document.getElementById('top-influencers-chart')?.getContext('2d');

        if (!platformCtx || !topInfluencersCtx) {
            console.error("One or more chart canvas elements not found.");
            return;
        }

        // --- Platform Revenue Chart (Doughnut) ---
        platformChart = new Chart(platformCtx, {
            type: 'doughnut',
            data: {
                labels: data.chart_data_platform.map(d => d.name),
                datasets: [{
                    data: data.chart_data_platform.map(d => d.revenue),
                    backgroundColor: ['#4F46E5', '#22C55E', '#F97316', '#3B82F6', '#EC4899'],
                    borderColor: '#111827',
                    borderWidth: 4,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { color: '#F9FAFB', boxWidth: 15, padding: 20 } }
                },
                cutout: '70%',
            }
        });

        // --- Top Influencers Chart (Horizontal Bar) ---
        topInfluencersChart = new Chart(topInfluencersCtx, {
            type: 'bar',
            data: {
                labels: data.top_influencers_by_revenue.map(d => d.name),
                datasets: [{
                    label: 'Revenue (INR)',
                    data: data.top_influencers_by_revenue.map(d => d.total_revenue),
                    backgroundColor: '#4F46E5',
                    borderRadius: 4,
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        beginAtZero: true,
                        grid: { color: '#374151' },
                        ticks: { callback: value => '₹' + (value / 1000) + 'k' }
                    },
                    y: { grid: { display: false } }
                },
                plugins: { legend: { display: false } }
            }
        });
    }

    // ==========================================================================
    // Data Fetching and UI Update Logic
    // ==========================================================================
    async function updateDashboard() {
        const currentFilters = {
            search_term: filters.search.value,
            brand: filters.brand.value,
            platform: filters.platform.value,
            category: filters.category.value,
        };

        try {
            const response = await fetch('/update_data', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(currentFilters),
            });
            if (!response.ok) throw new Error('Network response was not ok');
            const data = await response.json();
            updateUI(data);
        } catch (error) {
            console.error('Error fetching updated data:', error);
        }
    }

    function updateUI(data) {
        kpiElements.revenue.textContent = `₹${data.campaign_revenue.toLocaleString('en-IN')}`;
        kpiElements.cost.textContent = `₹${data.campaign_cost.toLocaleString('en-IN')}`;
        kpiElements.roas.textContent = `${data.campaign_roas.toFixed(2)}x`;
        kpiElements.iroas.textContent = `${data.incremental_roas.toFixed(2)}x`;
        kpiElements.orders.textContent = data.total_orders.toLocaleString('en-IN');

        tableBody.innerHTML = '';
        if (data.influencer_details.length > 0) {
            noDataMessage.style.display = 'none';
            data.influencer_details.forEach(inf => {
                const roasClass = inf.roas > data.overall_campaign_roas ? 'positive' : 'negative';
                const row = `
                    <tr>
                        <td>${inf.name}</td>
                        <td>${inf.category}</td>
                        <td>${inf.platform}</td>
                        <td class="text-right">${(inf.followers / 1000).toLocaleString('en-IN')}k</td>
                        <td class="text-right">₹${inf.total_revenue.toLocaleString('en-IN')}</td>
                        <td class="text-right">${inf.total_orders.toLocaleString('en-IN')}</td>
                        <td class="text-right">₹${inf.total_cost.toLocaleString('en-IN')}</td>
                        <td class="text-right roas-value ${roasClass}">${inf.roas.toFixed(2)}x</td>
                    </tr>
                `;
                tableBody.insertAdjacentHTML('beforeend', row);
            });
        } else {
            noDataMessage.style.display = 'block';
        }

        platformChart.data.labels = data.chart_data_platform.map(d => d.name);
        platformChart.data.datasets[0].data = data.chart_data_platform.map(d => d.revenue);
        platformChart.update();

        topInfluencersChart.data.labels = data.top_influencers_by_revenue.map(d => d.name);
        topInfluencersChart.data.datasets[0].data = data.top_influencers_by_revenue.map(d => d.total_revenue);
        topInfluencersChart.update();
    }
    
    // ==========================================================================
    // CSV Export
    // ==========================================================================
    function exportTableToCSV() {
        let csv = [];
        const rows = document.querySelectorAll("table tr");
        
        for (const row of rows) {
            let cols = row.querySelectorAll("td, th");
            let rowData = [];
            for (const col of cols) {
                let data = col.innerText.replace(/"/g, '""');
                data = `"${data}"`;
                rowData.push(data);
            }
            csv.push(rowData.join(","));
        }

        const csvFile = new Blob([csv.join("\n")], { type: "text/csv" });
        const downloadLink = document.createElement("a");
        downloadLink.download = "influencer_performance.csv";
        downloadLink.href = window.URL.createObjectURL(csvFile);
        downloadLink.style.display = "none";
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
    }

    // ==========================================================================
    // Event Listeners
    // ==========================================================================
    const debouncedUpdate = debounce(updateDashboard, 300);

    filters.brand.addEventListener('change', updateDashboard);
    filters.platform.addEventListener('change', updateDashboard);
    filters.category.addEventListener('change', updateDashboard);
    filters.search.addEventListener('keyup', debouncedUpdate);
    exportBtn.addEventListener('click', exportTableToCSV);

    // ==========================================================================
    // Initial Load
    // ==========================================================================
    createCharts(initialData);
    lucide.createIcons();
});
