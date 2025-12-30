# Phoenix Test Run Guide

## Environment Issue Detected

Your system has Python 3.14.2, but PyTorch 2.7.1 (required by this project) only supports Python 3.11-3.13.

## Quick Fix Options

### Option 1: Install Python 3.13 (Recommended)

```bash
# Install Python 3.13 via Homebrew
brew install python@3.13

# Setup uv with Python 3.13
export PATH="$HOME/.local/bin:$PATH"
uv venv --python python3.13
uv sync
```

### Option 2: Use Conda/Miniconda

```bash
# Install miniconda if you don't have it
brew install miniconda

# Create environment with Python 3.13
conda create -n olmoearth python=3.13
conda activate olmoearth

# Install dependencies
pip install -e .
```

### Option 3: Use pyenv

```bash
# Install pyenv
brew install pyenv

# Install Python 3.13
pyenv install 3.13.1
pyenv local 3.13.1

# Setup environment
export PATH="$HOME/.local/bin:$PATH"
uv venv --python python3.13
uv sync
```

## After Environment Setup

Once you have Python 3.11-3.13 installed and the environment set up:

### 1. Run Phoenix Test

```bash
cd /Users/cjmack/Documents/GitHub/olmoearth_projects
source .venv/bin/activate  # or: conda activate olmoearth

# Run test inference (takes ~5-15 minutes with GPU)
python -m olmoearth_projects.main olmoearth_run olmoearth_run \
  --config_path conus_solar_tracking/configs/test/ \
  --checkpoint_path gs://ai2-rslearn-projects-data/projects/2025_11_05_satlas_solar_farm/2025_11_05_model_update/epoch=9999-step=99999.ckpt \
  --scratch_path conus_solar_tracking/scratch/test/
```

### 2. Generate Visualizations

After the test completes, run the automated visualization script:

```bash
python3 conus_solar_tracking/scripts/run_phoenix_visualizations.py
```

This will:
- Find the test GeoTIFF output
- Generate publication-quality maps
- Create multi-panel overview figures
- Save everything to `conus_solar_tracking/test_results/`

## Manual Visualization

If you prefer to run visualizations manually:

```bash
# Find your test GeoTIFF
GEOTIFF=$(find conus_solar_tracking/scratch/test/results/results_raster/ -name "*.tif" | head -1)

# Create single map visualization
python3 conus_solar_tracking/scripts/visualize_geotiff.py "$GEOTIFF" \
  --output-dir conus_solar_tracking/test_results/figures \
  --title "Phoenix AZ Solar Farms - 2024" \
  --dpi 300
```

## Expected Test Results

**Region**: Phoenix metro area (approximately 2° x 1.5° = ~222km x 167km)

**Output Files**:
```
conus_solar_tracking/
├── scratch/test/results/results_raster/
│   └── combined_output.tif  (or similar)
└── test_results/
    └── figures/
        ├── *_map.png            (binary detection map)
        ├── *_map.pdf            (publication quality)
        ├── *_heatmap.png        (probability heat map)
        ├── *_overview.png       (multi-panel figure)
        └── *_overview.pdf       (publication quality)
```

**Expected Runtime**:
- Checkpoint download: ~2-5 minutes (first time only)
- Satellite data download: ~2-5 minutes
- Inference: ~5-10 minutes
- Visualization: ~30 seconds

**Total**: ~10-20 minutes

## Troubleshooting

### GPU Out of Memory

Edit `conus_solar_tracking/configs/test/model.yaml`:
```yaml
data:
  init_args:
    batch_size: 4  # Reduce from 8
```

### No GPU Available

The model requires a GPU. Options:
1. Use Google Colab (free GPU)
2. Use AWS/GCP with GPU instance
3. Ask about CPU-only inference (much slower)

### Checkpoint Download Fails

```bash
# Pre-download using gsutil
gsutil cp gs://ai2-rslearn-projects-data/projects/2025_11_05_satlas_solar_farm/2025_11_05_model_update/epoch=9999-step=99999.ckpt \
  conus_solar_tracking/checkpoints/solar_farm.ckpt

# Then modify the command to use local path:
--checkpoint_path conus_solar_tracking/checkpoints/solar_farm.ckpt
```

## What's Already Ready

✅ Phoenix test geometry created
✅ Test configuration set up
✅ Visualization scripts created
✅ Test results folder structure created
✅ Automated runner script created

You just need to:
1. Fix Python version (3.11-3.13)
2. Run `uv sync`
3. Run the test
4. Run visualizations

## Need Help?

Check the main README: `conus_solar_tracking/README.md`
Or the quick start: `conus_solar_tracking/QUICK_START.md`
