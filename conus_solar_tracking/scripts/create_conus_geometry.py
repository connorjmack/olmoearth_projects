#!/usr/bin/env python3
"""
Generate CONUS prediction request geometries for each year (2017-2025).

Creates GeoJSON files with CONUS bounding box and temporal properties
for each annual snapshot.
"""

import json
from pathlib import Path


def create_conus_geojson(year, output_path):
    """Create CONUS bounding box GeoJSON for a specific year.

    Args:
        year: Year for the prediction (2017-2025)
        output_path: Path where GeoJSON file will be saved
    """
    # CONUS bounding box (covers continental United States)
    west, south = -125.0, 24.0
    east, north = -66.0, 49.5

    # Use summer months (June-September) for best imagery quality
    # - Maximum clear sky conditions
    # - Consistent sun angles
    # - Operational solar farms visible
    start_date = f"{year}-06-01T00:00:00Z"
    end_date = f"{year}-09-01T00:00:00Z"

    geojson = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [west, south],
                    [west, north],
                    [east, north],
                    [east, south],
                    [west, south]
                ]]
            },
            "properties": {
                "oe_start_time": start_date,
                "oe_end_time": end_date,
                "year": year,
                "region": "CONUS",
                "description": f"Continental US solar farm detection for {year}"
            }
        }]
    }

    # Ensure output directory exists
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write GeoJSON file
    with open(output_path, 'w') as f:
        json.dump(geojson, f, indent=2)

    print(f"✓ Created {output_path}")


def main():
    """Generate geometry files for all years (2017-2025)."""
    base_dir = Path(__file__).parent.parent
    geometries_dir = base_dir / "geometries"

    print("Generating CONUS geometry files for 2017-2025...")
    print(f"Output directory: {geometries_dir}\n")

    for year in range(2017, 2026):
        output_path = geometries_dir / f"conus_{year}.geojson"
        create_conus_geojson(year, output_path)

    print(f"\n✓ Successfully generated {2026-2017} geometry files")
    print(f"  Location: {geometries_dir}")


if __name__ == "__main__":
    main()
