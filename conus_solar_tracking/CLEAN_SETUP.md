# Clean Conda Setup Guide

## Problem

The previous setup using `pip install -e .` had dependency resolution issues, causing missing modules like `olmoearth_run`, `jsonargparse`, etc.

## Solution

Use a proper conda `environment.yml` file that:
- Installs core packages (PyTorch, NumPy, GeoPandas) via conda-forge
- Installs specialized packages via pip
- Properly handles git dependencies

---

## Steps to Clean Setup

### 1. Remove Old Environment

```bash
conda deactivate
conda env remove -n olmoearth
```

### 2. Run Clean Setup Script

```bash
cd /Users/cjmack/Documents/GitHub/olmoearth_projects
bash conus_solar_tracking/setup_conda_clean.sh
```

**What this does:**
- Creates environment from `environment.yml`
- Installs all dependencies in correct order
- Verifies everything works
- Takes ~5-10 minutes

### 3. Activate and Test

```bash
conda activate olmoearth
bash conus_solar_tracking/run_phoenix_test.sh
```

---

## What Changed?

### Old Approach (Broken)
```bash
conda create -n olmoearth python=3.13
pip install -e .  # ← This had dependency issues
```

### New Approach (Clean)
```bash
conda env create -f environment.yml  # ← Handles everything properly
pip install -e .  # ← Only installs the project itself
```

---

## Files Created

1. **`environment.yml`** - Complete conda environment specification
   - Python 3.11 (required by olmoearth_pretrain)
   - PyTorch (from conda)
   - All scientific packages (from conda-forge)
   - olmoearth packages (from pip/git)

2. **`setup_conda_clean.sh`** - Automated setup using environment.yml
   - Removes old environment if exists
   - Creates new environment
   - Verifies all imports work

---

## Troubleshooting

### If setup fails with network errors
```bash
# Retry with verbose output
conda env create -f conus_solar_tracking/environment.yml --verbose
```

### If specific package fails to install
Edit `environment.yml` and comment out the failing package, then install manually:
```bash
conda activate olmoearth
pip install <package-name>
```

### If you want to start completely fresh
```bash
conda deactivate
conda env remove -n olmoearth
rm -rf ~/.conda/envs/olmoearth
bash conus_solar_tracking/setup_conda_clean.sh
```

---

## Quick Reference

**Create environment:**
```bash
bash conus_solar_tracking/setup_conda_clean.sh
```

**Activate environment:**
```bash
conda activate olmoearth
```

**Run Phoenix test:**
```bash
bash conus_solar_tracking/run_phoenix_test.sh
```

**Deactivate when done:**
```bash
conda deactivate
```

---

## Why This is Better

✅ **Reproducible** - Same environment every time
✅ **Complete** - All dependencies resolved correctly
✅ **Fast** - Conda binaries are pre-compiled
✅ **Reliable** - No dependency resolution conflicts

The previous approach using just `pip install -e .` failed because:
- Complex dependency chains (rslearn → olmoearth-runner → many subdeps)
- Git dependencies not handled by pip alone
- Missing transitive dependencies

This new approach uses conda to manage the base environment, then pip only for packages not available on conda-forge.
