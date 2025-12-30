# CONUS Solar Farm Deployment Tracking (2017-2025)

Track solar farm deployment across the continental United States using AI-powered satellite imagery analysis. This project uses the pre-trained OlmoEarth solar farm detection model to generate annual snapshots from 2017-2025 and analyze deployment trends over time.

## Overview

- **Model**: Pre-trained solar farm detection (satlas_solar_farm)
- **Coverage**: Continental United States (CONUS)
- **Time Period**: 2017-2025 (9 annual snapshots)
- **Satellite Data**: Sentinel-2 L2A (10m resolution, summer months)
- **Output**: GeoTIFF rasters + change detection analysis + trend visualizations

## Project Structure

```
conus_solar_tracking/
├── configs/          # Year-specific configuration files (2017-2025)
│   ├── 2017/
│   │   ├── dataset.json
│   │   ├── model.yaml
│   │   ├── olmoearth_run.yaml
│   │   └── prediction_request_geometry.geojson
│   ├── 2018/
│   └── ...
├── geometries/       # CONUS bounding box GeoJSON files
├── scripts/          # Automation and analysis scripts
│   ├── create_conus_geometry.py
│   ├── setup_year_configs.sh
│   ├── run_all_years.py
│   ├── analyze_changes.py
│   └── visualize_trends.py
├── scratch/          # Temporary processing data (can be deleted after)
├── results/          # Final GeoTIFF outputs (one per year)
└── analysis/         # Change detection results and visualizations
```

## Quick Start

### 1. Setup (Already Complete!)

The project structure and configurations are already set up:

```bash
# Directory structure created ✓
# Geometry files generated ✓
# Year-specific configs created ✓
# Grid size optimized for CONUS scale ✓
```

### 2. Run Inference (GPU Required)

**Option A: Run all years sequentially**
```bash
cd /Users/cjmack/Documents/GitHub/olmoearth_projects
source .venv/bin/activate  # Activate uv environment

python3 conus_solar_tracking/scripts/run_all_years.py
```

**Option B: Run specific year**
```bash
python3 conus_solar_tracking/scripts/run_all_years.py 2024
```

**Option C: Run single year directly**
```bash
python -m olmoearth_projects.main olmoearth_run olmoearth_run \
  --config_path conus_solar_tracking/configs/2024/ \
  --checkpoint_path gs://ai2-rslearn-projects-data/.../epoch=9999-step=99999.ckpt \
  --scratch_path conus_solar_tracking/scratch/2024/
```

**Estimated Runtime (Single GPU):**
- Per year: 6-12 hours
- All 9 years: 2-4 days (can run overnight)

### 3. Analyze Changes

After inference completes for all years:

```bash
python3 conus_solar_tracking/scripts/analyze_changes.py
```

**Outputs:**
- `analysis/solar_growth_summary.csv` - Year-over-year statistics
- `analysis/changes_YYYY_to_YYYY.tif` - Change detection rasters (8 files)

### 4. Generate Visualizations

```bash
python3 conus_solar_tracking/scripts/visualize_trends.py
```

**Outputs:**
- `analysis/deployment_trends.png` (and .pdf) - Cumulative area + annual growth
- `analysis/growth_rates.png` - Year-over-year growth rate chart
- `analysis/summary_table.md` - Formatted summary table

## Configuration Details

### Spatial Coverage

**CONUS Bounding Box:**
- West: -125.0°, East: -66.0°
- South: 24.0°, North: 49.5°

**Partitioning:**
- Grid size: 2.0 degrees (~222 km)
- Total partitions: ~750
- Enables efficient processing and failure recovery

### Temporal Configuration

**Time Windows (per year):**
- Start: June 1
- End: September 1
- Duration: 3 months (summer)
- Rationale: Maximum clear sky conditions, consistent sun angles

**Satellite Imagery:**
- Source: Sentinel-2 L2A (Microsoft Planetary Computer)
- Bands: All 12 bands (B01-B12)
- Timesteps: 4 (30-day mosaics)
- Resolution: 10m

### Model Configuration

**Architecture:**
- Encoder: OlmoEarth V1 Base (90M parameters)
- Decoder: UNet (multi-scale features)
- Task: Binary segmentation (solar farm / background)
- Window size: 128×128 pixels at 10m = 1.28 km × 1.28 km

**Performance (from Satlas model):**
- Precision: 0.85-0.95
- Recall: 0.75-0.90
- F1 Score: 0.80-0.92

## Hardware Requirements

### Minimum

- GPU: 8GB VRAM (reduce batch_size to 4 in model.yaml)
- RAM: 32GB
- Storage: 500GB SSD
- Timeline: 3-5 days for all years

### Recommended

- GPU: 16GB VRAM (RTX 4080, A100, etc.)
- RAM: 64GB
- Storage: 1TB NVMe SSD
- Timeline: 2-3 days for all years

### Optimal (Multi-GPU or Cloud)

- GPUs: 4-8× 16GB VRAM
- RAM: 128-256GB
- Storage: 2TB NVMe SSD
- Timeline: <1 day for all years

## Storage Requirements

| Component | Size per Year | Total (9 years) |
|-----------|---------------|-----------------|
| Input imagery (cached) | 50-100 GB | 450-900 GB |
| Scratch data (temp) | 100-200 GB | Can delete after each year |
| Final GeoTIFF | 5-10 GB | 45-90 GB |
| Analysis outputs | - | 10-20 GB |

**Total needed:** ~500 GB working space, ~100 GB for final outputs

## Troubleshooting

### GPU Memory Issues

If you encounter OOM (Out of Memory) errors:

1. Reduce batch size in `configs/YYYY/model.yaml`:
   ```yaml
   data:
     init_args:
       batch_size: 4  # Reduce from 8 to 4 (or 2)
   ```

2. Close other GPU applications

### Checkpoint Download Fails

The checkpoint auto-downloads from GCS. If it fails:

```bash
# Pre-download checkpoint manually
mkdir -p checkpoints
gsutil cp gs://ai2-rslearn-projects-data/.../epoch=9999-step=99999.ckpt \
  checkpoints/solar_farm.ckpt

# Then modify run_all_years.py to use local path
```

### Partition Failures

If a partition fails during processing:

1. Check logs in scratch/YYYY/
2. The pipeline supports stage-based recovery
3. Re-run the same year - it will resume from last successful stage

### Missing Results

If results aren't appearing:

1. Check `scratch/YYYY/results/results_raster/` - results are here first
2. The script copies them to `results/YYYY/`
3. Verify GeoTIFF files exist: `ls -lh results/*/`

## Next Steps

### Validation

Compare results against ground truth data:

1. **EIA Form 860** - Utility-scale solar farms
   - https://www.eia.gov/electricity/data/eia860/

2. **USGS Solar Development** - Federal land installations

3. **Visual inspection** in QGIS:
   ```bash
   # Load GeoTIFF layers for multiple years
   # Compare with Google Earth imagery
   # Verify known solar farm locations
   ```

### Extensions

**Quarterly snapshots:** Modify geometry dates to Q1, Q2, Q3, Q4

**State-level analysis:** Use state boundaries instead of CONUS-wide

**Rooftop solar:** Train custom model for smaller installations (requires training data)

**Other regions:** Modify bounding box for different countries/regions

## Citation

If you use this project or the OlmoEarth model, please cite:

```
OlmoEarth Projects
Allen Institute for AI (Ai2)
https://github.com/allenai/olmoearth_projects
```

## License

Follows the OlmoEarth Artifact License from the parent repository.

## Support

For issues with:
- **This project**: Open issue on GitHub or contact project maintainer
- **OlmoEarth model**: See https://github.com/allenai/olmoearth_projects
- **rslearn framework**: See rslearn documentation

---

**Status:** ✓ Setup Complete - Ready for inference

**Last Updated:** December 29, 2024
