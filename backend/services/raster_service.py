import os
import numpy as np
from PIL import Image
import rasterio
import pandas as pd
from backend.utils.geo_helpers import format_crs_info, extract_bounds_dict
from backend.utils.file_helpers import get_file_type_category

class RasterService:
    """
    Universal System to read GIS Rasters, Standard Images, and CSV Grids
    into unified Numeric NumPy Arrays for Spatial Analysis and Normalization.
    """

    @staticmethod
    def read_raster_data(file_path, band_index=1, rgb_mode="grayscale"):
        """
        Reads any supported file format and returns:
        - numpy_array: Numeric 2D floating point grid array
        - metadata: Dictionary containing file dimensions, CRS, NoData, etc.
        """
        category = get_file_type_category(file_path)
        
        if category == 'geotiff':
            return RasterService._read_geotiff(file_path, band_index)
        elif category == 'image':
            return RasterService._read_image(file_path, rgb_mode)
        elif category == 'csv':
            return RasterService._read_csv_grid(file_path)
        else:
            raise ValueError(f"Unsupported raster file format for file: {os.path.basename(file_path)}")

    @staticmethod
    def _read_geotiff(file_path, band_index=1):
        """Reads spatial GeoTIFF / TIFF / ASC files using Rasterio."""
        with rasterio.open(file_path) as dataset:
            total_bands = dataset.count
            
            # Clamp band index
            if band_index < 1 or band_index > total_bands:
                band_index = 1
                
            # Read specified band array
            band_data = dataset.read(band_index).astype(np.float32)
            nodata_value = dataset.nodatavals[0] if dataset.nodatavals else None
            
            crs_str = format_crs_info(dataset.crs)
            bounds_dict = extract_bounds_dict(dataset.bounds)
            
            metadata = {
                "file_category": "geotiff",
                "width": int(dataset.width),
                "height": int(dataset.height),
                "bands": int(total_bands),
                "selected_band": int(band_index),
                "crs": crs_str,
                "is_geospatial": dataset.crs is not None,
                "transform": [float(x) for x in list(dataset.transform)[:6]],
                "bounds": bounds_dict,
                "nodata": float(nodata_value) if nodata_value is not None else None,
                "dtype": str(dataset.dtypes[0])
            }
            
            return band_data, metadata

    @staticmethod
    def _read_image(file_path, rgb_mode="grayscale"):
        """Reads standard image formats (PNG, JPG, WEBP, BMP, GIF) using Pillow."""
        with Image.open(file_path) as img:
            img = img.convert("RGBA" if img.mode == "RGBA" else "RGB")
            img_array = np.array(img, dtype=np.float32)
            
            height, width = img_array.shape[0], img_array.shape[1]
            channels = img_array.shape[2] if len(img_array.shape) == 3 else 1
            
            # RGB Channel handling logic
            if channels >= 3:
                red = img_array[:, :, 0]
                green = img_array[:, :, 1]
                blue = img_array[:, :, 2]
                
                if rgb_mode == "red":
                    grid_array = red
                elif rgb_mode == "green":
                    grid_array = green
                elif rgb_mode == "blue":
                    grid_array = blue
                else:
                    # Standard Luminance Formula: Gray = 0.299R + 0.587G + 0.114B
                    grid_array = 0.299 * red + 0.587 * green + 0.114 * blue
            else:
                grid_array = img_array
                
            metadata = {
                "file_category": "image",
                "width": int(width),
                "height": int(height),
                "bands": int(channels),
                "rgb_mode": rgb_mode,
                "crs": "Not available (Non-spatial Image)",
                "is_geospatial": False,
                "transform": None,
                "bounds": None,
                "nodata": None,
                "dtype": "float32"
            }
            
            return grid_array, metadata

    @staticmethod
    def _read_csv_grid(file_path):
        """Reads numerical grid matrix from CSV file."""
        try:
            df = pd.read_csv(file_path, header=None)
            # Filter non-numeric values
            df = df.apply(pd.to_numeric, errors='coerce')
            grid_array = df.values.astype(np.float32)
            
            height, width = grid_array.shape
            
            metadata = {
                "file_category": "csv",
                "width": int(width),
                "height": int(height),
                "bands": 1,
                "crs": "Not available (CSV Table Grid)",
                "is_geospatial": False,
                "transform": None,
                "bounds": None,
                "nodata": None,
                "dtype": "float32"
            }
            
            return grid_array, metadata
        except Exception as e:
            raise ValueError(f"Failed to parse numeric grid from CSV file: {str(e)}")