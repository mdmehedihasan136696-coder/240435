from flask import Blueprint, jsonify
from backend.models.raster_model import RasterModel

raster_bp = Blueprint('raster_bp', __name__)

@raster_bp.route('/api/raster/<raster_id>', methods=['GET'])
def get_raster_info(raster_id):
    """
    GET /api/raster/<raster_id>
    Returns metadata record of uploaded raster.
    """
    record = RasterModel.get_raster_by_id(raster_id)
    if not record:
        return jsonify({"error": "Raster record not found"}), 404

    # Convert ObjectId if exists
    if "_id" in record and not isinstance(record["_id"], str):
        record["_id"] = str(record["_id"])

    return jsonify({
        "success": True,
        "data": record
    }), 200