#!/bin/bash
#
# Setup using uv (official recommended method)
# This uses Python 3.13 to avoid PyTorch compatibility issues
#

set -e

echo ""
echo "======================================================================="
echo "  CONUS Solar Tracking - uv Setup (Official Method)"
echo "======================================================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if uv is installed
echo "Step 1: Checking for uv..."
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}⚠ uv not found, installing...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
    echo -e "${GREEN}✓ uv installed${NC}"
else
    UV_VERSION=$(uv --version)
    echo -e "${GREEN}✓ Found: $UV_VERSION${NC}"
fi

# Navigate to project root
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)
echo ""
echo "Project root: $PROJECT_ROOT"

# Remove old venv if exists
if [ -d ".venv" ]; then
    echo ""
    echo "Step 2: Found existing .venv directory"
    read -p "Remove and recreate? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing .venv..."
        rm -rf .venv
        echo -e "${GREEN}✓ Removed${NC}"
    else
        echo "Keeping existing .venv. Exiting..."
        exit 0
    fi
fi

# Create venv with Python 3.11 (required by olmoearth_pretrain)
echo ""
echo "Step 3: Creating virtual environment with Python 3.11..."
echo "Note: uv will download Python 3.11 if not available"
echo ""

uv venv --python 3.11

echo -e "${GREEN}✓ Virtual environment created${NC}"

# Activate venv
echo ""
echo "Step 4: Installing dependencies with uv sync..."
echo "This will take 5-10 minutes (PyTorch, etc.)..."
echo ""

uv sync

echo -e "${GREEN}✓ Dependencies installed${NC}"

# Activate and verify
echo ""
echo "Step 5: Verifying installation..."
source .venv/bin/activate

PYTHON_VERSION=$(python --version)
echo "  Python: $PYTHON_VERSION"

# Test imports
echo ""
echo "Testing imports..."

if python -c "import torch; print(f'  ✓ PyTorch {torch.__version__}')" 2>/dev/null; then
    echo -e "${GREEN}  ✓ PyTorch${NC}"
else
    echo -e "${RED}  ✗ PyTorch import failed${NC}"
fi

if python -c "import rslearn; print('  ✓ rslearn')" 2>/dev/null; then
    echo -e "${GREEN}  ✓ rslearn${NC}"
else
    echo -e "${RED}  ✗ rslearn import failed${NC}"
fi

if python -c "import olmoearth_pretrain; print('  ✓ olmoearth_pretrain')" 2>/dev/null; then
    echo -e "${GREEN}  ✓ olmoearth_pretrain${NC}"
else
    echo -e "${RED}  ✗ olmoearth_pretrain import failed${NC}"
fi

if python -c "from olmoearth_run.runner.local.fine_tune_runner import OlmoEarthRunFineTuneRunner; print('  ✓ olmoearth-runner')" 2>/dev/null; then
    echo -e "${GREEN}  ✓ olmoearth-runner${NC}"
else
    echo -e "${RED}  ✗ olmoearth-runner import failed${NC}"
fi

if python -c "import matplotlib; print('  ✓ matplotlib')" 2>/dev/null; then
    echo -e "${GREEN}  ✓ matplotlib${NC}"
else
    echo -e "${RED}  ✗ matplotlib import failed${NC}"
fi

if python -c "import geopandas; print('  ✓ geopandas')" 2>/dev/null; then
    echo -e "${GREEN}  ✓ geopandas${NC}"
else
    echo -e "${RED}  ✗ geopandas import failed${NC}"
fi

# Install visualization packages
echo ""
echo "Step 6: Installing visualization dependencies..."
uv pip install matplotlib-scalebar tabulate
echo -e "${GREEN}✓ Visualization packages installed${NC}"

# Check for GPU
echo ""
echo "Step 7: Checking for GPU..."
if python -c "import torch; assert torch.cuda.is_available()" 2>/dev/null; then
    GPU_NAME=$(python -c "import torch; print(torch.cuda.get_device_name(0))")
    echo -e "${GREEN}  ✓ GPU detected: $GPU_NAME${NC}"
else
    echo -e "${YELLOW}  ⚠ No GPU detected (CPU only - inference will be very slow)${NC}"
    echo "    For GPU support, you need an NVIDIA GPU with CUDA"
fi

# Summary
echo ""
echo "======================================================================="
echo -e "${GREEN}  ✓ Setup Complete!${NC}"
echo "======================================================================="
echo ""
echo "Environment is ready to use."
echo ""
echo "To activate the environment in future sessions:"
echo "  ${GREEN}source .venv/bin/activate${NC}"
echo ""
echo "Next steps:"
echo "  1. Run Phoenix test:"
echo "     ${GREEN}source .venv/bin/activate${NC}"
echo "     ${GREEN}bash conus_solar_tracking/run_phoenix_test.sh${NC}"
echo ""
echo "  2. Or run manually:"
echo "     ${GREEN}python -m olmoearth_projects.main olmoearth_run olmoearth_run \\\\${NC}"
echo "       --config_path conus_solar_tracking/configs/test/ \\\\"
echo "       --checkpoint_path gs://...ckpt \\\\"
echo "       --scratch_path conus_solar_tracking/scratch/test/"
echo ""
echo "======================================================================="
