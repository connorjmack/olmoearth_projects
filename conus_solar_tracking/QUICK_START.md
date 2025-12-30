# Quick Start Guide - CONUS Solar Tracking

## What's Been Built

✓ **Complete tracking system** for solar farm deployment across the US (2017-2025)
✓ **9 yearly configurations** ready to run
✓ **Automation scripts** for inference, analysis, and visualization
✓ **Optimized for CONUS scale** with 2° grid partitioning (~750 partitions per year)

## File Overview

```
📁 conus_solar_tracking/
  📁 configs/2017-2025/     ← 9 years of configurations (ready to use)
  📁 geometries/            ← CONUS bounding boxes for each year
  📁 scripts/               ← 5 Python scripts (all ready)
  📁 scratch/               ← Temp data (auto-populated during runs)
  📁 results/               ← Final GeoTIFFs (auto-populated)
  📁 analysis/              ← Change detection outputs (auto-populated)
  📄 README.md              ← Full documentation
  📄 QUICK_START.md         ← This file
```

## Run Instructions

### Step 1: Activate Environment

```bash
cd /Users/cjmack/Documents/GitHub/olmoearth_projects
source .venv/bin/activate
```

### Step 2: Test Run (RECOMMENDED - Start Here!)

Before running the full CONUS, test on a smaller region first:

Create a test configuration for Phoenix, AZ (high solar density):

```bash
# Create test geometry file (Phoenix metro area)
cat > conus_solar_tracking/geometries/phoenix_test_2024.geojson << 'EOF'
{
  "type": "FeatureCollection",
  "features": [{
    "type": "Feature",
    "geometry": {
      "type": "Polygon",
      "coordinates": [[
        [-113.0, 32.5], [-113.0, 34.0],
        [-111.0, 34.0], [-111.0, 32.5], [-113.0, 32.5]
      ]]
    },
    "properties": {
      "oe_start_time": "2024-06-01T00:00:00Z",
      "oe_end_time": "2024-09-01T00:00:00Z"
    }
  }]
}
EOF

# Create test config directory
mkdir -p conus_solar_tracking/configs/test
cp conus_solar_tracking/configs/2024/* conus_solar_tracking/configs/test/
cp conus_solar_tracking/geometries/phoenix_test_2024.geojson \
   conus_solar_tracking/configs/test/prediction_request_geometry.geojson

# Run test (should take ~5-15 minutes)
python -m olmoearth_projects.main olmoearth_run olmoearth_run \
  --config_path conus_solar_tracking/configs/test/ \
  --checkpoint_path gs://ai2-rslearn-projects-data/projects/2025_11_05_satlas_solar_farm/2025_11_05_model_update/epoch=9999-step=99999.ckpt \
  --scratch_path conus_solar_tracking/scratch/test/

# Check results
ls -lh conus_solar_tracking/scratch/test/results/results_raster/
```

### Step 3: Run Full CONUS (All 9 Years)

**Option A: Run all years automatically (recommended)**
```bash
python3 conus_solar_tracking/scripts/run_all_years.py
```

**Option B: Run one year at a time**
```bash
# Run just 2024
python3 conus_solar_tracking/scripts/run_all_years.py 2024

# Run just 2023
python3 conus_solar_tracking/scripts/run_all_years.py 2023
```

**Expected Timeline:**
- Per year: 6-12 hours (single GPU)
- All 9 years: 2-4 days (can run overnight)

### Step 4: Analyze Changes

After all years complete:

```bash
python3 conus_solar_tracking/scripts/analyze_changes.py
```

**Outputs:**
- `analysis/solar_growth_summary.csv`
- `analysis/changes_2017_to_2018.tif` (and 7 more)

### Step 5: Create Visualizations

```bash
python3 conus_solar_tracking/scripts/visualize_trends.py
```

**Outputs:**
- `analysis/deployment_trends.png` + .pdf
- `analysis/growth_rates.png`
- `analysis/summary_table.md`

## Monitoring Progress

### Check What's Running
```bash
# Watch GPU usage
nvidia-smi -l 1

# Monitor disk space
df -h conus_solar_tracking/scratch/

# Check logs
tail -f conus_solar_tracking/scratch/2024/logs/*.log
```

### Check Results
```bash
# List completed years
ls -lh conus_solar_tracking/results/

# Count GeoTIFF files
find conus_solar_tracking/results/ -name "*.tif" | wc -l
# Should be 9 (one per year)
```

## Troubleshooting

### GPU Out of Memory?

Edit `conus_solar_tracking/configs/YYYY/model.yaml`:

```yaml
data:
  init_args:
    batch_size: 4  # Reduce from 8 to 4 (or even 2)
```

### Checkpoint Download Slow?

The checkpoint (~1-2GB) auto-downloads on first run. It's cached to `/tmp/rslearn_cache/`.

### Year Failed Mid-Run?

The pipeline supports recovery. Just re-run the same year:

```bash
python3 conus_solar_tracking/scripts/run_all_years.py 2024
```

It will resume from the last successful stage.

## Expected Outputs

### Per Year (in results/YYYY/)
- `combined_output.tif` - CONUS-wide solar farm detection
- Resolution: 10m
- CRS: EPSG:3857
- Values: 0-255 (probability of solar farm)

### Analysis Outputs
- Change detection rasters (8 files, one per year-pair)
- Summary CSV with metrics
- Visualization plots (PNG + PDF)

## File Sizes

| Directory | Expected Size |
|-----------|---------------|
| `configs/` | ~1 MB (config files) |
| `geometries/` | ~10 KB (GeoJSON files) |
| `scratch/YYYY/` | 100-200 GB per year (temporary, delete after) |
| `results/YYYY/` | 5-10 GB per year (keep) |
| `analysis/` | 10-20 GB (keep) |

**Total final output:** ~100-150 GB

## What Hardware Do You Have?

### Check Your GPU
```bash
nvidia-smi
```

**If you have:**
- **8GB VRAM**: Reduce batch_size to 4
- **16GB VRAM**: Use default batch_size of 8
- **24GB+ VRAM**: Can increase batch_size to 16 for faster processing

### Recommended Approach by Hardware

**Single GPU (8-16GB):**
- Run years sequentially with `run_all_years.py`
- Let it run overnight for 2-4 days
- Total cost: $0 (if you own hardware)

**Multiple GPUs:**
- Run multiple years in parallel
- Modify `run_all_years.py` to use CUDA_VISIBLE_DEVICES
- Complete in <1 day

**Cloud (AWS/GCP):**
- Use p3.2xlarge instances (~$3/hour)
- Process each year in 6-12 hours
- Total cost: ~$150-400 for all years

## Ready to Start!

**Recommended path:**
1. ✅ Run Phoenix test (15 min) ← Start here!
2. ✅ Verify test output looks good
3. ✅ Run full CONUS for one year (2024) to validate
4. ✅ Run all remaining years
5. ✅ Analyze and visualize

**Current status:** All scripts ready, configurations optimized ✓

---

Last updated: December 29, 2024
