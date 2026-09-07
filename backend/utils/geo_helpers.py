def format_crs_info(crs):
    """
    Formats Rasterio CRS object into human-readable string.
    If CRS is missing (standard JPG/PNG), returns 'Not available'.
    """
    if not crs:
        return "Not available (Non-spatial Raster)"
    
    try:
        if hasattr(crs, 'to_epsg') and crs.to_epsg():
            return f"EPSG:{crs.to_epsg()}"
        elif hasattr(crs, 'data') and 'init' in crs.data:
            return str(crs.data['init']).upper()
        return str(crs)
    except Exception:
        return "Custom Coordinate System"

def extract_bounds_dict(bounds):
    """Extract bounding box coordinates from Rasterio bounds."""
    if not bounds:
        return None
    return {
        "left": float(bounds.left),
        "bottom": float(bounds.bottom),
        "right": float(bounds.right),
        "top": float(bounds.top)
    }