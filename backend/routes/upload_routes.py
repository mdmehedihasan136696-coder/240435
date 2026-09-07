import os
import numpy as np
from PIL import Image
from flask import Blueprint, request, jsonify

upload_bp = Blueprint('upload_bp', __name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
PROCESSED_FOLDER = os.path.join(os.getcwd(), 'processed')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)


@upload_bp.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        filename = file.filename
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # Basic metadata & original preview generation
        with Image.open(file_path) as img:
            width, height = img.size
            mode = img.mode
            
            # Original image convert to PNG for web display
            orig_filename = f"orig_{os.path.splitext(filename)[0]}.png"
            orig_preview_path = os.path.join(PROCESSED_FOLDER, orig_filename)
            img.convert('RGB').save(orig_preview_path, format='PNG')

        return jsonify({
            "message": "File uploaded successfully",
            "filename": filename,
            "metadata": {
                "filename": filename,
                "dimensions": f"{width} x {height}",
                "bands": len(img.getbands()) if hasattr(img, 'getbands') else 1,
                "dtype": mode,
                "crs": "EPSG:4326 (Default)",
                "nodata": "None"
            },
            "original_preview_url": f"/processed/{orig_filename}"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@upload_bp.route('/api/normalize', methods=['POST'])
def normalize_raster():
    try:
        data = request.get_json() or {}
        filename = data.get('filename')
        method = data.get('method', 'min_max')

        if not filename:
            return jsonify({"error": "No filename provided"}), 400

        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(file_path):
            return jsonify({"error": "Uploaded file not found"}), 404

        # Read image using PIL and convert to numpy array
        with Image.open(file_path) as img:
            grayscale_img = img.convert('L')
            img_np = np.array(grayscale_img, dtype=np.float32)

        # Min-Max Normalization (0.0 to 1.0)
        min_val, max_val = img_np.min(), img_np.max()
        if max_val > min_val:
            norm_np = (img_np - min_val) / (max_val - min_val)
        else:
            norm_np = np.zeros_like(img_np)

        # Save output image as 8-bit PNG for preview
        norm_img_8u = (norm_np * 255).astype(np.uint8)
        norm_filename = f"norm_{os.path.splitext(filename)[0]}.png"
        out_path = os.path.join(PROCESSED_FOLDER, norm_filename)
        Image.fromarray(norm_img_8u).save(out_path, format='PNG')

        # 8x8 sample matrix for the UI dynamic grid
        sample_grid = norm_np[:8, :8].tolist() if norm_np.shape[0] >= 8 and norm_np.shape[1] >= 8 else norm_np.tolist()

        return jsonify({
            "message": "Normalization successful",
            "normalized_preview_url": f"/processed/{norm_filename}",
            "download_url": f"/processed/{norm_filename}",
            "tiff_download_url": f"/processed/{norm_filename}",
            "grid_matrix": sample_grid
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500