import os
import cv2
import numpy as np
from PIL import Image
from flask import Blueprint, request, jsonify, url_for

upload_bp = Blueprint('upload_bp', __name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
PROCESSED_FOLDER = os.path.join(os.getcwd(), 'processed')

@upload_bp.route('/api/normalize', methods=['POST'])
def normalize_raster():
    try:
        data = request.get_json()
        filename = data.get('filename')
        method = data.get('method', 'min_max')
        
        if not filename:
            return jsonify({"error": "No filename provided"}), 400
            
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404

        # Load image & Process Normalization (0.0 to 1.0)
        img = Image.open(file_path).convert('L')
        img_np = np.array(img, dtype=np.float32)

        min_val, max_val = img_np.min(), img_np.max()
        if max_val > min_val:
            norm_np = (img_np - min_val) / (max_val - min_val)
        else:
            norm_np = np.zeros_like(img_np)

        # Save Normalized Output PNG
        norm_img_8u = (norm_np * 255).astype(np.uint8)
        norm_filename = f"norm_{filename}.png"
        out_path = os.path.join(PROCESSED_FOLDER, norm_filename)
        Image.fromarray(norm_img_8u).save(out_path)

        # Generate sample grid matrix for visual grid
        small_matrix = norm_np[:8, :8].tolist() if norm_np.shape[0] >= 8 else norm_np.tolist()

        return jsonify({
            "message": "Normalization successful",
            "normalized_preview_url": f"/processed/{norm_filename}",
            "tiff_download_url": f"/processed/{norm_filename}",
            "download_url": f"/processed/{norm_filename}",
            "grid_matrix": small_matrix
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500