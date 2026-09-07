import os
import numpy as np
from flask import Blueprint, request, jsonify, send_file
from config import Config
from backend.models.raster_model import RasterModel
from backend.services.exporter import RasterExporter

export_bp = Blueprint('export_bp', __name__)

@export_bp.route('/api/export', methods=['POST'])
def export_raster():
    """
    POST /api/export
    JSON Payload:
    {
        "raster_id": "a1b2c3d4",
        "npy_filename": "elevation_a1b2_normalized.npy",
        "export_format": "geotiff"  // 'geotiff', 'png', 'jpg', 'csv', 'npy'
    }
    """
    data = request.get_json() or {}
    raster_id = data.get('raster_id')
    npy_filename = data.get('npy_filename')
    export_format = data.get('export_format', 'geotiff')

    if not raster_id or not npy_filename:
        return jsonify({"error": "Missing raster_id or normalized dataset reference"}), 400

    record = RasterModel.get_raster_by_id(raster_id)
    if not record:
        return jsonify({"error": "Original raster record not found"}), 404

    npy_path = os.path.join(Config.PROCESSED_FOLDER, npy_filename)
    if not os.path.exists(npy_path):
        return jsonify({"error": "Normalized pixel grid array cache not found. Please re-run normalization."}), 404

    try:
        norm_array = np.load(npy_path)
        out_filename, out_path = RasterExporter.export_data(
            norm_array=norm_array,
            export_format=export_format,
            original_meta=record
        )

        return jsonify({
            "success": True,
            "message": f"Successfully generated {export_format.upper()} export file!",
            "download_url": f"/storage/exports/{out_filename}",
            "filename": out_filename
        }), 200

    except Exception as e:
        return jsonify({"error": f"Failed to export raster data: {str(e)}"}), 500

@export_bp.route('/api/export/download/<filename>', methods=['GET'])
def download_export_file(filename):
    """Direct Attachment Download Endpoint."""
    file_path = os.path.join(Config.EXPORT_FOLDER, filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    return send_file(file_path, as_attachment=True)