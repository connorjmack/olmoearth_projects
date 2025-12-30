# 🚀 START HERE - Quick Setup Guide

Get the Phoenix test running in **3 simple steps** (~30 minutes total).

---

## Prerequisites

- **macOS** with Apple Silicon (M1/M2/M3) or Intel
- **NVIDIA GPU** (required for inference) OR access to cloud GPU
- **50GB free disk space**

---

## Quick Start (3 Steps)

### 📋 Step 1: Install Conda (if needed)

Check if you have conda:
```bash
conda --version
```

If not installed:
```bash
# Download and install Miniconda
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
bash Miniconda3-latest-MacOSX-arm64.sh

# Restart terminal after installation
```

### 🔧 Step 2: Run Automated Setup

```bash
cd /Users/cjmack/Documents/GitHub/olmoearth_projects

# Run automated setup (5-10 minutes)
bash conus_solar_tracking/setup_conda_auto.sh
```

This script will:
- ✓ Create conda environment with Python 3.11
- ✓ Install all dependencies (PyTorch, rslearn, etc.)
- ✓ Verify installation
- ✓ Check for GPU

### ▶️ Step 3: Run Phoenix Test

```bash
# Activate environment
conda activate olmoearth

# Run test (10-15 minutes)
bash conus_solar_tracking/run_phoenix_test.sh
```

This will:
- ✓ Run inference on Phoenix region
- ✓ Generate publication-quality visualizations
- ✓ Create summary report

---

## View Results

```bash
# View summary
cat conus_solar_tracking/test_results/TEST_RESULTS_SUMMARY.md

# Open figures
open conus_solar_tracking/test_results/figures/
```

---

## That's It! 🎉

You now have:
- ✅ Working conda environment
- ✅ Solar farm detection for Phoenix
- ✅ Publication-quality maps and figures
- ✅ Complete statistics and reports

---

## Next Steps

### Run Full CONUS Analysis (All 9 Years)

```bash
conda activate olmoearth
python conus_solar_tracking/scripts/run_all_years.py
```

### Analyze Temporal Changes

```bash
python conus_solar_tracking/scripts/analyze_changes.py
python conus_solar_tracking/scripts/visualize_trends.py
```

---

## Troubleshooting

### GPU Issues

If you get GPU out of memory errors:
```bash
# Edit batch size
nano conus_solar_tracking/configs/test/model.yaml
# Change batch_size: 8 to batch_size: 4
```

### Network Issues

If checkpoint download fails:
```bash
# Pre-download checkpoint
pip install gsutil
mkdir -p conus_solar_tracking/checkpoints
gsutil cp gs://ai2-rslearn-projects-data/.../epoch=9999-step=99999.ckpt \
  conus_solar_tracking/checkpoints/solar_farm.ckpt
```

### Environment Issues

If conda environment has problems:
```bash
# Recreate environment
conda deactivate
conda env remove -n olmoearth
bash conus_solar_tracking/setup_conda_auto.sh
```

---

## More Help

- **Detailed setup guide**: `SETUP_CONDA.md`
- **Full documentation**: `README.md`
- **Quick reference**: `QUICK_START.md`

---

## Complete Command Reference

```bash
# Setup (one time)
bash conus_solar_tracking/setup_conda_auto.sh

# Daily usage
conda activate olmoearth
bash conus_solar_tracking/run_phoenix_test.sh

# View results
open conus_solar_tracking/test_results/figures/

# Run full CONUS
python conus_solar_tracking/scripts/run_all_years.py

# Deactivate when done
conda deactivate
```

---

**Estimated Time**:
- Setup: 10 minutes
- Phoenix test: 15 minutes
- **Total: 25 minutes to results**

**Ready? Start with Step 1!** 👆
