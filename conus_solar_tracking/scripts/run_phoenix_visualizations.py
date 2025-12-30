#!/usr/bin/env python3
"""
Automated visualization runner for Phoenix test results.

Finds the test GeoTIFF output and generates all publication-quality figures.
"""

import subprocess
import sys
from pathlib import Path


def find_test_geotiff():
    """Find the test GeoTIFF output file."""
    base_dir = Path(__file__).parent.parent
    scratch_dir = base_dir / "scratch/test/results/results_raster"

    if not scratch_dir.exists():
        print(f"❌ Test results directory not found: {scratch_dir}")
        print("\nPlease run the Phoenix test inference first:")
        print("  python -m olmoearth_projects.main olmoearth_run olmoearth_run \\")
        print("    --config_path conus_solar_tracking/configs/test/ \\")
        print("    --checkpoint_path gs://...ckpt \\")
        print("    --scratch_path conus_solar_tracking/scratch/test/")
        return None

    # Find GeoTIFF files
    geotiffs = list(scratch_dir.glob("*.tif")) + list(scratch_dir.glob("*.tiff"))

    if not geotiffs:
        print(f"❌ No GeoTIFF files found in {scratch_dir}")
        print("\nThe test may still be running, or may have failed.")
        print(f"Check: {scratch_dir}")
        return None

    # Use the first (or only) GeoTIFF
    geotiff = geotiffs[0]
    print(f"✓ Found test GeoTIFF: {geotiff.name}")

    if len(geotiffs) > 1:
        print(f"  Note: Found {len(geotiffs)} GeoTIFF files, using: {geotiff.name}")

    return geotiff


def run_visualizations(geotiff_path, output_dir):
    """Run all visualization scripts on the test GeoTIFF.

    Args:
        geotiff_path: Path to input GeoTIFF
        output_dir: Directory to save figures
    """
    base_dir = Path(__file__).parent.parent
    viz_script = base_dir / "scripts/visualize_geotiff.py"

    print("\n" + "="*70)
    print("  Generating Publication-Quality Figures")
    print("="*70)
    print(f"  Input: {geotiff_path}")
    print(f"  Output: {output_dir}")
    print("="*70 + "\n")

    # Run visualization script
    cmd = [
        "python3",
        str(viz_script),
        str(geotiff_path),
        "--output-dir", str(output_dir),
        "--title", "Phoenix AZ - Solar Farm Detection (2024)",
        "--threshold", "128",
        "--dpi", "300"
    ]

    try:
        print("Running visualize_geotiff.py...")
        result = subprocess.run(cmd, check=True, capture_output=False)
        print("✓ Visualization complete!")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error running visualization script:")
        print(f"  {e}")
        return False

    return True


def create_summary_report(geotiff_path, output_dir):
    """Create a summary report of the test results."""
    import rasterio
    import numpy as np

    print("\nCreating summary report...")

    with rasterio.open(geotiff_path) as src:
        data = src.read(1)
        bounds = src.bounds
        crs = src.crs
        transform = src.transform

    # Calculate statistics
    pixel_size = abs(transform.a)
    threshold = 128
    binary = (data > threshold).astype(np.uint8)
    solar_pixels = np.sum(binary)
    total_pixels = binary.size
    solar_area_km2 = solar_pixels * pixel_size * pixel_size / 1_000_000
    solar_area_acres = solar_area_km2 * 247.105
    coverage_pct = (solar_pixels / total_pixels) * 100

    # Create report
    report = f"""
# Phoenix AZ Solar Farm Detection Test Results

## Test Configuration

- **Region**: Phoenix Metro Area
- **Bounds**: [{bounds.left:.4f}, {bounds.bottom:.4f}] to [{bounds.right:.4f}, {bounds.top:.4f}]
- **Time Period**: June-September 2024
- **Satellite Data**: Sentinel-2 L2A (10m resolution)
- **Model**: OlmoEarth Solar Farm Detection (satlas_solar_farm)

## Detection Results

- **Raster Dimensions**: {data.shape[1]} × {data.shape[0]} pixels
- **Spatial Resolution**: {pixel_size:.1f}m
- **Total Area Analyzed**: {total_pixels * pixel_size**2 / 1e6:.1f} km²

### Solar Farm Detections

- **Detected Pixels**: {solar_pixels:,}
- **Solar Farm Area**: {solar_area_km2:.2f} km² ({solar_area_acres:.1f} acres)
- **Coverage**: {coverage_pct:.4f}% of analyzed area
- **Detection Threshold**: {threshold}/255

## Quality Metrics

- **CRS**: {crs}
- **Data Type**: {data.dtype}
- **Value Range**: [{data.min()}, {data.max()}]

## Output Files

All visualizations saved to: `{output_dir}/`

### Generated Figures

1. **Binary Detection Map** (`*_map.png`, `*_map.pdf`)
   - Shows solar farm locations in orange
   - Includes scale bar, north arrow, legend
   - Publication-ready at 300 DPI

2. **Probability Heat Map** (`*_heatmap.png`)
   - Shows detection confidence as continuous colormap
   - Useful for identifying uncertain detections

3. **Multi-Panel Overview** (`*_overview.png`, `*_overview.pdf`)
   - Panel A: Binary detection
   - Panel B: Detection confidence
   - Panel C: Spatial density
   - Panel D: Statistics summary

## Validation

To validate these results:

1. **Visual Inspection**: Load GeoTIFFs in QGIS and compare with Google Earth
2. **Known Installations**: Check against EIA Form 860 data
3. **Cross-reference**: Compare with known Phoenix-area solar farms (e.g., Solana, Agua Caliente)

## Next Steps

If test results look good:

1. Run full CONUS inference for all years (2017-2025)
2. Perform temporal change detection
3. Generate deployment trend visualizations

Run: `python3 conus_solar_tracking/scripts/run_all_years.py`

---

*Report generated: {Path(geotiff_path).stat().st_mtime}*
*GeoTIFF: {geotiff_path}*
"""

    # Save report
    report_path = output_dir / "TEST_RESULTS_SUMMARY.md"
    with open(report_path, 'w') as f:
        f.write(report)

    print(f"✓ Summary report saved: {report_path}")

    # Also create a plain text statistics file
    stats_path = output_dir / "statistics.txt"
    with open(stats_path, 'w') as f:
        f.write(f"Phoenix AZ Solar Farm Detection - Summary Statistics\n")
        f.write(f"="*60 + "\n\n")
        f.write(f"Total Area Analyzed: {total_pixels * pixel_size**2 / 1e6:.2f} km²\n")
        f.write(f"Solar Farm Area: {solar_area_km2:.2f} km²\n")
        f.write(f"Solar Farm Area: {solar_area_acres:.1f} acres\n")
        f.write(f"Coverage: {coverage_pct:.4f}%\n")
        f.write(f"Detected Pixels: {solar_pixels:,}\n")
        f.write(f"Spatial Resolution: {pixel_size:.1f}m\n")

    print(f"✓ Statistics saved: {stats_path}")


def main():
    """Main function to run automated visualizations."""
    base_dir = Path(__file__).parent.parent
    output_dir = base_dir / "test_results/figures"

    print("\n" + "="*70)
    print("  Phoenix Test - Automated Visualization Runner")
    print("="*70)

    # Find test GeoTIFF
    geotiff = find_test_geotiff()
    if geotiff is None:
        sys.exit(1)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    (base_dir / "test_results/statistics").mkdir(parents=True, exist_ok=True)

    # Run visualizations
    success = run_visualizations(geotiff, output_dir)
    if not success:
        sys.exit(1)

    # Create summary report
    try:
        create_summary_report(geotiff, base_dir / "test_results")
        print("\n" + "="*70)
        print("  ✓ All visualizations and reports complete!")
        print("="*70)
        print(f"\nView results in: {base_dir / 'test_results'}/")
        print("\nGenerated files:")
        print("  - figures/*_map.png (and .pdf)")
        print("  - figures/*_heatmap.png")
        print("  - figures/*_overview.png (and .pdf)")
        print("  - TEST_RESULTS_SUMMARY.md")
        print("  - statistics.txt")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n⚠ Warning: Could not create summary report: {e}")
        print("Visualizations were created successfully.\n")


if __name__ == "__main__":
    main()
