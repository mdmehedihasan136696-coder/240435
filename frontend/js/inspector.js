// Pixel Inspector Controller

const InspectorModule = {
    init: function() {
        const origImg = document.getElementById('img-original-preview');
        const normImg = document.getElementById('img-normalized-preview');

        if (origImg) InspectorModule.attachHoverEvents(origImg);
        if (normImg) InspectorModule.attachHoverEvents(normImg);
    },

    attachHoverEvents: function(imgElement) {
        imgElement.addEventListener('mousemove', (e) => {
            if (!RasterModule.currentMetadata) return;

            const rect = imgElement.getBoundingClientRect();
            const clickX = e.clientX - rect.left;
            const clickY = e.clientY - rect.top;

            const nativeWidth = RasterModule.currentMetadata.width;
            const nativeHeight = RasterModule.currentMetadata.height;

            const pixelX = Math.floor((clickX / rect.width) * nativeWidth);
            const pixelY = Math.floor((clickY / rect.height) * nativeHeight);

            // Throttle or trigger inspector API update
            InspectorModule.inspectPixel(pixelX, pixelY);
        });
    },

    inspectPixel: function(x, y) {
        if (!RasterModule.currentRasterId) return;

        const npyFile = NormalizationModule.currentNormalizedResult ? NormalizationModule.currentNormalizedResult.npy_filename : null;

        fetch('/api/pixel-value', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                raster_id: RasterModule.currentRasterId,
                npy_filename: npyFile,
                x: x,
                y: y
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                document.getElementById('inspect-x').innerText = data.coords.x;
                document.getElementById('inspect-y').innerText = data.coords.y;
                document.getElementById('inspect-orig-val').innerText = data.original_value;
                document.getElementById('inspect-norm-val').innerText = data.normalized_value !== null ? data.normalized_value : 'N/A';
            }
        })
        .catch(err => console.error("Pixel inspector error:", err));
    }
};

document.addEventListener('DOMContentLoaded', () => {
    InspectorModule.init();
});