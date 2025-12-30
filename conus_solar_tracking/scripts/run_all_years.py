#!/usr/bin/env python3
"""
Run solar farm inference for all years (2017-2025) sequentially.

This script runs the OlmoEarth inference pipeline for each year, processing
the entire continental US and generating GeoTIFF outputs for each year.
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime


# Model checkpoint location
CHECKPOINT = "gs://ai2-rslearn-projects-data/projects/2025_11_05_satlas_solar_farm/2025_11_05_model_update/epoch=9999-step=99999.ckpt"


def run_year(year, base_dir, conus_base, checkpoint_path):
    """Run inference for a single year.

    Args:
        year: Year to process (2017-2025)
        base_dir: Base olmoearth_projects directory
        conus_base: CONUS solar tracking directory
        checkpoint_path: Path to model checkpoint

    Returns:
        bool: True if successful, False otherwise
    """
    config_path = conus_base / f"configs/{year}"
    scratch_path = conus_base / f"scratch/{year}"
    result_dst = conus_base / f"results/{year}"

    print(f"\n{'='*70}")
    print(f"  Starting inference for {year}")
    print(f"{'='*70}")
    print(f"  Config: {config_path}")
    print(f"  Scratch: {scratch_path}")
    print(f"  Output: {result_dst}")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")

    # Build command
    cmd = [
        "python", "-m", "olmoearth_projects.main",
        "olmoearth_run", "olmoearth_run",
        "--config_path", str(config_path),
        "--checkpoint_path", checkpoint_path,
        "--scratch_path", str(scratch_path)
    ]

    try:
        # Run inference
        start_time = datetime.now()
        subprocess.run(cmd, check=True, cwd=base_dir)
        end_time = datetime.now()
        duration = end_time - start_time

        print(f"\n{'='*70}")
        print(f"  ✓ Successfully completed {year}")
        print(f"  Duration: {duration}")
        print(f"  Finished: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")

        # Copy results to permanent storage
        result_src = scratch_path / "results/results_raster"
        if result_src.exists():
            print(f"Copying results to {result_dst}...")
            subprocess.run(["cp", "-r", str(result_src / "*"), str(result_dst)],
                          shell=True, check=False)
            print(f"✓ Results copied to {result_dst}\n")
        else:
            print(f"⚠ Warning: No results found at {result_src}\n")

        return True

    except subprocess.CalledProcessError as e:
        print(f"\n{'='*70}")
        print(f"  ✗ Error processing {year}")
        print(f"  Error code: {e.returncode}")
        print(f"{'='*70}\n")
        print("To resume from this year, re-run this script.")
        print("The pipeline supports stage-based recovery.")
        return False


def main():
    """Run inference for all years sequentially."""
    base_dir = Path("/Users/cjmack/Documents/GitHub/olmoearth_projects")
    conus_base = base_dir / "conus_solar_tracking"

    # Allow specifying starting year as command line argument
    start_year = 2017
    if len(sys.argv) > 1:
        try:
            start_year = int(sys.argv[1])
            if start_year < 2017 or start_year > 2025:
                print(f"Error: Year must be between 2017 and 2025")
                sys.exit(1)
        except ValueError:
            print(f"Error: Invalid year '{sys.argv[1]}'")
            print(f"Usage: {sys.argv[0]} [start_year]")
            sys.exit(1)

    years = range(start_year, 2026)

    print("\n" + "="*70)
    print("  CONUS Solar Farm Deployment Tracking (2017-2025)")
    print("="*70)
    print(f"  Years to process: {list(years)}")
    print(f"  Checkpoint: {CHECKPOINT[:80]}...")
    print(f"  Working directory: {conus_base}")
    print("="*70 + "\n")

    completed_years = []
    failed_year = None

    for year in years:
        success = run_year(year, base_dir, conus_base, CHECKPOINT)
        if success:
            completed_years.append(year)
        else:
            failed_year = year
            break

    # Print summary
    print("\n" + "="*70)
    print("  EXECUTION SUMMARY")
    print("="*70)
    print(f"  Completed years: {completed_years}")
    if failed_year:
        print(f"  Failed at: {failed_year}")
        print(f"\n  To resume, run: python {sys.argv[0]} {failed_year}")
        sys.exit(1)
    else:
        print(f"  Status: ✓ All {len(completed_years)} years completed successfully!")
        print(f"\n  Next steps:")
        print(f"  1. Run change detection: python scripts/analyze_changes.py")
        print(f"  2. Generate visualizations: python scripts/visualize_trends.py")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
