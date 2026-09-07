// Normalization Execution Controller

const NormalizationModule = {
    currentNormalizedResult: null,

    init: function() {
        // UI event listeners for normalize buttons
        const btnNormalize = document.getElementById('btn-run-normalize') || 
                             document.querySelector('button[aria-label="Normalize Raster"]') ||
                             Array.from(document.querySelectorAll('button')).find(btn => btn.textContent.includes('Normalize Raster'));

        if (btnNormalize) {
            btnNormalize.addEventListener('click', (e) => {
                e.preventDefault();
                NormalizationModule.runNormalization();
            });
        }

        // Custom range input toggle listener if present
        const techSelect = document.getElementById('norm-technique') || document.getElementById('normalization-method');
        if (techSelect) {
            techSelect.addEventListener('change', (e) => {
                const customInputs = document.getElementById('custom-range-inputs');
                if (customInputs) {
                    if (e.target.value === 'custom_range') {
                        customInputs.classList.remove('hidden');
                    } else {
                        customInputs.classList.add('hidden');
                    }
                }
            });
        }
    },

    runNormalization: function() {
        if (!RasterModule.currentRasterId) {
            if (typeof UI !== 'undefined' && UI.showToast) {
                UI.showToast('Please upload a raster file first.', 'warning');
            } else {
                alert('Please upload a raster file first.');
            }
            return;
        }

        // Extract dropdown selections dynamically
        const methodEl = document.getElementById('norm-technique') || document.querySelector('select[name="method"]');
        const bandEl = document.getElementById('band-index') || document.querySelector('select[name="band"]');
        const modeEl = document.getElementById('rgb-mode') || document.querySelector('select[name="rgb_mode"]');

        const method = methodEl ? methodEl.value : 'min_max';
        const bandIndex = bandEl ? parseInt(bandEl.value) || 1 : 1;
        const rgbMode = modeEl ? modeEl.value : 'grayscale';

        const payload = {
            raster_id: RasterModule.currentRasterId,
            method: method,
            band_index: bandIndex,
            rgb_mode: rgbMode
        };

        if (method === 'custom_range') {
            payload.target_min = parseFloat(document.getElementById('target-min').value || 0);
            payload.target_max = parseFloat(document.getElementById('target-max').value || 255);
        }

        if (typeof UI !== 'undefined' && UI.showToast) {
            UI.showToast('Processing raster normalization...', 'info');
        }

        fetch('/api/normalize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                if (typeof UI !== 'undefined' && UI.showToast) UI.showToast(data.error, 'error');
                return;
            }

            NormalizationModule.currentNormalizedResult = data;
            if (typeof UI !== 'undefined' && UI.showToast) {
                UI.showToast('Raster normalized successfully!', 'success');
            }

            // Update Preview Image
            const normPreview = document.getElementById('img-normalized-preview') || document.getElementById('normalized-raster-view');
            if (normPreview && data.preview_url) {
                normPreview.src = data.preview_url;
            }

            // Unhide preview & visualization sections
            if (typeof UI !== 'undefined' && UI.showElement) {
                UI.showElement('preview-section');
                UI.showElement('grid-section');
                UI.showElement('visualization-section');
                UI.scrollTo('preview-section');
            }
        })
        .catch(err => {
            console.error('Normalization error:', err);
            if (typeof UI !== 'undefined' && UI.showToast) {
                UI.showToast('Failed to process normalization.', 'error');
            }
        });
    }
};

document.addEventListener('DOMContentLoaded', () => {
    NormalizationModule.init();
});