# Gemini Project Context: OlmoEarth Projects

This directory contains a collection of geospatial AI projects built on the OlmoEarth foundation model and the `rslearn` framework. The primary active project is tracking solar farm deployment across the Continental United States (CONUS) from 2017 to 2025.

## Project Overview

*   **Core Task**: Satellite imagery analysis (segmentation) using the OlmoEarth V1 Base model.
*   **Key Project**: `conus_solar_tracking` - Annual snapshots of solar farms across the US.
*   **Main Technologies**: 
    *   **Python**: Primary programming language.
    *   **rslearn**: Remote sensing machine learning framework.
    *   **OlmoEarth**: Foundation model for Earth observation.
    *   **PyTorch Lightning**: Training and inference orchestration.
    *   **uv**: Dependency and environment management.
    *   **Satellite Data**: Sentinel-2 L2A (via Microsoft Planetary Computer).

## Project Structure

*   `olmoearth_projects/`: Core Python package.
    *   `main.py`: Entry point for running workflows.
    *   `olmoearth_run/`: Generic runners for inference and finetuning.
*   `conus_solar_tracking/`: Sub-project for US solar farm tracking.
    *   `configs/`: Year-specific configurations (2017-2025).
    *   `scripts/`: Automation for running inference and analysis.
    *   `results/`: Final output rasters (GeoTIFFs).
*   `olmoearth_run_data/`: Configuration templates for various tasks (mangrove, forest loss, etc.).
*   `pyproject.toml` & `uv.lock`: Dependency definitions.

## Getting Started & Workflows

### 1. Environment Setup
The project uses `uv` for lightning-fast dependency management.
```bash
uv sync
source .venv/bin/activate
```

### 2. Running the CONUS Solar Tracking
This is the main workflow. It requires a GPU with at least 8GB VRAM (16GB+ recommended).

**Run all years (2017-2025):**
```bash
python3 conus_solar_tracking/scripts/run_all_years.py
```

**Run a specific year:**
```bash
python3 conus_solar_tracking/scripts/run_all_years.py 2024
```

### 3. Analysis and Visualization
After inference is complete, generate trends and statistics:
```bash
# Analyze year-over-year changes
python3 conus_solar_tracking/scripts/analyze_changes.py

# Generate trend charts and summaries
python3 conus_solar_tracking/scripts/visualize_trends.py
```

### 4. Running Custom Workflows
Use the main entry point to run specific project workflows:
```bash
python -m olmoearth_projects.main <project_name> <workflow_name> [args...]
```
Example for `olmoearth_run`:
```bash
python -m olmoearth_projects.main olmoearth_run olmoearth_run \
  --config_path conus_solar_tracking/configs/2024/ \
  --checkpoint_path <path_to_ckpt> \
  --scratch_path <path_to_scratch>
```

## Development Conventions

*   **Configuration**: Heavy use of YAML (`model.yaml`, `olmoearth_run.yaml`) and JSON (`dataset.json`) for pipeline definitions.
*   **Logging**: Centralized logger in `olmoearth_projects.utils.logging`.
*   **Data Handling**: Uses `fsspec` and `upath` for cloud-agnostic file paths (local, GCS, etc.).
*   **Parallelism**: Uses `jsonargparse` for CLI and custom multiprocessing utils in `olmoearth_projects.utils.mp`.

## Key Files
*   `pyproject.toml`: Project metadata and dependencies.
*   `conus_solar_tracking/README.md`: Detailed guide for the solar tracking sub-project.
*   `olmoearth_projects/main.py`: The primary CLI entry point.
*   `config.yaml`: Root configuration for PyTorch Lightning trainer and model.
