import numpy as np

class RasterAnalytics:
    """
    Computes Statistical Distributions, Percentiles, and Histogram Frequency Bins
    for Original and Normalized Raster Grids.
    """

    @staticmethod
    def compute_histogram(grid_array, num_bins=30, nodata_val=None):
        """
        Calculates histogram bin edges and frequencies for a 2D float array.
        """
        valid_mask = ~np.isnan(grid_array)
        if nodata_val is not None:
            valid_mask = valid_mask & (grid_array != nodata_val)

        valid_data = grid_array[valid_mask]

        if valid_data.size == 0:
            return {"bins": [], "counts": [], "stats": {}}

        counts, bin_edges = np.histogram(valid_data, bins=num_bins)

        # Format bin midpoints/labels for charting
        bin_labels = [f"{(bin_edges[i] + bin_edges[i+1])/2:.2f}" for i in range(len(counts))]

        p25, p50, p75 = np.percentile(valid_data, [25, 50, 75])

        stats = {
            "min": float(np.min(valid_data)),
            "max": float(np.max(valid_data)),
            "mean": float(np.mean(valid_data)),
            "std": float(np.std(valid_data)),
            "p25": float(p25),
            "median": float(p50),
            "p75": float(p75),
            "total_valid_pixels": int(valid_data.size)
        }

        return {
            "labels": bin_labels,
            "counts": counts.tolist(),
            "stats": stats
        }