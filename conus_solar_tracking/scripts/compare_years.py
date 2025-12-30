#!/usr/bin/env python3
"""
Create publication-quality comparison figures for multiple years of solar farm data.

Generates side-by-side comparisons, temporal animations, and change visualizations.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import rasterio
from rasterio.warp import reproject, Resampling, calculate_default_transform
from pathlib import Path
import argparse


def load_and_align_rasters(*paths):
    """Load multiple rasters and align them to the same grid.

    Args:
        *paths: Paths to GeoTIFF files

    Returns:
        tuple: (list of arrays, metadata, bounds)
    """
    # Load first raster as reference
    with rasterio.open(paths[0]) as src:
        ref_data = src.read(1)
        ref_meta = src.meta.copy()
        ref_bounds = src.bounds
        ref_transform = src.transform
        ref_crs = src.crs

    aligned_arrays = [ref_data]

    # Align other rasters to reference
    for path in paths[1:]:
        with rasterio.open(path) as src:
            data = src.read(1)

            # Check if alignment needed
            if src.crs != ref_crs or src.bounds != ref_bounds:
                # Reproject to match reference
                transform, width, height = calculate_default_transform(
                    src.crs, ref_crs, src.width, src.height, *src.bounds
                )

                aligned = np.empty((ref_data.shape[0], ref_data.shape[1]), dtype=data.dtype)
                reproject(
                    source=data,
                    destination=aligned,
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=ref_transform,
                    dst_crs=ref_crs,
                    resampling=Resampling.nearest
                )
                aligned_arrays.append(aligned)
            else:
                aligned_arrays.append(data)

    return aligned_arrays, ref_meta, ref_bounds


def create_side_by_side_comparison(geotiff_paths, years, output_path, threshold=128, dpi=300):
    """Create side-by-side comparison of multiple years.

    Args:
        geotiff_paths: List of paths to GeoTIFF files
        years: List of year labels
        output_path: Path to save output figure
        threshold: Detection threshold (0-255)
        dpi: Output resolution
    """
    print(f"\nCreating side-by-side comparison for {len(years)} years...")

    # Load and align all rasters
    arrays, meta, bounds = load_and_align_rasters(*geotiff_paths)

    # Convert to binary
    binary_arrays = [(arr > threshold).astype(np.uint8) for arr in arrays]

    # Calculate statistics for each year
    pixel_size = abs(meta['transform'].a)
    stats = []
    for arr in binary_arrays:
        total_pixels = np.sum(arr)
        area_km2 = total_pixels * pixel_size * pixel_size / 1_000_000
        stats.append(area_km2)

    # Create figure
    n_years = len(years)
    fig, axes = plt.subplots(1, n_years, figsize=(6*n_years, 6), dpi=dpi)

    if n_years == 1:
        axes = [axes]

    # Colormap
    cmap = ListedColormap(['white', '#FF6B35'])

    for idx, (ax, binary, year, area) in enumerate(zip(axes, binary_arrays, years, stats)):
        # Plot
        ax.imshow(binary, cmap=cmap, interpolation='nearest',
                 extent=[bounds.left, bounds.right, bounds.bottom, bounds.top])

        # Title with statistics
        ax.set_title(f'{year}\n{area:.2f} km²', fontsize=14, fontweight='bold')

        # Labels
        if idx == 0:
            ax.set_ylabel('Latitude', fontsize=12, fontweight='bold')
        ax.set_xlabel('Longitude', fontsize=12, fontweight='bold')

        # Grid
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.tick_params(labelsize=10)

    # Overall title
    fig.suptitle('Solar Farm Deployment Comparison', fontsize=18, fontweight='bold', y=0.98)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight', facecolor='white')
    print(f"  ✓ Saved: {output_path}")
    plt.close()


def create_change_visualization(geotiff_path1, geotiff_path2, year1, year2,
                                output_path, threshold=128, dpi=300):
    """Create change detection visualization between two years.

    Args:
        geotiff_path1: Path to first year GeoTIFF
        geotiff_path2: Path to second year GeoTIFF
        year1: Label for first year
        year2: Label for second year
        output_path: Path to save output figure
        threshold: Detection threshold
        dpi: Output resolution
    """
    print(f"\nCreating change visualization: {year1} → {year2}...")

    # Load and align rasters
    arrays, meta, bounds = load_and_align_rasters(geotiff_path1, geotiff_path2)
    data1, data2 = arrays

    # Binary classification
    binary1 = (data1 > threshold).astype(np.uint8)
    binary2 = (data2 > threshold).astype(np.uint8)

    # Detect changes
    new_installations = (binary1 == 0) & (binary2 == 1)
    decommissioned = (binary1 == 1) & (binary2 == 0)
    persistent = (binary1 == 1) & (binary2 == 1)
    no_solar = (binary1 == 0) & (binary2 == 0)

    # Create change map
    # 0=no solar, 1=persistent, 2=new, 3=decommissioned
    change_map = np.zeros_like(binary1, dtype=np.uint8)
    change_map[persistent] = 1
    change_map[new_installations] = 2
    change_map[decommissioned] = 3

    # Calculate statistics
    pixel_size = abs(meta['transform'].a)
    pixel_area_km2 = pixel_size * pixel_size / 1_000_000

    area1 = np.sum(binary1) * pixel_area_km2
    area2 = np.sum(binary2) * pixel_area_km2
    new_area = np.sum(new_installations) * pixel_area_km2
    decom_area = np.sum(decommissioned) * pixel_area_km2
    persistent_area = np.sum(persistent) * pixel_area_km2

    # Create 3-panel figure
    fig = plt.figure(figsize=(20, 6), dpi=dpi)

    # Panel 1: Year 1
    ax1 = plt.subplot(1, 3, 1)
    cmap_binary = ListedColormap(['white', '#FF6B35'])
    ax1.imshow(binary1, cmap=cmap_binary, interpolation='nearest',
              extent=[bounds.left, bounds.right, bounds.bottom, bounds.top])
    ax1.set_title(f'{year1}\nTotal: {area1:.2f} km²',
                 fontsize=14, fontweight='bold')
    ax1.set_xlabel('Longitude', fontsize=11)
    ax1.set_ylabel('Latitude', fontsize=11)
    ax1.grid(True, alpha=0.3)

    # Panel 2: Year 2
    ax2 = plt.subplot(1, 3, 2)
    ax2.imshow(binary2, cmap=cmap_binary, interpolation='nearest',
              extent=[bounds.left, bounds.right, bounds.bottom, bounds.top])
    ax2.set_title(f'{year2}\nTotal: {area2:.2f} km²',
                 fontsize=14, fontweight='bold')
    ax2.set_xlabel('Longitude', fontsize=11)
    ax2.set_ylabel('Latitude', fontsize=11)
    ax2.grid(True, alpha=0.3)

    # Panel 3: Change detection
    ax3 = plt.subplot(1, 3, 3)
    cmap_change = ListedColormap(['white', '#FFD700', '#00FF00', '#FF0000'])
    # 0=no solar (white), 1=persistent (gold), 2=new (green), 3=decommissioned (red)
    im3 = ax3.imshow(change_map, cmap=cmap_change, interpolation='nearest',
                     extent=[bounds.left, bounds.right, bounds.bottom, bounds.top])
    ax3.set_title(f'Change Detection\nNet: {(area2-area1):+.2f} km²',
                 fontsize=14, fontweight='bold')
    ax3.set_xlabel('Longitude', fontsize=11)
    ax3.set_ylabel('Latitude', fontsize=11)
    ax3.grid(True, alpha=0.3)

    # Add legend for change map
    legend_elements = [
        mpatches.Patch(facecolor='white', edgecolor='black', label='No Solar'),
        mpatches.Patch(facecolor='#FFD700', edgecolor='black',
                      label=f'Persistent ({persistent_area:.2f} km²)'),
        mpatches.Patch(facecolor='#00FF00', edgecolor='black',
                      label=f'New ({new_area:.2f} km²)'),
        mpatches.Patch(facecolor='#FF0000', edgecolor='black',
                      label=f'Decommissioned ({decom_area:.2f} km²)')
    ]
    ax3.legend(handles=legend_elements, loc='upper right', fontsize=10,
              framealpha=0.9)

    # Overall title
    net_change = area2 - area1
    growth_pct = (net_change / area1 * 100) if area1 > 0 else 0
    fig.suptitle(f'Solar Farm Change Detection: {year1} → {year2} '
                f'(Net Change: {net_change:+.2f} km², {growth_pct:+.1f}%)',
                fontsize=16, fontweight='bold', y=0.98)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight', facecolor='white')
    print(f"  ✓ Saved: {output_path}")

    # Also save as PDF
    pdf_path = output_path.with_suffix('.pdf')
    plt.savefig(pdf_path, bbox_inches='tight', facecolor='white')
    print(f"  ✓ Saved: {pdf_path}")

    plt.close()


def main():
    """Main function for comparison visualizations."""
    parser = argparse.ArgumentParser(description='Compare solar farm detections across years')
    parser.add_argument('geotiffs', nargs='+', help='Paths to GeoTIFF files')
    parser.add_argument('--years', nargs='+', help='Year labels (optional)')
    parser.add_argument('--output-dir', type=str, required=True,
                       help='Output directory')
    parser.add_argument('--mode', choices=['side-by-side', 'change'], default='side-by-side',
                       help='Comparison mode')
    parser.add_argument('--threshold', type=int, default=128,
                       help='Detection threshold (0-255)')
    parser.add_argument('--dpi', type=int, default=300,
                       help='Output resolution')

    args = parser.parse_args()

    # Validate inputs
    geotiff_paths = [Path(p) for p in args.geotiffs]
    for path in geotiff_paths:
        if not path.exists():
            print(f"Error: File not found: {path}")
            return

    # Determine years
    if args.years:
        years = args.years
    else:
        # Try to extract years from filenames
        years = [p.stem.split('_')[-1] if p.stem.split('_')[-1].isdigit()
                else f"Year {i+1}" for i, p in enumerate(geotiff_paths)]

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "="*70)
    print("  Solar Farm Year Comparison")
    print("="*70)
    print(f"  Mode: {args.mode}")
    print(f"  Files: {len(geotiff_paths)}")
    print(f"  Output: {output_dir}")
    print("="*70)

    if args.mode == 'side-by-side':
        output_path = output_dir / "comparison_side_by_side.png"
        create_side_by_side_comparison(geotiff_paths, years, output_path,
                                      args.threshold, args.dpi)

    elif args.mode == 'change' and len(geotiff_paths) == 2:
        output_path = output_dir / f"change_{years[0]}_to_{years[1]}.png"
        create_change_visualization(geotiff_paths[0], geotiff_paths[1],
                                   years[0], years[1], output_path,
                                   args.threshold, args.dpi)

    print("\n" + "="*70)
    print("  ✓ Comparison complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
