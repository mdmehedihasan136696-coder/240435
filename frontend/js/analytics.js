// Analytics & Histogram Chart Controller

const AnalyticsModule = {
    chartInstance: null,

    init: function() {
        const btnRenderAnalytics = document.getElementById('btn-render-analytics');
        if (btnRenderAnalytics) {
            btnRenderAnalytics.addEventListener('click', AnalyticsModule.fetchAndRenderAnalytics);
        }
    },

    fetchAndRenderAnalytics: function() {
        if (!RasterModule.currentRasterId) {
            UI.showToast('Please upload a raster file first.', 'warning');
            return;
        }

        const npyFile = NormalizationModule.currentNormalizedResult ? NormalizationModule.currentNormalizedResult.npy_filename : null;

        UI.showToast('Calculating pixel distribution analytics...', 'info');

        fetch('/api/analytics', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                raster_id: RasterModule.currentRasterId,
                npy_filename: npyFile,
                bins: 30
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                UI.showToast(data.error, 'error');
                return;
            }

            AnalyticsModule.renderChart(data.original_histogram, data.normalized_histogram);
            UI.showElement('analytics-section');
            UI.scrollTo('analytics-section');
        })
        .catch(err => {
            console.error(err);
            UI.showToast('Failed to load distribution analytics.', 'error');
        });
    },

    renderChart: function(origHist, normHist) {
        const canvas = document.getElementById('histogram-chart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');

        if (AnalyticsModule.chartInstance) {
            AnalyticsModule.chartInstance.destroy();
        }

        const datasets = [];

        if (origHist && origHist.counts) {
            datasets.push({
                label: 'Original Distribution',
                data: origHist.counts,
                backgroundColor: 'rgba(59, 130, 246, 0.5)',
                borderColor: '#3b82f6',
                borderWidth: 1.5,
                borderRadius: 3
            });
        }

        if (normHist && normHist.counts) {
            datasets.push({
                label: 'Normalized Distribution',
                data: normHist.counts,
                backgroundColor: 'rgba(16, 185, 129, 0.5)',
                borderColor: '#10b981',
                borderWidth: 1.5,
                borderRadius: 3
            });
        }

        const labels = normHist ? normHist.labels : (origHist ? origHist.labels : []);

        AnalyticsModule.chartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: '#e2e8f0' } },
                    tooltip: { mode: 'index', intersect: false }
                },
                scales: {
                    x: {
                        ticks: { color: '#94a3b8', maxRotation: 45 },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' }
                    },
                    y: {
                        ticks: { color: '#94a3b8' },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' }
                    }
                }
            }
        });
    }
};

document.addEventListener('DOMContentLoaded', () => {
    AnalyticsModule.init();
});