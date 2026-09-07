import os
import numpy as np
from PIL import Image
import rasterio
from rasterio.transform import Affine
from config import Config
from backend.utils.file_helpers import generate_unique_filename

class RasterExporter:
    """
    Engine to export normalized NumPy array into multiple file formats:
    GeoTIFF (with Spatial CRS/Transform), PNG, JPG, CSV, or NPY.
    """

    @staticmethod
    def export_data(norm_array, export_format, original_meta, output_prefix="normalized"):
        """
        Exports normalized array into specified format.
        Returns filename and full output file path.
        """
        export_format = export_format.lower()
        orig_name = original_meta.get('original_filename', 'raster.tif')

        if export_format in ['geotiff', 'tif', 'gtiff']:
            return RasterExporter._to_geotiff(norm_array, original_meta, orig_name)
        elif export_format in ['png', 'jpg', 'jpeg']:
            return RasterExporter._to_image(norm_array, export_format, orig_name)
        elif export_format == 'csv':
            return RasterExporter._to_csv(norm_array, orig_name)
        elif export_format == 'npy':
            return RasterExporter._to_npy(norm_array, orig_name)
        else:
            raise ValueError(f"Unsupported export format: {export_format}")

    @staticmethod
    def _to_geotiff(norm_array, meta, orig_name):
        filename = generate_unique_filename(orig_name, suffix="export.tif")
        out_path = os.path.join(Config.EXPORT_FOLDER, filename)

        height, width = norm_array.shape

        # Retrieve CRS and Transform
        crs = meta.get('crs')
        if crs and crs.startswith("Not available"):
            crs = None

        transform_list = meta.get('transform')
        transform = Affine(*transform_list) if transform_list and len(transform_list) == 6 else None

        nodata_val = meta.get('nodata') if meta.get('nodata') is not None else -9999.0

        # Replace NaNs with nodata_val for GeoTIFF compliance
        export_grid = norm_array.copy()
        export_grid[np.isnan(export_grid)] = nodata_val

        with rasterio.open(
            out_path,
            'w',
            driver='GTiff',
            height=height,
            width=width,
            count=1,
            dtype=rasterio.float32,
            crs=crs,
            transform=transform,
            nodata=nodata_val
        ) as dst:
            dst.write(export_grid.astype(np.float32), 1)

        return filename, out_path

    @staticmethod
    def _to_image(norm_array, fmt, orig_name):
        ext = 'png' if fmt == 'png' else 'jpg'
        filename = generate_unique_filename(orig_name, suffix=f"export.{ext}")
        out_path = os.path.join(Config.EXPORT_FOLDER, filename)

        # Rescale normalized array to 0-255 uint8 grayscale image
        valid_mask = ~np.isnan(norm_array)
        min_val = np.nanmin(norm_array) if np.any(valid_mask) else 0
        max_val = np.nanmax(norm_array) if np.any(valid_mask) else 1

        if max_val > min_val:
            scaled = (norm_array - min_val) / (max_val - min_val)
            scaled = np.clip(scaled * 255.0, 0, 255).astype(np.uint8)
        else:
            scaled = np.zeros_like(norm_array, dtype=np.uint8)

        scaled[~valid_mask] = 0

        img = Image.fromarray(scaled)
        if ext == 'jpg':
            img = img.convert('RGB')
        img.save(out_path, format='PNG' if ext == 'png' else 'JPEG')

        return filename, out_path

    @staticmethod
    def _to_csv(norm_array, orig_name):
        filename = generate_unique_filename(orig_name, suffix="export.csv")
        out_path = os.path.join(Config.EXPORT_FOLDER, filename)

        # Export matrix with floating point precision
        np.savetxt(out_path, norm_array, delimiter=",", fmt="%.6f")
        return filename, out_path

    @staticmethod
    def _to_npy(norm_array, orig_name):
        filename = generate_unique_filename(orig_name, suffix="export.npy")
        out_path = os.path.join(Config.EXPORT_FOLDER, filename)

        np.save(out_path, norm_array)
        return filename, out_path