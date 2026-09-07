const API_BASE_URL = 'http://127.0.0.1:5000/api';
const SERVER_BASE_URL = 'http://127.0.0.1:5000';

let currentFilename = null;
let leafletMap = null;

document.addEventListener('DOMContentLoaded', () => {
    initMap();
    setupEventListeners();
});

function initMap() {
    const mapContainer = document.getElementById('leafletMap');
    if (mapContainer && !leafletMap) {
        leafletMap = L.map('leafletMap').setView([22.8157, 89.5524], 12); // Khulna default
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(leafletMap);
    }
}

function setupEventListeners() {
    const fileInput = document.getElementById('fileInput');
    const dropZone = document.getElementById('dropZone');
    const normalizeBtn = document.getElementById('normalizeBtn');

    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                uploadFile(e.target.files[0]);
            }
        });
    }

    if (dropZone) {
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            if (e.dataTransfer.files.length > 0) {
                uploadFile(e.dataTransfer.files[0]);
            }
        });
    }

    if (normalizeBtn) {
        normalizeBtn.addEventListener('click', processNormalization);
    }
}

async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    const progressContainer = document.getElementById('uploadProgress');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');

    if (progressContainer) progressContainer.classList.remove('hidden');

    try {
        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        console.log("Backend Response:", data); // Debugging Log

        if (response.ok) {
            currentFilename = data.filename || data.file_name;
            
            // Safe extraction of metadata (checks nested object or root level)
            const metaObj = data.metadata || data.info || data;
            displayMetadata(metaObj);
            
            // Render Original Preview Image
            const previewPath = data.preview_url || data.preview || data.image_url;
            if (previewPath) {
                renderOriginalImage(previewPath);
            }
            
            document.getElementById('normalizeBtn').disabled = false;
            document.getElementById('bandSelect').disabled = false;
            
            if (progressText) progressText.innerText = "Upload Complete!";
            if (progressBar) progressBar.style.width = "100%";
        } else {
            alert(`Upload Failed: ${data.error || 'Unknown error'}`);
        }
    } catch (err) {
        console.error('Upload Error:', err);
        alert('Could not connect to the Python Flask backend. Make sure app.py is running.');
    }
}

function displayMetadata(meta) {
    const container = document.getElementById('metadataContainer');
    if (!container) return;

    if (!meta || typeof meta !== 'object') {
        container.innerHTML = `<p class="empty-state-text">No metadata returned.</p>`;
        return;
    }

    const filename = meta.filename || meta.name || currentFilename || 'N/A';
    const width = meta.width || meta.cols || meta.columns || '-';
    const height = meta.height || meta.rows || '-';
    const bands = meta.count || meta.bands || meta.band_count || 1;
    const crs = meta.crs || meta.projection || 'Unprojected / Pixel Space';
    const dtype = meta.dtype || meta.data_type || meta.type || 'N/A';

    container.innerHTML = `
        <div style="font-size: 0.85rem; line-height: 1.6; text-align: left;">
            <p><strong>Filename:</strong> ${filename}</p>
            <p><strong>Dimensions:</strong> ${width} x ${height} px</p>
            <p><strong>Bands:</strong> ${bands}</p>
            <p><strong>CRS:</strong> ${crs}</p>
            <p><strong>Data Type:</strong> ${dtype}</p>
        </div>
    `;
}

function renderOriginalImage(url) {
    const canvas = document.getElementById('originalCanvas');
    const placeholder = document.getElementById('origPlaceholder');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const img = new Image();

    const fullUrl = url.startsWith('http') ? url : `${SERVER_BASE_URL}${url}`;

    img.crossOrigin = "anonymous";
    img.onload = () => {
        canvas.width = img.width;
        canvas.height = img.height;
        canvas.style.width = '100%';
        canvas.style.height = 'auto';
        canvas.style.maxHeight = '350px';
        canvas.style.display = 'block';

        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0);

        if (placeholder) {
            placeholder.style.display = 'none';
        }
    };

    img.onerror = (err) => {
        console.error('Failed to load original raster image from:', fullUrl, err);
    };

    img.src = fullUrl;
}

async function processNormalization() {
    if (!currentFilename) return;

    const palette = document.getElementById('paletteSelect').value;
    const band = document.getElementById('bandSelect').value;

    try {
        const response = await fetch(`${API_BASE_URL}/normalize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename: currentFilename,
                palette: palette,
                band: parseInt(band)
            })
        });

        const data = await response.json();

        if (response.ok) {
            updateStats(data.stats);
            renderNormalizedImage(data.normalized_url || data.preview_url);
            enableDownloads(data.downloads || data.export_urls);
        } else {
            alert(`Normalization Failed: ${data.error}`);
        }
    } catch (err) {
        console.error('Normalization Error:', err);
        alert('Failed to process raster normalization.');
    }
}

function updateStats(stats) {
    if (!stats) return;
    document.getElementById('statMin').innerText = stats.min !== undefined ? Number(stats.min).toFixed(4) : '-';
    document.getElementById('statMax').innerText = stats.max !== undefined ? Number(stats.max).toFixed(4) : '-';
    document.getElementById('statMean').innerText = stats.mean !== undefined ? Number(stats.mean).toFixed(4) : '-';
    document.getElementById('statStd').innerText = stats.std !== undefined ? Number(stats.std).toFixed(4) : '-';
}

function renderNormalizedImage(url) {
    const canvas = document.getElementById('normalizedCanvas');
    const placeholder = document.getElementById('normPlaceholder');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const img = new Image();

    const fullUrl = url.startsWith('http') ? url : `${SERVER_BASE_URL}${url}`;

    img.crossOrigin = "anonymous";
    img.onload = () => {
        canvas.width = img.width;
        canvas.height = img.height;
        canvas.style.width = '100%';
        canvas.style.height = 'auto';
        canvas.style.maxHeight = '350px';
        canvas.style.display = 'block';

        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0);

        if (placeholder) {
            placeholder.style.display = 'none';
        }
    };

    img.onerror = (err) => {
        console.error('Failed to load normalized image from:', fullUrl, err);
    };

    img.src = fullUrl;
}

function enableDownloads(downloads) {
    if (!downloads) return;
    setupDownloadBtn('dlGeoTiff', downloads.geotiff);
    setupDownloadBtn('dlPng', downloads.png);
    setupDownloadBtn('dlCsv', downloads.csv);
    setupDownloadBtn('dlStats', downloads.json);
}

function setupDownloadBtn(id, url) {
    const btn = document.getElementById(id);
    if (btn && url) {
        btn.disabled = false;
        btn.onclick = () => {
            const fullUrl = url.startsWith('http') ? url : `${SERVER_BASE_URL}${url}`;
            window.open(fullUrl, '_blank');
        };
    }
}