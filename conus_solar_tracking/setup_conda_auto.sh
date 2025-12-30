#!/bin/bash
#
# Automated Conda Environment Setup for CONUS Solar Tracking
#
# This script will:
# 1. Check if conda is installed
# 2. Create olmoearth environment with Python 3.13
# 3. Install all dependencies
# 4. Verify installation
#

set -e  # Exit on error

echo ""
echo "======================================================================="
echo "  CONUS Solar Tracking - Automated Conda Setup"
echo "======================================================================="
echo ""

# Colors for output
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

# Initialize conda for bash/zsh
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
        echo "Using existing environment..."
        conda activate olmoearth
        echo -e "${GREEN}✓ Activated existing environment${NC}"
        SKIP_CREATE=1
    fi
fi

# Create environment
if [ -z "$SKIP_CREATE" ]; then
    echo ""
    echo "Step 3: Creating conda environment 'olmoearth' with Python 3.11..."
    conda create -n olmoearth python=3.11 -y
    echo -e "${GREEN}✓ Environment created${NC}"
fi

# Activate environment
echo ""
echo "Step 4: Activating environment..."
conda activate olmoearth
PYTHON_VERSION=$(python --version)
echo -e "${GREEN}✓ Activated: $PYTHON_VERSION${NC}"

# Navigate to project directory
echo ""
echo "Step 5: Installing project dependencies..."
cd "$(dirname "$0")/.."
echo "  Working directory: $(pwd)"

# Upgrade pip
echo "  Upgrading pip..."
pip install --upgrade pip --quiet

# Install project
echo "  Installing olmoearth_projects (this may take 5-10 minutes)..."
echo "  Please be patient while PyTorch and other large packages download..."
pip install -e . --upgrade

echo -e "${GREEN}✓ Project installed${NC}"

# Install common missing dependencies explicitly
echo "  Installing additional dependencies..."
pip install python-dotenv jsonargparse --quiet
echo -e "${GREEN}✓ Additional dependencies installed${NC}"

# Install visualization dependencies
echo ""
echo "Step 6: Installing visualization dependencies..."
pip install matplotlib-scalebar tabulate --quiet
echo -e "${GREEN}✓ Visualization packages installed${NC}"

# Verify installation
echo ""
echo "Step 7: Verifying installation..."

# Test PyTorch
if python -c "import torch; print(f'PyTorch {torch.__version__}')" 2>/dev/null; then
    echo -e "${GREEN}  ✓ PyTorch$(NC}"
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
echo "Step 8: Checking for GPU..."
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
echo "     ${GREEN}python -m olmoearth_projects.main olmoearth_run olmoearth_run \\${NC}"
echo "       --config_path conus_solar_tracking/configs/test/ \\"
echo "       --checkpoint_path gs://...ckpt \\"
echo "       --scratch_path conus_solar_tracking/scratch/test/"
echo ""
echo "  3. Generate visualizations:"
echo "     ${GREEN}python conus_solar_tracking/scripts/run_phoenix_visualizations.py${NC}"
echo ""
echo "Documentation:"
echo "  - Setup guide: conus_solar_tracking/SETUP_CONDA.md"
echo "  - Quick start: conus_solar_tracking/QUICK_START.md"
echo "  - Full docs: conus_solar_tracking/README.md"
echo ""
echo "======================================================================="
