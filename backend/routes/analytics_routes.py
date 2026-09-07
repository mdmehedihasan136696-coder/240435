import os
import numpy as np
from flask import Blueprint, request, jsonify
from config import Config
from backend.models.raster_model import RasterModel
from backend.services.raster_service import RasterService
from backend.services.analytics import RasterAnalytics

analytics_bp = Blueprint('analytics_bp', __name__)

@analytics_bp.route('/api/analytics', methods=['POST'])
def get_analytics_data():
    """
    POST /api/analytics
    JSON Payload:
    {
        "raster_id": "a1b2c3d4",
        "npy_filename": "elevation_a1b2_normalized.npy",
        "bins": 30,
        "band_index": 1,
        "rgb_mode": "grayscale"
    }
    """
    data = request.get_json() or {}
    raster_id = data.get('raster_id')
    npy_filename = data.get('npy_filename')
    num_bins = int(data.get('bins', 30))
    band_index = int(data.get('band_index', 1))
    rgb_mode = data.get('rgb_mode', 'grayscale')

    if not raster_id:
        return jsonify({"error": "Missing raster_id field"}), 400

    record = RasterModel.get_raster_by_id(raster_id)
    if not record:
        return jsonify({"error": "Raster metadata record not found"}), 404

    try:
        # Load Original Data
        upload_path = os.path.join(Config.UPLOAD_FOLDER, record['saved_filename'])
        orig_array, meta = RasterService.read_raster_data(upload_path, band_index=band_index, rgb_mode=rgb_mode)

        orig_histogram = RasterAnalytics.compute_histogram(
            grid_array=orig_array,
            num_bins=num_bins,
            nodata_val=meta.get('nodata')
        )

        norm_histogram = None
        if npy_filename:
            npy_path = os.path.join(Config.PROCESSED_FOLDER, npy_filename)
            if os.path.exists(npy_path):
                norm_array = np.load(npy_path)
                norm_histogram = RasterAnalytics.compute_histogram(
                    grid_array=norm_array,
                    num_bins=num_bins,
                    nodata_val=meta.get('nodata')
                )

        return jsonify({
            "success": True,
            "original_histogram": orig_histogram,
            "normalized_histogram": norm_histogram
        }), 200

    except Exception as e:
        return jsonify({"error": f"Failed to calculate analytics: {str(e)}"}), 500