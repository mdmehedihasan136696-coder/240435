// Raster Export Controller

const ExportModule = {
    init: function() {
        const btnExportGeoTIFF = document.getElementById('btn-export-geotiff');
        const btnExportPNG = document.getElementById('btn-export-png');
        const btnExportJPG = document.getElementById('btn-export-jpg');
        const btnExportCSV = document.getElementById('btn-export-csv');
        const btnExportNPY = document.getElementById('btn-export-npy');

        if (btnExportGeoTIFF) btnExportGeoTIFF.addEventListener('click', () => ExportModule.triggerExport('geotiff'));
        if (btnExportPNG) btnExportPNG.addEventListener('click', () => ExportModule.triggerExport('png'));
        if (btnExportJPG) btnExportJPG.addEventListener('click', () => ExportModule.triggerExport('jpg'));
        if (btnExportCSV) btnExportCSV.addEventListener('click', () => ExportModule.triggerExport('csv'));
        if (btnExportNPY) btnExportNPY.addEventListener('click', () => ExportModule.triggerExport('npy'));
    },

    triggerExport: function(format) {
        if (!RasterModule.currentRasterId) {
            UI.showToast('No active raster dataset found for export.', 'error');
            return;
        }

        if (!NormalizationModule.currentNormalizedResult || !NormalizationModule.currentNormalizedResult.npy_filename) {
            UI.showToast('Please run the normalization process before exporting.', 'warning');
            return;
        }

        UI.showToast(`Generating ${format.toUpperCase()} export file...`, 'info');

        const payload = {
            raster_id: RasterModule.currentRasterId,
            npy_filename: NormalizationModule.currentNormalizedResult.npy_filename,
            export_format: format
        };

        fetch('/api/export', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                UI.showToast(data.error, 'error');
                return;
            }

            UI.showToast(`${format.toUpperCase()} file generated! Downloading...`, 'success');

            // Trigger direct browser download link
            const link = document.createElement('a');
            link.href = data.download_url;
            link.download = data.filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        })
        .catch(err => {
            console.error(err);
            UI.showToast('Export API call failed.', 'error');
        });
    }
};

document.addEventListener('DOMContentLoaded', () => {
    ExportModule.init();
});