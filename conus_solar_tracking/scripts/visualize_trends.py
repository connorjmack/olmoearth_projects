#!/usr/bin/env python3
"""
Visualize solar farm deployment trends across CONUS (2017-2025).

Generates plots and charts showing:
- Cumulative solar farm area over time
- Annual new installations
- Growth rates
- Year-over-year comparisons
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
from datetime import datetime


def create_deployment_trends_plot(df, output_dir):
    """Create comprehensive deployment trends visualization.

    Args:
        df: DataFrame with change detection statistics
        output_dir: Directory to save plot
    """
    # Build cumulative area timeline
    years = [df['year1'].iloc[0]] + df['year2'].tolist()
    cumulative_area = [df['total_year1_km2'].iloc[0]] + df['total_year2_km2'].tolist()

    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Plot 1: Cumulative area over time
    ax1.plot(years, cumulative_area, marker='o', linewidth=2.5,
             markersize=8, color='#2E86AB', label='Total Area')
    ax1.fill_between(years, cumulative_area, alpha=0.3, color='#2E86AB')

    ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Total Solar Farm Area (km²)', fontsize=12, fontweight='bold')
    ax1.set_title('CONUS Solar Farm Deployment (2017-2025)',
                  fontsize=14, fontweight='bold', pad=20)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_xlim(2016.5, 2025.5)

    # Add value labels on points
    for year, area in zip(years, cumulative_area):
        ax1.annotate(f'{area:,.0f}',
                    xy=(year, area),
                    xytext=(0, 10),
                    textcoords='offset points',
                    ha='center',
                    fontsize=9,
                    color='#2E86AB')

    # Plot 2: Annual new installations
    colors = ['#A23B72' if val >= 0 else '#F18F01'
              for val in df['net_change_km2']]

    bars = ax2.bar(df['year2'], df['new_installations_km2'],
                   color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)

    ax2.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax2.set_ylabel('New Installations (km²)', fontsize=12, fontweight='bold')
    ax2.set_title('Annual Solar Farm Growth',
                  fontsize=14, fontweight='bold', pad=20)
    ax2.grid(True, alpha=0.3, linestyle='--', axis='y')
    ax2.set_xlim(2017.5, 2025.5)

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax2.annotate(f'{height:,.0f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5),
                    textcoords='offset points',
                    ha='center',
                    fontsize=9,
                    color='black')

    plt.tight_layout()

    # Save plot
    output_path = output_dir / "deployment_trends.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")

    # Also save as PDF for publication quality
    output_path_pdf = output_dir / "deployment_trends.pdf"
    plt.savefig(output_path_pdf, bbox_inches='tight')
    print(f"✓ Saved: {output_path_pdf}")

    plt.close()


def create_growth_rate_plot(df, output_dir):
    """Create growth rate visualization.

    Args:
        df: DataFrame with change detection statistics
        output_dir: Directory to save plot
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    # Create bar plot with color based on positive/negative growth
    colors = ['#06A77D' if rate >= 0 else '#D62828'
              for rate in df['growth_rate_pct']]

    bars = ax.bar(df['year2'], df['growth_rate_pct'],
                  color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)

    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    ax.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Year-over-Year Growth Rate (%)', fontsize=12, fontweight='bold')
    ax.set_title('Solar Farm Deployment Growth Rate (2017-2025)',
                 fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
    ax.set_xlim(2017.5, 2025.5)

    # Add value labels
    for bar in bars:
        height = bar.get_height()
        label_y = height + (1 if height >= 0 else -3)
        ax.annotate(f'{height:+.1f}%',
                   xy=(bar.get_x() + bar.get_width() / 2, height),
                   xytext=(0, 5 if height >= 0 else -15),
                   textcoords='offset points',
                   ha='center',
                   fontsize=9,
                   color='black',
                   fontweight='bold')

    plt.tight_layout()

    # Save plot
    output_path = output_dir / "growth_rates.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")

    plt.close()


def create_comparison_table(df, output_dir):
    """Create formatted comparison table.

    Args:
        df: DataFrame with change detection statistics
        output_dir: Directory to save table
    """
    # Create formatted table
    table_df = df[['year2', 'total_year2_km2', 'new_installations_km2',
                   'net_change_km2', 'growth_rate_pct']].copy()

    table_df.columns = ['Year', 'Total Area (km²)', 'New Installations (km²)',
                        'Net Change (km²)', 'Growth Rate (%)']

    # Format numbers
    table_df['Total Area (km²)'] = table_df['Total Area (km²)'].apply(lambda x: f'{x:,.2f}')
    table_df['New Installations (km²)'] = table_df['New Installations (km²)'].apply(lambda x: f'{x:,.2f}')
    table_df['Net Change (km²)'] = table_df['Net Change (km²)'].apply(lambda x: f'{x:+,.2f}')
    table_df['Growth Rate (%)'] = table_df['Growth Rate (%)'].apply(lambda x: f'{x:+.2f}%')

    # Save as markdown table
    output_path = output_dir / "summary_table.md"
    with open(output_path, 'w') as f:
        f.write("# CONUS Solar Farm Deployment Summary (2017-2025)\n\n")
        f.write(table_df.to_markdown(index=False))
        f.write("\n\n")
        f.write(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

    print(f"✓ Saved: {output_path}")

    # Also save as CSV for Excel
    csv_path = output_dir / "summary_table.csv"
    table_df.to_csv(csv_path, index=False)
    print(f"✓ Saved: {csv_path}")


def main():
    """Generate all visualizations from change detection results."""
    base_dir = Path(__file__).parent.parent
    analysis_dir = base_dir / "analysis"
    summary_path = analysis_dir / "solar_growth_summary.csv"

    print("\n" + "="*70)
    print("  CONUS Solar Farm Deployment - Visualization Generator")
    print("="*70)

    # Load summary data
    if not summary_path.exists():
        print(f"\n✗ Error: Summary file not found at {summary_path}")
        print("  Run analyze_changes.py first to generate the summary data.")
        return

    print(f"\nLoading summary data from: {summary_path}")
    df = pd.read_csv(summary_path)

    print(f"Years covered: {df['year1'].min()} - {df['year2'].max()}")
    print(f"Total change periods: {len(df)}\n")

    # Create output directory
    analysis_dir.mkdir(parents=True, exist_ok=True)

    # Generate visualizations
    print("Generating visualizations...")
    print("-" * 70)

    create_deployment_trends_plot(df, analysis_dir)
    create_growth_rate_plot(df, analysis_dir)
    create_comparison_table(df, analysis_dir)

    # Print summary statistics
    print("\n" + "="*70)
    print("  SUMMARY STATISTICS")
    print("="*70)

    total_2017 = df['total_year1_km2'].iloc[0]
    total_2025 = df['total_year2_km2'].iloc[-1]
    total_growth = total_2025 - total_2017
    total_growth_pct = (total_growth / total_2017 * 100)
    avg_annual_growth = df['growth_rate_pct'].mean()

    print(f"\n  Total solar farm area in 2017: {total_2017:,.2f} km²")
    print(f"  Total solar farm area in 2025: {total_2025:,.2f} km²")
    print(f"  Total growth (2017-2025): {total_growth:+,.2f} km² ({total_growth_pct:+.1f}%)")
    print(f"  Average annual growth rate: {avg_annual_growth:.2f}%")

    peak_growth_year = df.loc[df['growth_rate_pct'].idxmax(), 'year2']
    peak_growth_rate = df['growth_rate_pct'].max()
    print(f"  Peak growth year: {int(peak_growth_year)} ({peak_growth_rate:.2f}%)")

    print("\n" + "="*70)
    print(f"\n✓ All visualizations saved to: {analysis_dir}/")
    print("\nGenerated files:")
    print(f"  - deployment_trends.png (and .pdf)")
    print(f"  - growth_rates.png")
    print(f"  - summary_table.md (and .csv)")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
