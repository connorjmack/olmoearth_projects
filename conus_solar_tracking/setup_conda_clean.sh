#!/bin/bash
#
# Clean Conda Environment Setup - Uses environment.yml
#

set -e

echo ""
echo "======================================================================="
echo "  CONUS Solar Tracking - Clean Conda Setup"
echo "======================================================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if conda is installed
echo "Step 1: Checking for conda..."
if ! command -v conda &> /dev/null; then
    echo -e "${RED}✗ conda not found${NC}"
    echo ""
    echo "Please install Miniconda first:"
    echo "  curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh"
    echo "  bash Miniconda3-latest-MacOSX-arm64.sh"
    echo ""
    echo "Then restart your terminal and run this script again."
    exit 1
else
    CONDA_VERSION=$(conda --version)
    echo -e "${GREEN}✓ Found: $CONDA_VERSION${NC}"
fi

# Initialize conda
echo ""
echo "Initializing conda..."
conda init bash 2>/dev/null || true
conda init zsh 2>/dev/null || true

# Source conda
if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/miniconda3/etc/profile.d/conda.sh"
elif [ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/anaconda3/etc/profile.d/conda.sh"
fi

# Check if environment already exists
echo ""
echo "Step 2: Checking for existing 'olmoearth' environment..."
if conda env list | grep -q "^olmoearth "; then
    echo -e "${YELLOW}⚠ Environment 'olmoearth' already exists${NC}"
    read -p "Remove and recreate? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing environment..."
        conda deactivate 2>/dev/null || true
        conda env remove -n olmoearth -y
        echo -e "${GREEN}✓ Removed${NC}"
    else
        echo "Keeping existing environment. Exiting..."
        exit 0
    fi
fi

# Navigate to project directory
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)
echo "Project root: $PROJECT_ROOT"

# Create environment from YAML
echo ""
echo "Step 3: Creating conda environment from environment.yml..."
echo "This will take 5-10 minutes (downloading PyTorch, etc.)..."
echo ""

conda env create -f conus_solar_tracking/environment.yml

echo -e "${GREEN}✓ Environment created${NC}"

# Activate environment
echo ""
echo "Step 4: Activating environment..."
conda activate olmoearth
PYTHON_VERSION=$(python --version)
echo -e "${GREEN}✓ Activated: $PYTHON_VERSION${NC}"

# Install the project in editable mode
echo ""
echo "Step 5: Installing olmoearth_projects in editable mode..."
pip install -e .
echo -e "${GREEN}✓ Project installed${NC}"

# Verify installation
echo ""
echo "Step 6: Verifying installation..."

# Test PyTorch
if python -c "import torch; print(f'PyTorch {torch.__version__}')" 2>/dev/null; then
    echo -e "${GREEN}  ✓ PyTorch${NC}"
else
    echo -e "${RED}  ✗ PyTorch import failed${NC}"
fi

# Test rslearn
if python -c "import rslearn" 2>/dev/null; then
    echo -e "${GREEN}  ✓ rslearn${NC}"
else
    echo -e "${RED}  ✗ rslearn import failed${NC}"
fi

# Test olmoearth_pretrain
if python -c "import olmoearth_pretrain" 2>/dev/null; then
    echo -e "${GREEN}  ✓ olmoearth_pretrain${NC}"
else
    echo -e "${RED}  ✗ olmoearth_pretrain import failed${NC}"
fi

# Test olmoearth-runner
if python -c "from olmoearth_run.runner.local.fine_tune_runner import OlmoEarthRunFineTuneRunner" 2>/dev/null; then
    echo -e "${GREEN}  ✓ olmoearth-runner${NC}"
else
    echo -e "${RED}  ✗ olmoearth-runner import failed${NC}"
fi

# Test matplotlib
if python -c "import matplotlib" 2>/dev/null; then
    echo -e "${GREEN}  ✓ matplotlib${NC}"
else
    echo -e "${RED}  ✗ matplotlib import failed${NC}"
fi

# Test geopandas
if python -c "import geopandas" 2>/dev/null; then
    echo -e "${GREEN}  ✓ geopandas${NC}"
else
    echo -e "${RED}  ✗ geopandas import failed${NC}"
fi

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
echo "Environment 'olmoearth' is ready to use."
echo ""
echo "To activate the environment in future sessions:"
echo "  ${GREEN}conda activate olmoearth${NC}"
echo ""
echo "Next steps:"
echo "  1. Run Phoenix test:"
echo "     ${GREEN}bash conus_solar_tracking/run_phoenix_test.sh${NC}"
echo ""
echo "  2. Or run manually:"
echo "     ${GREEN}conda activate olmoearth${NC}"
echo "     ${GREEN}python -m olmoearth_projects.main olmoearth_run olmoearth_run \\\\${NC}"
echo "       --config_path conus_solar_tracking/configs/test/ \\\\"
echo "       --checkpoint_path gs://...ckpt \\\\"
echo "       --scratch_path conus_solar_tracking/scratch/test/"
echo ""
echo "======================================================================="
