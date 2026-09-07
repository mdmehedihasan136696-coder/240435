import os
import numpy as np
from flask import Blueprint, request, jsonify
from config import Config
from backend.models.raster_model import RasterModel
from backend.services.raster_service import RasterService

inspector_bp = Blueprint('inspector_bp', __name__)

@inspector_bp.route('/api/pixel-value', methods=['POST'])
def get_pixel_value():
    """
    POST /api/pixel-value
    JSON Payload:
    {
        "raster_id": "a1b2c3d4",
        "npy_filename": "elevation_a1b2_normalized.npy",
        "x": 120,
        "y": 85,
        "band_index": 1,
        "rgb_mode": "grayscale"
    }
    """
    data = request.get_json() or {}
    raster_id = data.get('raster_id')
    npy_filename = data.get('npy_filename')
    x = data.get('x')
    y = data.get('y')
    band_index = int(data.get('band_index', 1))
    rgb_mode = data.get('rgb_mode', 'grayscale')

    if not raster_id or x is None or y is None:
        return jsonify({"error": "Missing raster_id or coordinates (x, y)"}), 400

    record = RasterModel.get_raster_by_id(raster_id)
    if not record:
        return jsonify({"error": "Raster record not found"}), 404

    try:
        x = int(x)
        y = int(y)

        # 1. Fetch Original Pixel Value
        upload_path = os.path.join(Config.UPLOAD_FOLDER, record['saved_filename'])
        orig_array, _ = RasterService.read_raster_data(upload_path, band_index=band_index, rgb_mode=rgb_mode)

        height, width = orig_array.shape
        if x < 0 or x >= width or y < 0 or y >= height:
            return jsonify({"error": f"Coordinates out of bounds. Grid size is {width}x{height}"}), 400

        orig_val = float(orig_array[y, x])

        # 2. Fetch Normalized Pixel Value if available
        norm_val = None
        if npy_filename:
            npy_path = os.path.join(Config.PROCESSED_FOLDER, npy_filename)
            if os.path.exists(npy_path):
                norm_array = np.load(npy_path)
                norm_val = float(norm_array[y, x])

        return jsonify({
            "success": True,
            "coords": {"x": x, "y": y},
            "original_value": orig_val if not np.isnan(orig_val) else "NoData/NaN",
            "normalized_value": norm_val if norm_val is not None and not np.isnan(norm_val) else "NoData/NaN"
        }), 200

    except Exception as e:
        return jsonify({"error": f"Failed to inspect pixel value: {str(e)}"}), 500