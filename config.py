import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default_raster_secret_key")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/raster_normalizer")
    
    # File Storage Paths
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "storage", "uploads")
    PROCESSED_FOLDER = os.path.join(BASE_DIR, "storage", "processed")
    EXPORT_FOLDER = os.path.join(BASE_DIR, "storage", "exports")
    
    # Allowed Formats
    ALLOWED_RASTER_EXTENSIONS = {'tif', 'tiff', 'geotiff', 'asc'}
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'webp', 'gif'}
    ALLOWED_DATA_EXTENSIONS = {'csv'}
    ALLOWED_EXTENSIONS = ALLOWED_RASTER_EXTENSIONS | ALLOWED_IMAGE_EXTENSIONS | ALLOWED_DATA_EXTENSIONS
    
    # Upload Limit (100 MB)
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 100 * 1024 * 1024))