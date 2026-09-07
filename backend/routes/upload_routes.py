import os
import numpy as np
from PIL import Image
from flask import Blueprint, request, jsonify
from config import Config
from backend.utils.file_helpers import (
    is_allowed_file, 
    generate_unique_filename, 
    get_file_extension
)
from backend.services.raster_service import RasterService
from backend.models.raster_model import RasterModel

upload_bp = Blueprint('upload_bp', __name__)

@upload_bp.route('/api/upload', methods=['POST'])
def upload_file():
    """
    POST /api/upload
    Handles raw image / GIS raster upload, extracts initial metadata,
    generates a web-viewable PNG preview, and stores record.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file field found in upload request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected for upload"}), 400

    if not is_allowed_file(file.filename):
        return jsonify({
            "error": "Unsupported file format. Please upload .tif, .geotiff, .asc, .png, .jpg, .jpeg, .bmp, .webp, or .csv"
        }), 400

    try:
        # 1. Save Original File
        saved_filename = generate_unique_filename(file.filename)
        upload_path = os.path.join(Config.UPLOAD_FOLDER, saved_filename)
        file.save(upload_path)

        # 2. Extract Data Array & Metadata via RasterService
        grid_array, metadata = RasterService.read_raster_data(upload_path)

        # 3. Calculate Original Array Min / Max Statistics
        valid_mask = ~np.isnan(grid_array)
        if metadata.get("nodata") is not None:
            valid_mask = valid_mask & (grid_array != metadata["nodata"])

        valid_data = grid_array[valid_mask]
        if valid_data.size == 0:
            return jsonify({"error": "The uploaded raster contains no valid numerical values."}), 400

        orig_min = float(np.min(valid_data))
        orig_max = float(np.max(valid_data))
        orig_mean = float(np.mean(valid_data))
        orig_std = float(np.std(valid_data))

        # 4. Generate Web Preview PNG Image (0-255 scaled)
        preview_filename = generate_unique_filename(file.filename, suffix="preview.png")
        # Ensure extension is .png
        preview_filename = preview_filename.rsplit('.', 1)[0] + '.png'
        preview_path = os.path.join(Config.PROCESSED_FOLDER, preview_filename)

        if orig_max > orig_min:
            norm_display = (grid_array - orig_min) / (orig_max - orig_min)
            norm_display = np.clip(norm_display * 255.0, 0, 255).astype(np.uint8)
        else:
            norm_display = np.zeros_like(grid_array, dtype=np.uint8)

        # Handle NaNs / NoData for Preview Image (set to transparent or black)
        norm_display[~valid_mask] = 0
        img = Image.fromarray(norm_display)
        img.save(preview_path, format="PNG")

        # 5. Build Complete Metadata Record
        meta_record = {
            "original_filename": file.filename,
            "saved_filename": saved_filename,
            "preview_filename": preview_filename,
            "file_size_bytes": os.path.getsize(upload_path),
            "stats": {
                "min": orig_min,
                "max": orig_max,
                "mean": orig_mean,
                "std": orig_std
            },
            **metadata
        }

        # 6. Save Record in Database
        raster_id = RasterModel.save_raster_metadata(meta_record)

        return jsonify({
            "success": True,
            "message": "File uploaded and processed successfully!",
            "raster_id": raster_id,
            "preview_url": f"/storage/processed/{preview_filename}",
            "metadata": meta_record
        }), 200

    except Exception as e:
        return jsonify({"error": f"Failed to process raster file: {str(e)}"}), 500