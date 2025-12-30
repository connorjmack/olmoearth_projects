#!/usr/bin/env python3
"""
Analyze year-over-year changes in solar farm deployment across CONUS.

This script compares annual GeoTIFF outputs to detect:
- New solar farm installations
- Decommissioned solar farms
- Total area changes
- Growth rates
"""

import numpy as np
import pandas as pd
import rasterio
from pathlib import Path
from rasterio.warp import calculate_default_transform, reproject, Resampling


def load_and_align_rasters(year1_path, year2_path):
    """Load two rasters and ensure they have matching extents/resolutions.

    Args:
        year1_path: Path to first year GeoTIFF
        year2_path: Path to second year GeoTIFF

    Returns:
        tuple: (array1, array2, metadata) - Aligned rasters and metadata
    """
    with rasterio.open(year1_path) as src1, rasterio.open(year2_path) as src2:
        # Read rasters
        arr1 = src1.read(1)
        arr2 = src2.read(1)

        # Check if CRS and bounds match
        if src1.crs != src2.crs or src1.bounds != src2.bounds:
            print(f"  ⚠ Reprojecting {year2_path.name} to match {year1_path.name}")

            # Reproject src2 to match src1
            transform, width, height = calculate_default_transform(
                src2.crs, src1.crs, src2.width, src2.height, *src2.bounds
            )

            arr2_aligned = np.empty((height, width), dtype=arr2.dtype)
            reproject(
                source=arr2,
                destination=arr2_aligned,
                src_transform=src2.transform,
                src_crs=src2.crs,
                dst_transform=transform,
                dst_crs=src1.crs,
                resampling=Resampling.nearest
            )
            arr2 = arr2_aligned

        meta = src1.meta.copy()

    return arr1, arr2, meta


def detect_changes(year1, year2, results_dir, output_dir, threshold=128):
    """Detect changes in solar farm deployment between two years.

    Args:
        year1: First year (baseline)
        year2: Second year (comparison)
        results_dir: Directory containing annual GeoTIFF results
        output_dir: Directory to save change detection outputs
        threshold: Threshold for binary classification (0-255)

    Returns:
        dict: Statistics about detected changes
    """
    print(f"\nAnalyzing changes: {year1} → {year2}")
    print("-" * 50)

    # Find GeoTIFF files (handle various naming patterns)
    results_dir = Path(results_dir)
    year1_dir = results_dir / str(year1)
    year2_dir = results_dir / str(year2)

    # Look for .tif files in results directories
    year1_files = list(year1_dir.glob("*.tif")) + list(year1_dir.glob("*.tiff"))
    year2_files = list(year2_dir.glob("*.tif")) + list(year2_dir.glob("*.tiff"))

    if not year1_files:
        print(f"  ✗ No GeoTIFF found for {year1} in {year1_dir}")
        return None
    if not year2_files:
        print(f"  ✗ No GeoTIFF found for {year2} in {year2_dir}")
        return None

    year1_path = year1_files[0]
    year2_path = year2_files[0]

    print(f"  Loading: {year1_path.name}")
    print(f"  Loading: {year2_path.name}")

    # Load and align rasters
    try:
        data_year1, data_year2, meta = load_and_align_rasters(year1_path, year2_path)
    except Exception as e:
        print(f"  ✗ Error loading rasters: {e}")
        return None

    # Threshold to binary (model outputs probabilities 0-255)
    binary_year1 = (data_year1 > threshold).astype(np.uint8)
    binary_year2 = (data_year2 > threshold).astype(np.uint8)

    # Detect changes
    new_installations = (binary_year1 == 0) & (binary_year2 == 1)
    decommissioned = (binary_year1 == 1) & (binary_year2 == 0)
    persistent = (binary_year1 == 1) & (binary_year2 == 1)

    # Calculate areas (10m resolution = 100m² per pixel)
    pixel_area_m2 = 100  # 10m × 10m
    pixel_area_km2 = pixel_area_m2 / 1_000_000  # Convert to km²

    new_area_km2 = np.sum(new_installations) * pixel_area_km2
    decom_area_km2 = np.sum(decommissioned) * pixel_area_km2
    persistent_area_km2 = np.sum(persistent) * pixel_area_km2
    total_year1_km2 = np.sum(binary_year1) * pixel_area_km2
    total_year2_km2 = np.sum(binary_year2) * pixel_area_km2

    # Calculate growth metrics
    net_change_km2 = total_year2_km2 - total_year1_km2
    growth_rate_pct = (net_change_km2 / total_year1_km2 * 100) if total_year1_km2 > 0 else 0

    # Create change map
    # 0 = no solar, 1 = new, 2 = decommissioned, 3 = persistent
    change_map = np.zeros_like(data_year1, dtype=np.uint8)
    change_map[new_installations] = 1
    change_map[decommissioned] = 2
    change_map[persistent] = 3

    # Save change detection raster
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"changes_{year1}_to_{year2}.tif"

    meta.update(dtype=rasterio.uint8, count=1, compress='lzw')
    with rasterio.open(output_path, 'w', **meta) as dst:
        dst.write(change_map, 1)

    # Print statistics
    print(f"\n  Results:")
    print(f"    Total {year1}: {total_year1_km2:,.2f} km²")
    print(f"    Total {year2}: {total_year2_km2:,.2f} km²")
    print(f"    New installations: {new_area_km2:,.2f} km²")
    print(f"    Decommissioned: {decom_area_km2:,.2f} km²")
    print(f"    Net change: {net_change_km2:+,.2f} km²")
    print(f"    Growth rate: {growth_rate_pct:+.2f}%")
    print(f"  ✓ Saved change map: {output_path}")

    return {
        'year1': year1,
        'year2': year2,
        'total_year1_km2': total_year1_km2,
        'total_year2_km2': total_year2_km2,
        'new_installations_km2': new_area_km2,
        'decommissioned_km2': decom_area_km2,
        'persistent_km2': persistent_area_km2,
        'net_change_km2': net_change_km2,
        'growth_rate_pct': growth_rate_pct
    }


def main():
    """Run change detection for all consecutive year pairs."""
    base_dir = Path(__file__).parent.parent
    results_dir = base_dir / "results"
    output_dir = base_dir / "analysis"

    print("\n" + "="*70)
    print("  CONUS Solar Farm Change Detection Analysis")
    print("="*70)
    print(f"  Results directory: {results_dir}")
    print(f"  Output directory: {output_dir}")
    print("="*70)

    # Run year-over-year analysis
    years = range(2017, 2026)
    stats = []

    for i in range(len(list(years)) - 1):
        year1 = 2017 + i
        year2 = year1 + 1

        result = detect_changes(year1, year2, results_dir, output_dir)
        if result:
            stats.append(result)

    if not stats:
        print("\n✗ No change detection results generated")
        print("  Ensure that GeoTIFF files exist in results/YYYY/ directories")
        return

    # Create summary dataframe
    df = pd.DataFrame(stats)

    # Save summary statistics
    summary_path = output_dir / "solar_growth_summary.csv"
    df.to_csv(summary_path, index=False)

    # Print summary table
    print("\n" + "="*70)
    print("  SUMMARY TABLE")
    print("="*70)
    print(df.to_string(index=False))
    print("="*70)

    print(f"\n✓ Summary saved to: {summary_path}")
    print(f"✓ Change maps saved to: {output_dir}/")

    print("\nNext step: Generate visualizations with visualize_trends.py")


if __name__ == "__main__":
    main()
