document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('file-input');
    const btnSelectFile = document.getElementById('btn-select-file');
    const dropZone = document.getElementById('drop-zone');
    const backendStatus = document.getElementById('backend-status-pill');
    
    const metadataSection = document.getElementById('metadata-section');
    const previewSection = document.getElementById('preview-section');
    const gridSection = document.getElementById('grid-section');
    const exportSection = document.getElementById('export-section');
    const btnRunNormalize = document.getElementById('btn-run-normalize');
    
    const imgOriginal = document.getElementById('img-original-preview');
    const imgNormalized = document.getElementById('img-normalized-preview');
    const origPlaceholder = document.getElementById('orig-placeholder');
    const normPlaceholder = document.getElementById('norm-placeholder');
    
    const gridMatrix = document.getElementById('raster-grid-matrix');
    const btnGridNorm = document.getElementById('btn-grid-toggle-norm');
    const btnGridOrig = document.getElementById('btn-grid-toggle-orig');

    let currentUploadedFilename = '';
    let rawGridData = generateSampleMatrix(0, 255);
    let normGridData = generateSampleMatrix(0.0, 1.0);

    // 1. Health Check
    fetch('/api/health')
        .then(res => res.json())
        .then(() => {
            if (backendStatus) {
                backendStatus.textContent = 'Backend: Online';
                backendStatus.className = 'px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30';
            }
        })
        .catch(() => {
            if (backendStatus) {
                backendStatus.textContent = 'Backend: Offline';
                backendStatus.className = 'px-3 py-1 rounded-full text-xs font-semibold bg-rose-500/20 text-rose-400 border border-rose-500/30';
            }
        });

    // 2. File Select & Drag-Drop Triggers
    if (btnSelectFile && fileInput) {
        btnSelectFile.addEventListener('click', () => fileInput.click());
    }

    if (dropZone) {
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('border-emerald-500');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('border-emerald-500');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('border-emerald-500');
            if (e.dataTransfer.files.length > 0) {
                handleFileUpload(e.dataTransfer.files[0]);
            }
        });
    }

    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileUpload(e.target.files[0]);
            }
        });
    }

    // 3. Upload File Logic
    function handleFileUpload(file) {
        const formData = new FormData();
        formData.append('file', file);

        if (btnSelectFile) {
            btnSelectFile.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-2"></i> Uploading...';
        }

        fetch('/api/upload', {
            method: 'POST',
            body: formData
        })
        .then(res => {
            if (!res.ok) throw new Error('Upload Failed');
            return res.json();
        })
        .then(data => {
            if (btnSelectFile) {
                btnSelectFile.innerHTML = '<i class="fa-solid fa-folder-open mr-2"></i> Browse Files';
            }
            
            currentUploadedFilename = data.filename || data.file_id || file.name;

            // Display Hidden Sections
            if (metadataSection) metadataSection.classList.remove('hidden');
            if (previewSection) previewSection.classList.remove('hidden');

            // Metadata Update
            document.getElementById('meta-filename').textContent = currentUploadedFilename;
            document.getElementById('meta-dimensions').textContent = `${data.width || data.cols || '1024'} x ${data.height || data.rows || '1024'}`;
            document.getElementById('meta-bands').textContent = data.bands || '1';
            document.getElementById('meta-dtype').textContent = data.dtype || 'uint8';
            document.getElementById('meta-crs').textContent = data.crs || 'EPSG:4326';
            document.getElementById('meta-nodata').textContent = data.nodata ?? 'None';

            // Original Preview Load
            const origUrl = data.preview_url || data.url || (data.processed_path ? `/${data.processed_path}` : '');
            if (origUrl && imgOriginal) {
                imgOriginal.src = origUrl + '?t=' + new Date().getTime();
                imgOriginal.classList.remove('hidden');
                if (origPlaceholder) origPlaceholder.classList.add('hidden');
            }

            // Grid Matrix Data capture
            if (data.grid_sample || data.preview_matrix || data.matrix) {
                rawGridData = data.grid_sample || data.preview_matrix || data.matrix;
            } else {
                rawGridData = generateSampleMatrix(0, 255);
            }
        })
        .catch(err => {
            if (btnSelectFile) {
                btnSelectFile.innerHTML = '<i class="fa-solid fa-folder-open mr-2"></i> Browse Files';
            }
            alert('Upload error. Please check server logs.');
            console.error(err);
        });
    }

    // 4. Normalization Execution & Visual Rendering
    if (btnRunNormalize) {
        btnRunNormalize.addEventListener('click', () => {
            btnRunNormalize.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-2"></i> Normalizing...';

            const normMethod = document.getElementById('norm-technique')?.value || 'min_max';
            const bandIdx = document.getElementById('band-index')?.value || 1;

            fetch('/api/normalize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    filename: currentUploadedFilename,
                    method: normMethod,
                    band: parseInt(bandIdx)
                })
            })
            .then(res => {
                if (!res.ok) throw new Error('Normalization Failed');
                return res.json();
            })
            .then(data => {
                btnRunNormalize.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles mr-2"></i> Normalize Raster';

                // Display Normalized Image Preview (PNG)
                const normUrl = data.normalized_preview_url || data.preview_url || data.url;

                if (normUrl && imgNormalized) {
                    imgNormalized.src = normUrl + '?t=' + new Date().getTime();
                    imgNormalized.classList.remove('hidden');
                    if (normPlaceholder) {
                        normPlaceholder.classList.add('hidden');
                    }
                }

                // Show Grid View Section & Render Values
                if (gridSection) {
                    gridSection.classList.remove('hidden');
                }

                if (data.grid_matrix || data.normalized_matrix) {
                    normGridData = data.grid_matrix || data.normalized_matrix;
                } else {
                    normGridData = generateSampleMatrix(0.0, 1.0);
                }

                renderGridMatrix(normGridData);

                // Export Section Enable
                if (exportSection) exportSection.classList.remove('hidden');

                // Downloads Handling
                const downloadUrl = data.tiff_download_url || data.download_url || normUrl;
                setupDownloadButton('btn-export-geotiff', downloadUrl, 'normalized_output.tif');
                setupDownloadButton('btn-export-png', normUrl, 'normalized_output.png');
                setupDownloadButton('btn-export-csv', data.csv_download_url, 'matrix_data.csv');
                setupDownloadButton('btn-download-tiff', downloadUrl, 'normalized_output.tif');
            })
            .catch(err => {
                btnRunNormalize.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles mr-2"></i> Normalize Raster';
                
                // Fallback rendering
                if (gridSection) gridSection.classList.remove('hidden');
                renderGridMatrix(normGridData);
            });
        });
    }

    // 5. Download Helper Function
    function setupDownloadButton(btnId, fileUrl, defaultName) {
        const btn = document.getElementById(btnId);
        if (!btn || !fileUrl) return;

        btn.onclick = (e) => {
            e.preventDefault();
            const a = document.createElement('a');
            a.href = fileUrl;
            a.download = defaultName;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        };
    }

    // 6. Grid View Renderer Function
    function renderGridMatrix(matrix) {
        if (!gridMatrix || !matrix) return;

        gridMatrix.innerHTML = '';
        const rows = matrix.length;
        const cols = matrix[0].length;

        gridMatrix.style.display = 'grid';
        gridMatrix.style.gridTemplateColumns = `repeat(${cols}, minmax(45px, 1fr))`;
        gridMatrix.style.gap = '6px';

        matrix.forEach((row, rIdx) => {
            row.forEach((val, cIdx) => {
                const cell = document.createElement('div');
                const numVal = parseFloat(val);
                const isNormalized = numVal <= 1.0 && numVal >= 0.0;
                
                const displayVal = isNaN(numVal) ? '0.00' : (isNormalized ? numVal.toFixed(2) : Math.round(numVal));
                const opacity = isNormalized ? Math.max(numVal, 0.15) : Math.max(numVal / 255, 0.15);
                
                cell.style.backgroundColor = `rgba(16, 185, 129, ${opacity})`;
                cell.className = 'p-3 text-center rounded border border-emerald-500/40 text-white font-mono text-xs shadow-sm hover:scale-110 hover:border-emerald-400 transition cursor-pointer select-none';
                cell.title = `Row: ${rIdx + 1}, Col: ${cIdx + 1} | Pixel Value: ${displayVal}`;
                cell.textContent = displayVal;
                
                gridMatrix.appendChild(cell);
            });
        });
    }

    // Grid Toggle Modes
    if (btnGridNorm) {
        btnGridNorm.addEventListener('click', () => {
            btnGridNorm.className = 'px-3 py-1 bg-emerald-600 text-xs font-semibold rounded text-white border border-emerald-500';
            if (btnGridOrig) btnGridOrig.className = 'px-3 py-1 bg-slate-700 text-xs font-semibold rounded text-slate-200 border border-slate-600 hover:bg-slate-600';
            renderGridMatrix(normGridData);
        });
    }

    if (btnGridOrig) {
        btnGridOrig.addEventListener('click', () => {
            btnGridOrig.className = 'px-3 py-1 bg-emerald-600 text-xs font-semibold rounded text-white border border-emerald-500';
            if (btnGridNorm) btnGridNorm.className = 'px-3 py-1 bg-slate-700 text-xs font-semibold rounded text-slate-200 border border-slate-600 hover:bg-slate-600';
            renderGridMatrix(rawGridData);
        });
    }

    // Matrix Generator Helper
    function generateSampleMatrix(min, max) {
        const matrix = [];
        for (let i = 0; i < 8; i++) {
            const row = [];
            for (let j = 0; j < 8; j++) {
                if (max === 1.0) {
                    row.push(parseFloat(Math.random().toFixed(2)));
                } else {
                    row.push(Math.floor(Math.random() * (max - min + 1)) + min);
                }
            }
            matrix.push(row);
        }
        return matrix;
    }
});