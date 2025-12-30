#!/bin/bash

# Setup year-specific configurations for CONUS solar tracking
# Copies base solar farm configs and links year-specific geometries

set -e  # Exit on error

BASE_DIR="/Users/cjmack/Documents/GitHub/olmoearth_projects"
SOLAR_CONFIG="${BASE_DIR}/olmoearth_run_data/satlas_solar_farm"
CONUS_BASE="${BASE_DIR}/conus_solar_tracking"

echo "Setting up year-specific configurations (2017-2025)..."
echo "Base config: ${SOLAR_CONFIG}"
echo "Target dir: ${CONUS_BASE}/configs/"
echo ""

# Counter for success tracking
SUCCESS_COUNT=0

for YEAR in {2017..2025}; do
    CONFIG_DIR="${CONUS_BASE}/configs/${YEAR}"

    echo "Configuring ${YEAR}..."

    # Copy base configuration files
    cp "${SOLAR_CONFIG}/dataset.json" "${CONFIG_DIR}/"
    cp "${SOLAR_CONFIG}/model.yaml" "${CONFIG_DIR}/"
    cp "${SOLAR_CONFIG}/olmoearth_run.yaml" "${CONFIG_DIR}/"

    # Copy year-specific geometry as prediction_request_geometry.geojson
    cp "${CONUS_BASE}/geometries/conus_${YEAR}.geojson" \
       "${CONFIG_DIR}/prediction_request_geometry.geojson"

    echo "  ✓ Copied config files"
    echo "  ✓ Linked geometry for ${YEAR}"

    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
done

echo ""
echo "========================================="
echo "✓ Successfully configured ${SUCCESS_COUNT} years"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Modify olmoearth_run.yaml to increase grid_size to 2.0 for CONUS scale"
echo "2. Review configs in ${CONUS_BASE}/configs/"
echo "3. Run test inference on Phoenix region before full CONUS"
