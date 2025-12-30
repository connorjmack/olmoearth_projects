#!/usr/bin/env python3
"""
Create publication-quality maps from solar farm detection GeoTIFF files.

Generates high-resolution maps with:
- Solar farm detections overlaid on satellite basemap
- Scale bars, north arrows, legends
- Multiple color schemes and transparency options
- Export to PNG, PDF, and SVG formats
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
from matplotlib_scalebar.scalebar import ScaleBar
import rasterio
from rasterio.plot import show
from pathlib import Path
import argparse


def create_solar_farm_map(geotiff_path, output_dir, title=None, threshold=128,
                          dpi=300, figsize=(12, 10)):
    """Create publication-quality map from solar farm GeoTIFF.

    Args:
        geotiff_path: Path to input GeoTIFF file
        output_dir: Directory to save output figures
        title: Optional title for the map
        threshold: Threshold for binary classification (0-255)
        dpi: Resolution for output images
        figsize: Figure size in inches (width, height)
    """
    print(f"\nCreating map from: {geotiff_path}")

    # Load GeoTIFF
    with rasterio.open(geotiff_path) as src:
        data = src.read(1)
        bounds = src.bounds
        crs = src.crs
        transform = src.transform

        # Get resolution in meters
        pixel_size_x = abs(transform.a)
        pixel_size_y = abs(transform.e)

    print(f"  Raster size: {data.shape}")
    print(f"  CRS: {crs}")
    print(f"  Bounds: {bounds}")
    print(f"  Resolution: {pixel_size_x}m x {pixel_size_y}m")

    # Calculate statistics
    binary_data = (data > threshold).astype(np.uint8)
    total_pixels = np.sum(binary_data)
    total_area_km2 = total_pixels * pixel_size_x * pixel_size_y / 1_000_000

    print(f"  Solar farm pixels: {total_pixels:,}")
    print(f"  Total area: {total_area_km2:.2f} km²")

    # Create figure with high DPI
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    # Display detection results
    # Create custom colormap: white background, solar farms in orange/red
    from matplotlib.colors import ListedColormap
    colors = ['white', '#FF6B35']  # White for no solar, vibrant orange for solar
    cmap = ListedColormap(colors)

    # Plot binary detection
    im = ax.imshow(binary_data, cmap=cmap, interpolation='nearest',
                   extent=[bounds.left, bounds.right, bounds.bottom, bounds.top])

    # Add title
    if title:
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    else:
        ax.set_title('Solar Farm Detections', fontsize=16, fontweight='bold', pad=20)

    # Add labels
    ax.set_xlabel('Longitude', fontsize=12, fontweight='bold')
    ax.set_ylabel('Latitude', fontsize=12, fontweight='bold')

    # Add scale bar
    scalebar = ScaleBar(
        pixel_size_x,
        units='m',
        location='lower right',
        length_fraction=0.2,
        width_fraction=0.02,
        box_alpha=0.8,
        color='black',
        font_properties={'size': 10, 'weight': 'bold'}
    )
    ax.add_artist(scalebar)

    # Add north arrow
    arrow_x = bounds.left + (bounds.right - bounds.left) * 0.95
    arrow_y = bounds.bottom + (bounds.top - bounds.bottom) * 0.95
    ax.annotate('N', xy=(arrow_x, arrow_y), xytext=(arrow_x, arrow_y - (bounds.top - bounds.bottom) * 0.05),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'),
                fontsize=14, fontweight='bold', ha='center')

    # Add legend
    legend_elements = [
        mpatches.Patch(facecolor='white', edgecolor='black', label='No Solar Farm'),
        mpatches.Patch(facecolor='#FF6B35', edgecolor='black', label=f'Solar Farm ({total_area_km2:.1f} km²)')
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=11, framealpha=0.9)

    # Add grid
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)

    # Format tick labels
    ax.tick_params(axis='both', labelsize=10)

    plt.tight_layout()

    # Save in multiple formats
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    base_name = Path(geotiff_path).stem

    # PNG (high resolution)
    png_path = output_dir / f"{base_name}_map.png"
    plt.savefig(png_path, dpi=dpi, bbox_inches='tight', facecolor='white')
    print(f"  ✓ Saved: {png_path}")

    # PDF (vector, publication quality)
    pdf_path = output_dir / f"{base_name}_map.pdf"
    plt.savefig(pdf_path, bbox_inches='tight', facecolor='white')
    print(f"  ✓ Saved: {pdf_path}")

    plt.close()

    # Create heat map version (probability visualization)
    create_heatmap(geotiff_path, data, bounds, output_dir, title, dpi, figsize)


def create_heatmap(geotiff_path, data, bounds, output_dir, title, dpi, figsize):
    """Create heat map visualization of solar farm probabilities."""

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    # Use continuous colormap for probabilities
    from matplotlib.colors import LinearSegmentedColormap
    colors_gradient = ['#f7f7f7', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
    cmap = LinearSegmentedColormap.from_list('solar_heat', colors_gradient)

    # Plot probability values
    im = ax.imshow(data, cmap=cmap, interpolation='bilinear', vmin=0, vmax=255,
                   extent=[bounds.left, bounds.right, bounds.bottom, bounds.top])

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Detection Confidence (0-255)', rotation=270, labelpad=20,
                   fontsize=11, fontweight='bold')
    cbar.ax.tick_params(labelsize=10)

    # Add title
    if title:
        ax.set_title(f"{title} - Probability Heat Map", fontsize=16, fontweight='bold', pad=20)
    else:
        ax.set_title('Solar Farm Detection Probability', fontsize=16, fontweight='bold', pad=20)

    # Labels and formatting
    ax.set_xlabel('Longitude', fontsize=12, fontweight='bold')
    ax.set_ylabel('Latitude', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    ax.tick_params(axis='both', labelsize=10)

    plt.tight_layout()

    # Save heatmap
    base_name = Path(geotiff_path).stem
    heatmap_path = output_dir / f"{base_name}_heatmap.png"
    plt.savefig(heatmap_path, dpi=dpi, bbox_inches='tight', facecolor='white')
    print(f"  ✓ Saved: {heatmap_path}")

    plt.close()


def create_overview_panel(geotiff_path, output_dir, title=None, threshold=128, dpi=300):
    """Create multi-panel overview figure with different visualizations."""

    print(f"\nCreating multi-panel overview...")

    with rasterio.open(geotiff_path) as src:
        data = src.read(1)
        bounds = src.bounds
        transform = src.transform
        pixel_size = abs(transform.a)

    binary_data = (data > threshold).astype(np.uint8)

    # Create 2x2 panel figure
    fig = plt.figure(figsize=(16, 14), dpi=dpi)

    # Panel 1: Binary detection
    ax1 = plt.subplot(2, 2, 1)
    from matplotlib.colors import ListedColormap
    cmap_binary = ListedColormap(['white', '#FF6B35'])
    ax1.imshow(binary_data, cmap=cmap_binary, interpolation='nearest',
               extent=[bounds.left, bounds.right, bounds.bottom, bounds.top])
    ax1.set_title('A) Binary Detection', fontsize=14, fontweight='bold', loc='left')
    ax1.set_xlabel('Longitude', fontsize=11)
    ax1.set_ylabel('Latitude', fontsize=11)
    ax1.grid(True, alpha=0.3)

    # Panel 2: Probability heat map
    ax2 = plt.subplot(2, 2, 2)
    from matplotlib.colors import LinearSegmentedColormap
    colors_gradient = ['#f7f7f7', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
    cmap_heat = LinearSegmentedColormap.from_list('solar_heat', colors_gradient)
    im2 = ax2.imshow(data, cmap=cmap_heat, interpolation='bilinear', vmin=0, vmax=255,
                     extent=[bounds.left, bounds.right, bounds.bottom, bounds.top])
    ax2.set_title('B) Detection Confidence', fontsize=14, fontweight='bold', loc='left')
    ax2.set_xlabel('Longitude', fontsize=11)
    ax2.set_ylabel('Latitude', fontsize=11)
    ax2.grid(True, alpha=0.3)
    cbar2 = plt.colorbar(im2, ax=ax2, fraction=0.046)
    cbar2.set_label('Confidence (0-255)', rotation=270, labelpad=15, fontsize=10)

    # Panel 3: Detection density (spatial binning)
    ax3 = plt.subplot(2, 2, 3)
    # Create coarser grid for density visualization
    bin_size = max(10, data.shape[0] // 50)
    density = np.zeros((data.shape[0] // bin_size, data.shape[1] // bin_size))
    for i in range(density.shape[0]):
        for j in range(density.shape[1]):
            block = binary_data[i*bin_size:(i+1)*bin_size, j*bin_size:(j+1)*bin_size]
            density[i, j] = np.mean(block) * 100  # Percentage

    im3 = ax3.imshow(density, cmap='YlOrRd', interpolation='bilinear',
                     extent=[bounds.left, bounds.right, bounds.bottom, bounds.top])
    ax3.set_title('C) Detection Density', fontsize=14, fontweight='bold', loc='left')
    ax3.set_xlabel('Longitude', fontsize=11)
    ax3.set_ylabel('Latitude', fontsize=11)
    ax3.grid(True, alpha=0.3)
    cbar3 = plt.colorbar(im3, ax=ax3, fraction=0.046)
    cbar3.set_label('Solar Coverage (%)', rotation=270, labelpad=15, fontsize=10)

    # Panel 4: Statistics summary
    ax4 = plt.subplot(2, 2, 4)
    ax4.axis('off')

    # Calculate statistics
    total_pixels = np.sum(binary_data)
    total_area_km2 = total_pixels * pixel_size * pixel_size / 1_000_000
    total_area_acres = total_area_km2 * 247.105
    coverage_pct = (total_pixels / binary_data.size) * 100

    stats_text = f"""
    DETECTION STATISTICS
    {'='*40}

    Region Bounds:
      West:  {bounds.left:.4f}°
      East:  {bounds.right:.4f}°
      South: {bounds.bottom:.4f}°
      North: {bounds.top:.4f}°

    Raster Properties:
      Resolution: {pixel_size:.1f}m
      Dimensions: {data.shape[1]} × {data.shape[0]} pixels
      Total Area: {data.shape[0] * data.shape[1] * pixel_size**2 / 1e6:.1f} km²

    Solar Farm Detection:
      Detected Pixels: {total_pixels:,}
      Solar Farm Area: {total_area_km2:.2f} km²
      Solar Farm Area: {total_area_acres:.1f} acres
      Coverage: {coverage_pct:.3f}%

    Detection Threshold: {threshold}/255
    """

    ax4.text(0.1, 0.95, stats_text, transform=ax4.transAxes,
             fontsize=11, verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

    # Overall title
    if title:
        fig.suptitle(title, fontsize=18, fontweight='bold', y=0.98)
    else:
        fig.suptitle('Solar Farm Detection Overview', fontsize=18, fontweight='bold', y=0.98)

    plt.tight_layout(rect=[0, 0, 1, 0.96])

    # Save multi-panel figure
    output_dir = Path(output_dir)
    base_name = Path(geotiff_path).stem
    overview_path = output_dir / f"{base_name}_overview.png"
    plt.savefig(overview_path, dpi=dpi, bbox_inches='tight', facecolor='white')
    print(f"  ✓ Saved: {overview_path}")

    # Also save as PDF
    overview_pdf_path = output_dir / f"{base_name}_overview.pdf"
    plt.savefig(overview_pdf_path, bbox_inches='tight', facecolor='white')
    print(f"  ✓ Saved: {overview_pdf_path}")

    plt.close()


def main():
    """Main function to process GeoTIFF and create visualizations."""
    parser = argparse.ArgumentParser(description='Create publication-quality maps from solar farm GeoTIFFs')
    parser.add_argument('geotiff', type=str, help='Path to input GeoTIFF file')
    parser.add_argument('--output-dir', type=str, default=None,
                       help='Output directory (default: same as input + _figures)')
    parser.add_argument('--title', type=str, default=None,
                       help='Title for the map')
    parser.add_argument('--threshold', type=int, default=128,
                       help='Detection threshold (0-255, default: 128)')
    parser.add_argument('--dpi', type=int, default=300,
                       help='Output resolution in DPI (default: 300)')

    args = parser.parse_args()

    geotiff_path = Path(args.geotiff)

    if not geotiff_path.exists():
        print(f"Error: File not found: {geotiff_path}")
        return

    # Determine output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = geotiff_path.parent / f"{geotiff_path.stem}_figures"

    print("\n" + "="*70)
    print("  Solar Farm GeoTIFF Visualization")
    print("="*70)
    print(f"  Input: {geotiff_path}")
    print(f"  Output: {output_dir}")
    print("="*70)

    # Create visualizations
    create_solar_farm_map(geotiff_path, output_dir, args.title, args.threshold, args.dpi)
    create_overview_panel(geotiff_path, output_dir, args.title, args.threshold, args.dpi)

    print("\n" + "="*70)
    print("  ✓ Visualization complete!")
    print(f"  Output directory: {output_dir}")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
