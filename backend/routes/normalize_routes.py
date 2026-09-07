import os
import numpy as np
from PIL import Image
from flask import Blueprint, request, jsonify
from config import Config
from backend.models.raster_model import RasterModel
from backend.services.raster_service import RasterService
from backend.services.normalizer import MinMaxNormalizer
from backend.utils.file_helpers import generate_unique_filename

normalize_bp = Blueprint('normalize_bp', __name__)

@normalize_bp.route('/api/normalize', methods=['POST'])
def run_normalization():
    """
    POST /api/normalize
    JSON Payload:
    {
        "raster_id": "a1b2c3d4",
        "target_min": 0.0,
        "target_max": 1.0,
        "custom_min": null,
        "custom_max": null,
        "band_index": 1,
        "rgb_mode": "grayscale"
    }
    """
    data = request.get_json() or {}
    raster_id = data.get('raster_id')

    if not raster_id:
        return jsonify({"error": "Missing required field 'raster_id'"}), 400

    record = RasterModel.get_raster_by_id(raster_id)
    if not record:
        return jsonify({"error": "Raster metadata record not found"}), 404

    target_min = float(data.get('target_min', 0.0))
    target_max = float(data.get('target_max', 1.0))
    custom_min = float(data['custom_min']) if data.get('custom_min') is not None and data.get('custom_min') != '' else None
    custom_max = float(data['custom_max']) if data.get('custom_max') is not None and data.get('custom_max') != '' else None
    band_index = int(data.get('band_index', 1))
    rgb_mode = data.get('rgb_mode', 'grayscale')

    try:
        # Load Original Array
        upload_path = os.path.join(Config.UPLOAD_FOLDER, record['saved_filename'])
        grid_array, meta = RasterService.read_raster_data(upload_path, band_index=band_index, rgb_mode=rgb_mode)

        # Perform Normalization
        norm_array, stats = MinMaxNormalizer.normalize(
            grid_array=grid_array,
            target_min=target_min,
            target_max=target_max,
            custom_min=custom_min,
            custom_max=custom_max,
            nodata_val=meta.get('nodata')
        )

        # Save Processed Array temporarily to .npy for downstream exports
        npy_filename = generate_unique_filename(record['original_filename'], suffix="normalized.npy")
        npy_path = os.path.join(Config.PROCESSED_FOLDER, npy_filename)
        np.save(npy_path, norm_array)

        # Generate Visual Preview PNG for Normalized Grid
        norm_preview_filename = generate_unique_filename(record['original_filename'], suffix="norm_preview.png")
        norm_preview_filename = norm_preview_filename.rsplit('.', 1)[0] + '.png'
        norm_preview_path = os.path.join(Config.PROCESSED_FOLDER, norm_preview_filename)

        valid_mask = ~np.isnan(norm_array)
        if meta.get('nodata') is not None:
            valid_mask = valid_mask & (norm_array != meta['nodata'])

        # Rescale normalized range to 0-255 uint8 for browser preview display
        if stats['output_max'] > stats['output_min']:
            display_img = (norm_array - stats['output_min']) / (stats['output_max'] - stats['output_min'])
            display_img = np.clip(display_img * 255.0, 0, 255).astype(np.uint8)
        else:
            display_img = np.zeros_like(norm_array, dtype=np.uint8)

        display_img[~valid_mask] = 0
        img = Image.fromarray(display_img)
        img.save(norm_preview_path, format="PNG")

        return jsonify({
            "success": True,
            "message": "Raster Min-Max Normalization completed successfully!",
            "raster_id": raster_id,
            "npy_filename": npy_filename,
            "normalized_preview_url": f"/storage/processed/{norm_preview_filename}",
            "stats": stats
        }), 200

    except Exception as e:
        return jsonify({"error": f"Normalization calculation failed: {str(e)}"}), 500