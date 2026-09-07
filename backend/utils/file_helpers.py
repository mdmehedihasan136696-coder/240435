import os
import uuid
from werkzeug.utils import secure_filename
from config import Config

def ensure_directories():
    """Ensure that required storage directories exist on disk."""
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.PROCESSED_FOLDER, exist_ok=True)
    os.makedirs(Config.EXPORT_FOLDER, exist_ok=True)

def get_file_extension(filename):
    """Extract lowercase file extension without leading dot."""
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''

def is_allowed_file(filename):
    """Check if uploaded file extension is supported."""
    ext = get_file_extension(filename)
    return ext in Config.ALLOWED_EXTENSIONS

def generate_unique_filename(original_filename, suffix=""):
    """
    Generates a secure, unique filename preserving original extension.
    Example: elevation.tif -> elevation_a1b2c3d4_normalized.tif
    """
    ext = get_file_extension(original_filename)
    base_name = original_filename.rsplit('.', 1)[0]
    clean_base = secure_filename(base_name) or "raster_file"
    unique_id = uuid.uuid4().hex[:8]
    
    if suffix:
        return f"{clean_base}_{unique_id}_{suffix}.{ext}"
    return f"{clean_base}_{unique_id}.{ext}"

def get_file_type_category(filename):
    """Categorize file extension into 'raster', 'image', or 'data'."""
    ext = get_file_extension(filename)
    if ext in Config.ALLOWED_RASTER_EXTENSIONS:
        return 'geotiff'
    elif ext in Config.ALLOWED_IMAGE_EXTENSIONS:
        return 'image'
    elif ext in Config.ALLOWED_DATA_EXTENSIONS:
        return 'csv'
    return 'unknown'