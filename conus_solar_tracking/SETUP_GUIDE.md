# Setup Guide - Choose Your Method

You have two options for setting up the environment. **We recommend using `uv`** (Option 1) since it's officially supported by the repository.

---

## Option 1: uv (Recommended - Official Method)

`uv` is what the OlmoEarth developers use and test with. It's faster and has better dependency resolution.

### Quick Setup

```bash
cd /Users/cjmack/Documents/GitHub/olmoearth_projects
bash conus_solar_tracking/setup_uv.sh
```

**What happens:**
- Installs `uv` if needed
- Creates `.venv` with Python 3.11 (downloads if needed)
- Installs all dependencies via `uv sync`
- Verifies everything works

**Time:** ~5-10 minutes

### Daily Usage

```bash
# Activate environment
source .venv/bin/activate

# Run Phoenix test
bash conus_solar_tracking/run_phoenix_test.sh

# Deactivate when done
deactivate
```

---

## Option 2: Conda (Alternative)

If you prefer conda or already have conda installed.

### Quick Setup

```bash
cd /Users/cjmack/Documents/GitHub/olmoearth_projects
bash conus_solar_tracking/setup_conda_clean.sh
```

**What happens:**
- Creates conda environment with Python 3.11
- Installs dependencies via conda + pip
- Verifies everything works

**Time:** ~5-10 minutes

### Daily Usage

```bash
# Activate environment
conda activate olmoearth

# Run Phoenix test
bash conus_solar_tracking/run_phoenix_test.sh

# Deactivate when done
conda deactivate
```

---

## Which Should I Choose?

### Use `uv` if:
- ✅ You want the officially supported method
- ✅ You want faster installs and better dependency resolution
- ✅ You don't have a preference

### Use `conda` if:
- ✅ You already use conda for other projects
- ✅ You prefer conda's environment management
- ✅ You have conda installed and configured

**Both work fine!** The test scripts work with either environment.

---

## After Setup - Run Phoenix Test

No matter which option you choose, run the Phoenix test the same way:

```bash
# For uv
source .venv/bin/activate
bash conus_solar_tracking/run_phoenix_test.sh

# For conda
conda activate olmoearth
bash conus_solar_tracking/run_phoenix_test.sh
```

**Expected runtime:** 10-15 minutes

**Outputs:**
- GeoTIFF: `conus_solar_tracking/scratch/test/results/results_raster/*.tif`
- Figures: `conus_solar_tracking/test_results/figures/`
- Report: `conus_solar_tracking/test_results/TEST_RESULTS_SUMMARY.md`

---

## Troubleshooting

### uv: "No Python 3.11 found"
The setup script automatically downloads Python 3.11 via uv. If this fails:
```bash
# Install Python 3.11 manually first
brew install python@3.11
# Then run setup again
bash conus_solar_tracking/setup_uv.sh
```

### Conda: "conda: command not found"
Install Miniconda first:
```bash
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
bash Miniconda3-latest-MacOSX-arm64.sh
# Restart terminal, then run setup
bash conus_solar_tracking/setup_conda_clean.sh
```

### "ModuleNotFoundError" when running test
Ensure environment is activated:
```bash
# Check if activated
which python  # Should show .venv/bin/python or miniconda3/envs/olmoearth/bin/python

# If not activated, activate first
source .venv/bin/activate  # for uv
# OR
conda activate olmoearth   # for conda
```

---

## Clean Start

### Remove uv environment
```bash
cd /Users/cjmack/Documents/GitHub/olmoearth_projects
rm -rf .venv
bash conus_solar_tracking/setup_uv.sh
```

### Remove conda environment
```bash
conda deactivate
conda env remove -n olmoearth -y
bash conus_solar_tracking/setup_conda_clean.sh
```

---

## Next Steps

1. ✅ Choose setup method (uv recommended)
2. ✅ Run setup script (~10 minutes)
3. ✅ Run Phoenix test (~15 minutes)
4. ✅ View results
5. ✅ Run full CONUS if satisfied

**Total time to first results:** ~25 minutes
