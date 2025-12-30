#!/bin/bash
#
# Run Phoenix Test and Generate Visualizations
#
# This script runs the complete Phoenix test workflow:
# 1. Checks environment is activated
# 2. Runs inference on Phoenix region
# 3. Generates publication-quality visualizations
#

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "======================================================================="
echo "  Phoenix Solar Farm Detection Test"
echo "======================================================================="
echo ""

# Check if environment is activated (conda or venv)
if [[ "$CONDA_DEFAULT_ENV" == "olmoearth" ]]; then
    echo -e "${GREEN}✓ Conda environment activated: $CONDA_DEFAULT_ENV${NC}"
    echo "  Python: $(python --version)"
elif [[ "$VIRTUAL_ENV" == *".venv"* ]]; then
    echo -e "${GREEN}✓ Virtual environment activated${NC}"
    echo "  Python: $(python --version)"
else
    echo -e "${RED}✗ Error: No environment activated${NC}"
    echo ""
    echo "Please activate the environment first:"
    echo "  For uv (recommended):  ${GREEN}source .venv/bin/activate${NC}"
    echo "  For conda:             ${GREEN}conda activate olmoearth${NC}"
    echo ""
    echo "Or run setup if you haven't already:"
    echo "  For uv (recommended):  ${GREEN}bash conus_solar_tracking/setup_uv.sh${NC}"
    echo "  For conda:             ${GREEN}bash conus_solar_tracking/setup_conda_clean.sh${NC}"
    echo ""
    exit 1
fi
echo ""

# Navigate to project root
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)
echo "Project root: $PROJECT_ROOT"
echo ""

# Checkpoint path
CHECKPOINT="gs://ai2-rslearn-projects-data/projects/2025_11_05_satlas_solar_farm/2025_11_05_model_update/epoch=9999-step=99999.ckpt"

echo "======================================================================="
echo "  Step 1: Running Inference on Phoenix Region"
echo "======================================================================="
echo ""
echo "This will take approximately 10-15 minutes."
echo "What happens:"
echo "  1. Download checkpoint (~2-5 min, first time only)"
echo "  2. Download Sentinel-2 imagery (~2-5 min)"
echo "  3. Run model inference (~5-10 min)"
echo ""
echo "Press Ctrl+C to cancel, or wait a moment to start..."
sleep 3

echo ""
echo "Starting inference..."
echo ""

# Run inference
python -m olmoearth_projects.main olmoearth_run olmoearth_run \
  --config_path conus_solar_tracking/configs/test/ \
  --checkpoint_path "$CHECKPOINT" \
  --scratch_path conus_solar_tracking/scratch/test/

INFERENCE_EXIT_CODE=$?

if [ $INFERENCE_EXIT_CODE -ne 0 ]; then
    echo ""
    echo -e "${RED}✗ Inference failed with exit code $INFERENCE_EXIT_CODE${NC}"
    echo ""
    echo "Check the error messages above for details."
    echo "Common issues:"
    echo "  - GPU out of memory: Reduce batch_size in configs/test/model.yaml"
    echo "  - Network issues: Check internet connection"
    echo "  - Missing dependencies: Run setup_conda_auto.sh again"
    echo ""
    exit 1
fi

echo ""
echo -e "${GREEN}✓ Inference complete!${NC}"
echo ""

# Check if GeoTIFF was created
GEOTIFF_DIR="conus_solar_tracking/scratch/test/results/results_raster"
if [ ! -d "$GEOTIFF_DIR" ] || [ -z "$(ls -A $GEOTIFF_DIR/*.tif 2>/dev/null)" ]; then
    echo -e "${RED}✗ No GeoTIFF output found in $GEOTIFF_DIR${NC}"
    echo "Inference may have failed. Check logs for errors."
    exit 1
fi

echo -e "${GREEN}✓ GeoTIFF output found${NC}"
ls -lh "$GEOTIFF_DIR"/*.tif
echo ""

echo "======================================================================="
echo "  Step 2: Generating Visualizations"
echo "======================================================================="
echo ""
echo "Creating publication-quality figures..."
echo ""

# Run visualization script
python conus_solar_tracking/scripts/run_phoenix_visualizations.py

VIZ_EXIT_CODE=$?

if [ $VIZ_EXIT_CODE -ne 0 ]; then
    echo ""
    echo -e "${YELLOW}⚠ Visualization script failed${NC}"
    echo "However, the GeoTIFF is ready and you can visualize it manually:"
    echo "  open $GEOTIFF_DIR"
    echo ""
    exit 0
fi

echo ""
echo -e "${GREEN}✓ Visualizations complete!${NC}"
echo ""

echo "======================================================================="
echo -e "${GREEN}  ✓ Phoenix Test Complete!${NC}"
echo "======================================================================="
echo ""
echo "Results saved to:"
echo "  ${GREEN}conus_solar_tracking/test_results/${NC}"
echo ""
echo "Generated files:"
echo "  - GeoTIFF: $(ls $GEOTIFF_DIR/*.tif 2>/dev/null | head -1)"
echo "  - Figures: conus_solar_tracking/test_results/figures/"
echo "  - Report: conus_solar_tracking/test_results/TEST_RESULTS_SUMMARY.md"
echo ""
echo "View results:"
echo "  ${GREEN}open conus_solar_tracking/test_results/figures/${NC}"
echo "  ${GREEN}cat conus_solar_tracking/test_results/TEST_RESULTS_SUMMARY.md${NC}"
echo ""
echo "Next steps:"
echo "  1. Review the test results"
echo "  2. If satisfied, run full CONUS analysis:"
echo "     ${GREEN}python conus_solar_tracking/scripts/run_all_years.py${NC}"
echo ""
echo "======================================================================="
