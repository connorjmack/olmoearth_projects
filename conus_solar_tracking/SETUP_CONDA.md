# Step-by-Step: Conda Environment Setup

## Complete Setup and Test Run Guide

Follow these steps exactly to set up the environment and run the Phoenix test.

---

## Step 1: Install Conda (if needed)

### Check if conda is installed:
```bash
conda --version
```

### If NOT installed, install Miniconda:
```bash
# Download and install Miniconda for macOS (ARM/M1/M2/M3)
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
bash Miniconda3-latest-MacOSX-arm64.sh

# Follow prompts, then restart terminal or run:
source ~/.bash_profile  # or ~/.zshrc
```

---

## Step 2: Create Conda Environment with Python 3.11

```bash
# Navigate to project directory
cd /Users/cjmack/Documents/GitHub/olmoearth_projects

# Create new environment named 'olmoearth' with Python 3.11
conda create -n olmoearth python=3.11 -y

# Activate the environment
conda activate olmoearth

# Verify Python version (should show 3.11.x)
python --version
```

**Expected output**: `Python 3.11.x`

---

## Step 3: Install Core Dependencies

```bash
# Make sure you're in the project root and environment is activated
cd /Users/cjmack/Documents/GitHub/olmoearth_projects
conda activate olmoearth

# Install pip and upgrade it
conda install pip -y
pip install --upgrade pip

# Install the project in editable mode
# This reads pyproject.toml and installs all dependencies
pip install -e .
```

**This will take 5-10 minutes** as it downloads and installs:
- PyTorch 2.7.1
- rslearn
- olmoearth-runner
- olmoearth_pretrain
- All other dependencies

---

## Step 4: Install Visualization Dependencies

```bash
# Still in the same environment
pip install matplotlib-scalebar tabulate
```

---

## Step 5: Verify Installation

```bash
# Test imports
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import rslearn; print('rslearn: OK')"
python -c "import olmoearth_pretrain; print('olmoearth_pretrain: OK')"
python -c "import matplotlib; print('matplotlib: OK')"
```

**Expected output**: No errors, shows version numbers

---

## Step 6: Run Phoenix Test

Now you're ready to run the test!

```bash
# Make sure you're in project root with environment activated
cd /Users/cjmack/Documents/GitHub/olmoearth_projects
conda activate olmoearth

# Run Phoenix test inference (~10-15 minutes)
python -m olmoearth_projects.main olmoearth_run olmoearth_run \
  --config_path conus_solar_tracking/configs/test/ \
  --checkpoint_path gs://ai2-rslearn-projects-data/projects/2025_11_05_satlas_solar_farm/2025_11_05_model_update/epoch=9999-step=99999.ckpt \
  --scratch_path conus_solar_tracking/scratch/test/
```

**What happens during the test**:
1. ✓ Checkpoint downloads (~2-5 min, only first time)
2. ✓ Satellite imagery downloads for Phoenix (~2-5 min)
3. ✓ Model inference runs (~5-10 min)
4. ✓ GeoTIFF saved to `scratch/test/results/results_raster/`

**You'll see output like**:
```
Downloading checkpoint...
Building dataset...
Running inference...
Processing partition 1/8...
Processing partition 2/8...
...
✓ Complete!
```

---

## Step 7: Generate Visualizations

After the test completes successfully:

```bash
# Generate all publication-quality figures
python conus_solar_tracking/scripts/run_phoenix_visualizations.py
```

**This creates**:
- `test_results/figures/*_map.png` - Binary detection map
- `test_results/figures/*_map.pdf` - PDF version
- `test_results/figures/*_heatmap.png` - Probability heat map
- `test_results/figures/*_overview.png` - Multi-panel overview
- `test_results/figures/*_overview.pdf` - PDF version
- `test_results/TEST_RESULTS_SUMMARY.md` - Full report

---

## Step 8: View Results

```bash
# View the summary report
cat conus_solar_tracking/test_results/TEST_RESULTS_SUMMARY.md

# Open figures folder
open conus_solar_tracking/test_results/figures/

# Or view specific figure
open conus_solar_tracking/test_results/figures/*_overview.png
```

---

## Quick Reference: Daily Usage

**Every time you want to work on this project**:

```bash
# Navigate to project
cd /Users/cjmack/Documents/GitHub/olmoearth_projects

# Activate environment
conda activate olmoearth

# Now you can run any scripts
python conus_solar_tracking/scripts/run_all_years.py
```

**To deactivate when done**:
```bash
conda deactivate
```

---

## Troubleshooting

### Problem: "conda: command not found"

**Solution**: Conda not installed or not in PATH
```bash
# Add conda to PATH (if installed but not found)
export PATH="$HOME/miniconda3/bin:$PATH"

# Or reinstall Miniconda
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
bash Miniconda3-latest-MacOSX-arm64.sh
```

### Problem: "No module named 'torch'"

**Solution**: PyTorch not installed
```bash
conda activate olmoearth
pip install torch torchvision torchaudio
```

### Problem: "ModuleNotFoundError: No module named 'dotenv'"

**Solution**: Dependencies not installed
```bash
conda activate olmoearth
pip install -e .
```

### Problem: GPU out of memory

**Solution**: Reduce batch size
```bash
# Edit this file
nano conus_solar_tracking/configs/test/model.yaml

# Find line with batch_size: 8
# Change to batch_size: 4 (or 2)
```

### Problem: Checkpoint download fails

**Solution**: Use gsutil to pre-download
```bash
# Install gsutil
pip install gsutil

# Create checkpoint directory
mkdir -p conus_solar_tracking/checkpoints

# Download checkpoint
gsutil cp gs://ai2-rslearn-projects-data/projects/2025_11_05_satlas_solar_farm/2025_11_05_model_update/epoch=9999-step=99999.ckpt \
  conus_solar_tracking/checkpoints/solar_farm.ckpt

# Then use local checkpoint in command:
--checkpoint_path conus_solar_tracking/checkpoints/solar_farm.ckpt
```

### Problem: "No GeoTIFF files found"

**Solution**: Inference may have failed or still running
```bash
# Check if test completed
ls -lh conus_solar_tracking/scratch/test/results/results_raster/

# Check logs for errors
ls -lh conus_solar_tracking/scratch/test/logs/
```

---

## Environment Management

### Delete and recreate environment:
```bash
conda deactivate
conda env remove -n olmoearth
conda create -n olmoearth python=3.13 -y
conda activate olmoearth
cd /Users/cjmack/Documents/GitHub/olmoearth_projects
pip install -e .
```

### List all conda environments:
```bash
conda env list
```

### Export environment (for reproducibility):
```bash
conda activate olmoearth
conda env export > environment.yml
```

---

## Hardware Requirements

**Minimum**:
- GPU: 8GB VRAM (NVIDIA GPU required)
- RAM: 16GB
- Storage: 50GB free

**Recommended**:
- GPU: 16GB VRAM
- RAM: 32GB+
- Storage: 100GB free

**Note**: This requires an NVIDIA GPU with CUDA support. If you don't have a GPU:
- Use Google Colab (free GPU)
- Use cloud instances (AWS p3.2xlarge, GCP with T4/V100)
- Contact me for CPU-only alternatives (much slower)

---

## Next Steps After Successful Test

Once Phoenix test works:

1. **Review test results** in `test_results/`
2. **Run full CONUS** for all years (2017-2025):
   ```bash
   python conus_solar_tracking/scripts/run_all_years.py
   ```
3. **Analyze changes**:
   ```bash
   python conus_solar_tracking/scripts/analyze_changes.py
   ```
4. **Create trend visualizations**:
   ```bash
   python conus_solar_tracking/scripts/visualize_trends.py
   ```

---

## Summary Checklist

- [ ] Conda installed
- [ ] Environment created (`conda create -n olmoearth python=3.11`)
- [ ] Environment activated (`conda activate olmoearth`)
- [ ] Dependencies installed (`pip install -e .`)
- [ ] Visualization packages installed
- [ ] Phoenix test run (10-15 min)
- [ ] Visualizations generated (30 sec)
- [ ] Results viewed

**Total time**: ~30-40 minutes (including downloads and inference)

---

**You're ready to go!** Start with Step 1 above. 🚀
