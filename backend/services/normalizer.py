import numpy as np

class MinMaxNormalizer:
    """
    Core Mathematical Engine for Min-Max Raster Normalization.
    Supports linear rescaling, custom range clipping, custom min/max overrides,
    and missing/NoData value preservation.
    """

    @staticmethod
    def normalize(grid_array, target_min=0.0, target_max=1.0, 
                  custom_min=None, custom_max=None, nodata_val=None):
        """
        Applies Min-Max Normalization to 2D NumPy Array.
        
        Formula:
            X_scaled = target_min + [(X - user_min) * (target_max - target_min)] / (user_max - user_min)
        """
        # Create a float32 copy to prevent modifying original in-memory array
        data = grid_array.copy().astype(np.float32)

        # 1. Mask NoData / NaNs
        valid_mask = ~np.isnan(data)
        if nodata_val is not None:
            valid_mask = valid_mask & (data != nodata_val)

        valid_data = data[valid_mask]

        if valid_data.size == 0:
            raise ValueError("Cannot normalize an array containing no valid data pixels.")

        # 2. Determine User / Data Min and Max
        data_min = float(np.min(valid_data)) if custom_min is None else float(custom_min)
        data_max = float(np.max(valid_data)) if custom_max is None else float(custom_max)

        if data_max < data_min:
            raise ValueError("Custom Min cannot be strictly greater than Custom Max.")

        # 3. Prevent Division by Zero for uniform arrays
        range_diff = data_max - data_min
        if range_diff == 0:
            normalized_array = np.full_like(data, target_min)
        else:
            # 4. Apply Vectorized Scaling Equation
            scale_factor = (target_max - target_min) / range_diff
            normalized_array = target_min + (data - data_min) * scale_factor

            # Clip values if custom overrides were provided outside actual data min/max
            if custom_min is not None or custom_max is not None:
                normalized_array = np.clip(normalized_array, target_min, target_max)

        # Preserve original NaN / NoData pixels
        if nodata_val is not None:
            normalized_array[~valid_mask] = nodata_val
        else:
            normalized_array[~valid_mask] = np.nan

        # Calculate Statistics for response
        norm_valid = normalized_array[valid_mask]
        stats = {
            "input_min": float(np.min(valid_data)),
            "input_max": float(np.max(valid_data)),
            "target_min": float(target_min),
            "target_max": float(target_max),
            "output_min": float(np.nanmin(norm_valid)),
            "output_max": float(np.nanmax(norm_valid)),
            "output_mean": float(np.nanmean(norm_valid)),
            "output_std": float(np.nanstd(norm_valid))
        }

        return normalized_array, stats