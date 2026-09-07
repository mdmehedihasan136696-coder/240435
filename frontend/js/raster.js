// Raster Upload & Handling Module

const RasterModule = {
    currentRasterId: null,
    currentMetadata: null,

    init: function() {
        const dropZone = document.getElementById('drop-zone');
        const fileInput = document.getElementById('file-input');
        const btnBrowse = document.getElementById('btn-browse');

        if (!dropZone || !fileInput) return;

        // Browse Button Trigger
        btnBrowse.addEventListener('click', (e) => {
            e.stopPropagation();
            fileInput.click();
        });

        dropZone.addEventListener('click', () => fileInput.click());

        // File Selection Event
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                RasterModule.uploadFile(e.target.files[0]);
            }
        });

        // Drag & Drop Events
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropZone.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropZone.classList.remove('dragover');
            }, false);
        });

        dropZone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0) {
                RasterModule.uploadFile(files[0]);
            }
        });
    },

    uploadFile: function(file) {
        const formData = new FormData();
        formData.append('file', file);

        // Show Progress Container
        UI.showElement('progress-container');
        const statusText = document.getElementById('progress-status-text');
        const progressFill = document.getElementById('progress-bar-fill');
        const progressPerc = document.getElementById('progress-percentage');

        statusText.innerText = `Uploading and processing ${file.name}...`;
        progressFill.style.width = '30%';
        progressPerc.innerText = '30%';

        fetch('/api/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                UI.showToast(data.error, 'error');
                UI.hideElement('progress-container');
                return;
            }

            progressFill.style.width = '100%';
            progressPerc.innerText = '100%';
            
            setTimeout(() => {
                UI.hideElement('progress-container');
            }, 600);

            // Store current state
            RasterModule.currentRasterId = data.raster_id;
            RasterModule.currentMetadata = data.metadata;

            UI.showToast('Raster uploaded and analyzed successfully!', 'success');

            // Render Metadata in UI
            RasterModule.renderMetadata(data.metadata, data.preview_url);

            // Show Metadata Section
            UI.showElement('metadata-section');
            UI.scrollTo('metadata-section');
        })
        .catch(err => {
            console.error(err);
            UI.showToast('Error uploading file to backend server.', 'error');
            UI.hideElement('progress-container');
        });
    },

    renderMetadata: function(meta, previewUrl) {
        document.getElementById('meta-filename').innerText = meta.original_filename;
        document.getElementById('meta-dims').innerText = `${meta.width} x ${meta.height} px`;
        document.getElementById('meta-bands').innerText = meta.bands;
        document.getElementById('meta-datatype').innerText = meta.dtype || 'Float32';
        document.getElementById('meta-crs').innerText = meta.crs || 'Not available';
        document.getElementById('meta-nodata').innerText = meta.nodata !== null ? meta.nodata : 'None';
        document.getElementById('file-type-badge').innerText = meta.file_category.toUpperCase();

        // Original Preview Image Update
        const origPreviewImg = document.getElementById('img-original-preview');
        if (origPreviewImg) {
            origPreviewImg.src = previewUrl;
        }

        // Show/Hide RGB mode controls if multiband
        if (meta.bands >= 3 && meta.file_category === 'image') {
            UI.showElement('band-selector-box');
            UI.showElement('rgb-mode-group');
        } else {
            UI.showElement('band-selector-box');
            UI.hideElement('rgb-mode-group');
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    RasterModule.init();
});