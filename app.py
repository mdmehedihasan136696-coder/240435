import os
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from config import Config
from backend.utils.file_helpers import ensure_directories
from database.mongo import Database

# Import Blueprints
from backend.routes.upload_routes import upload_bp
from backend.routes.raster_routes import raster_bp
from backend.routes.normalize_routes import normalize_bp
from backend.routes.export_routes import export_bp
from backend.routes.inspector_routes import inspector_bp
from backend.routes.analytics_routes import analytics_bp

# Initialize Flask App
app = Flask(__name__, static_folder='frontend', static_url_path='')
app.config.from_object(Config)

# Enable CORS for frontend API calls
CORS(app)

# Ensure required storage folders exist at startup
ensure_directories()

# Initialize Database
Database.initialize()

# Register API Blueprints
app.register_blueprint(upload_bp)
app.register_blueprint(raster_bp)
app.register_blueprint(normalize_bp)
app.register_blueprint(export_bp)
app.register_blueprint(inspector_bp)
app.register_blueprint(analytics_bp)

# Route: Serve Frontend UI Index
@app.route('/')
def serve_frontend():
    return send_from_directory('frontend', 'index.html')

# Route: Serve Storage Files (Previews, Outputs, Exports)
@app.route('/storage/uploads/<path:filename>')
def serve_upload_files(filename):
    return send_from_directory(Config.UPLOAD_FOLDER, filename)

# Route: Serve Processed Storage Files
@app.route('/storage/processed/<path:filename>')
def serve_processed_files(filename):
    return send_from_directory(Config.PROCESSED_FOLDER, filename)

# Route: Serve Export Storage Files
@app.route('/storage/exports/<path:filename>')
def serve_export_files(filename):
    return send_from_directory(Config.EXPORT_FOLDER, filename)

# Health Check API Endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "online",
        "app_name": "Raster Normalizer Studio API",
        "version": "1.0.0"
    }), 200

# Global Error Handler for 404
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Requested resource or API endpoint not found"}), 404

# Global Error Handler for 500
@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "An internal server error occurred during raster processing"}), 500

if __name__ == '__main__':
    print("🚀 Starting Raster Normalizer Flask Backend Engine...")
    app.run(host='0.0.0.0', port=5000, debug=True)