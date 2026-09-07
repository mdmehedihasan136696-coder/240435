import os
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

# Configure Flask App
app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

# Absolute paths for directories
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
PROCESSED_FOLDER = os.path.join(BASE_DIR, 'processed')

# Ensure required storage folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# ----------------------------------------------------
# 1. FRONTEND & STATIC FILES ROUTES
# ----------------------------------------------------

@app.route('/')
def index():
    """Serves the main HTML page."""
    if os.path.exists(os.path.join(BASE_DIR, 'index.html')):
        return send_from_directory(BASE_DIR, 'index.html')
    elif os.path.exists(os.path.join(BASE_DIR, 'frontend', 'index.html')):
        return send_from_directory(os.path.join(BASE_DIR, 'frontend'), 'index.html')
    return jsonify({"error": "index.html file not found on server"}), 404

@app.route('/js/<path:filename>')
def serve_js(filename):
    """Serves JavaScript assets."""
    js_dir = os.path.join(BASE_DIR, 'frontend', 'js') if os.path.exists(os.path.join(BASE_DIR, 'frontend', 'js')) else os.path.join(BASE_DIR, 'js')
    return send_from_directory(js_dir, filename)

@app.route('/css/<path:filename>')
def serve_css(filename):
    """Serves CSS assets."""
    css_dir = os.path.join(BASE_DIR, 'frontend', 'css') if os.path.exists(os.path.join(BASE_DIR, 'frontend', 'css')) else os.path.join(BASE_DIR, 'css')
    return send_from_directory(css_dir, filename)

# ----------------------------------------------------
# 2. UPLOAD & PROCESSED FILE SERVING
# ----------------------------------------------------

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    """Serves raw uploaded files."""
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/processed/<path:filename>')
def serve_processed(filename):
    """Serves processed normalized images and previews."""
    return send_from_directory(PROCESSED_FOLDER, filename)

# ----------------------------------------------------
# 3. HEALTH & BLUEPRINT REGISTRATION
# ----------------------------------------------------

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "Raster Normalizer API"
    }), 200

# Import and register upload and processing routes
from backend.routes.upload_routes import upload_bp
app.register_blueprint(upload_bp)

# ----------------------------------------------------
# 4. SERVER RUNNER
# ----------------------------------------------------

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)