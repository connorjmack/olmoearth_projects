# Finetuning OlmoEarth on a classification task - Example

| # | Section |
| - | - |
| 0 | [Setup](#1-setup) |
| 1 | [Setup](#1-setup) |
| 2 | [Gathering and prepping the dataset](#2-Gathering-and-prepping-the-dataset) |
| 3 | [Benchmarking the base model](#3-benchmarking-the-base-model) |
| 4 | [Defining your ...](#4-defining-your-) |
| 5 | [Training](#5-training) |
| 6 | [Using your fine-tuned model](#6-using-your-fine-tuned-model) |


## 0. Goal
Let's build a burned area detection model using OlmoEarth. We will finetune the base model on a burned area mapping task and use it to detect fire perimeters on a unseen past fires.


## 1. Setup


## 2. Gathering and prepping the dataset
Letʼs start off by using fire perimeter data from CalFire. These come as polygons associated with a contained date, which will use to determine when our satellite snapshots should be captured (usually within 2 weeks of the contained date).

Let's download the data:
``` shell
curl -L -A "Mozilla/5.0" -e "https://www.fire.ca.gov/" "https://34c031f8-c9fd-4018-8c5a-4159cdff6b0d-cdn-endpoint.azureedge.net/-/media/calfire-website/what-we-do/fire-resource-assessment-program---frap/gis-data/2025/fire241gdb.ashx?rev=51177a999fe84e83a7c03b7d5a66b93b" -o fire241gdb.zip
```

The data comes in the form of burnt polygons, each associated with a containment date and an alarm date.
We will use the rslearn library to process the data. This library makes it convenient to load and store the data in a structured format that can be easily consumed by OlmoEarth model.

### 0a. Data Download, filtering (year >=2020) and label creation
```shell
python3 ./rslp/burn-scar/scripts/calfire-data-prep.py
```
### 0b. point sampling and csv creation
```shell
python3 ./rslp/burn-scar/scripts/calfire-sample-points.py --max_iter 3
```

### 1. Converting input CSV to standardized geojson annotation files
```shell
python ./rslp/burn-scar/scripts/OER_annotation_creation.py /weka/dfive-default/hadriens/datasets/label_data/Calfp_2020-2025_GroundTruthPoints.csv --outdir /weka/dfive-default/rslearn-eai/datasets/burn-scar/oerun --id-col polygon_id
```
"coordinate_mode": "pixel" indicate that the vector on disk (layers/{layer}/data.geojson) have coordinates in pixel units.
Mixed native resolutions (10/20/60 m) are fine — rslearn resamples to the window’s resolution during materialize using resampling_method.
"sort_by" controls ordering of candidate scenes before matching; supported value here is "cloud_cover" (ascending).
Use to prefer lowest‑cloud scenes when building mosaics or selecting first valid.
"use_rtree_index" uses a spatial rtree for fast scene lookup (speeds up prepare a lot on big spatiotemporal extents).

### 2a. labeled window creation
```shell
python -m rslp.main olmoearth_run prepare_labeled_windows     --project_path ./olmoearth_run_data/burn-scar_test     --scratch_path /weka/dfive-default/rslearn-eai/datasets/burn-scar/oerun
```

### 2b.  source data prep
```shell
export DATASET_PATH=/weka/dfive-default/rslearn-eai/datasets/burn-scar/oerun/dataset
export DATASET_GROUP=post_random_split
rslearn dataset prepare --root $DATASET_PATH --group $DATASET_GROUP --workers 32 --retry-max-attempts 8
rslearn dataset ingest --root $DATASET_PATH --group $DATASET_GROUP --workers 32 --retry-max-attempts 8
rslearn dataset materialize --root $DATASET_PATH --group $DATASET_GROUP --workers 64 --retry-max-attempts 8
```
> ---
> **TODO**
> - Expose ***build_dataset_from_windows*** through the rslp cli:
https://github.com/allenai/olmoearth_run/blob/develop/src/olmoearth_run/runner/local/fine_tune_runner.py#L129-L134
https://github.com/allenai/rslearn_projects/blob/master/rslp/olmoearth_run/olmoearth_run.py#L54-L75
> ---

```


## 3. Defining and training the model

First let's download the OlmoEarth pretrained model weights. Depending on the complexity of the task, your finetuning budget, and your GPU memory, you can select:
  - OlmoEarth nano: {X} parameters - {HF link}:
  - OlmoEarth tiny: {X} parameters, - {HF link}:
  - OlmoEarth base: {X} parameters, - {HF link}:
  - OlmoEarth large: {X} parameters, - {HF link}:


Now we need to design our model architecture, training loop and evaluation metrics, and define how the data should be pre-processed and sent to the model.
Behind the scenes, we use Lightning to coordinate and run the fine-tuning job. This allows us to configure every aspect of the job in a single configuration file.

Let's create it:
`burn_scar_model.yaml`:

```yaml
model:
  class_path: rslearn.train.lightning_module.RslearnLightningModule
  init_args:
    # This part defines the model architecture.
    # Essentially we apply the OlmoEarth backbone with a classification head
    model:
      class_path: rslearn.models.multitask.MultiTaskModel
      init_args:
        encoder:
          - class_path: rslp.helios.model.Helios
            init_args:
              checkpoint_path: "{CHECKPOINT_PATH}"
              selector: ["encoder"]
              forward_kwargs:
                patch_size: {PATCH_SIZE}
        decoders:
          burn-scar_classification:
            - class_path: rslearn.models.pooling_decoder.PoolingDecoder
              init_args:
                in_channels: {ENCODER_EMBEDDING_SIZE}
                out_channels: 2
            - class_path: rslearn.train.tasks.classification.ClassificationHead
    lr: 0.0001
    scheduler:
      class_path: rslearn.train.scheduler.PlateauScheduler
      init_args:
        factor: 0.2
        patience: 2
        min_lr: 0
        cooldown: 10
data:
  class_path: rslearn.train.data_module.RslearnDataModule
  init_args:
    # Replace this with the dataset path.
    path: /weka/dfive-default/rslearn-eai/datasets/burn-scar/California/2020-25
    # This defines the layers that should be read for each window.
    # The key ("image" / "targets") is what the data will be called in the model,
    # while the layers option specifies which layers will be read.
    inputs:
      sentinel2_l2a:
        data_type: "raster"
        layers: ["sentinel2_l2a"]
        bands: ["B02", "B03", "B04", "B08", "B05", "B06", "B07", "B8A", "B11", "B12", "B01", "B09"]
        passthrough: true #if false only what the Task returns via process_inputs is sent to the model. If true the raw input (here is the raster) is added to the Task output, which is then accessible for transforms or visualization
        dtype: FLOAT32
      label:
        data_type: "vector"
        layers: ["label"]
        is_target: true
    task:
      class_path: rslearn.train.tasks.multi_task.MultiTask
      init_args:
        tasks:
          burn-scar_classification:
            class_path: rslearn.train.tasks.classification.ClassificationTask
            init_args:
              property_name: "category"
              classes: ["burnt", "unburnt"]
              enable_f1_metric: true
              metric_kwargs:
                average: "micro"
        input_mapping:
          burn-scar_classification:
            label: "targets"
    batch_size: 32
    num_workers: 32
    # These define different options for different phases/splits, like training,
    # validation, and testing.
    # Here we use the same transform across splits except training where we add a
    # flipping augmentation.
    # For now we are using the same windows for training and validation.
    default_config:
      transforms:
        - class_path: rslearn.train.transforms.concatenate.Concatenate
          init_args:
            selections:
              sentinel2_l2a: []
            output_selector: sentinel2_l2a
        - class_path: rslp.helios.norm.HeliosNormalize
          init_args:
            config_fname: "/opt/helios/data/norm_configs/computed.json"
            band_names:
              sentinel2_l2a: ["B02", "B03", "B04", "B08", "B05", "B06", "B07", "B8A", "B11", "B12", "B01", "B09"]
        - class_path: rslearn.train.transforms.pad.Pad
          init_args:
            size: 8
            mode: "center"
            image_selectors: ["sentinel2_l2a"]
    train_config:
      groups: ["groundtruth_polygon_split_window_32"]
      tags:
        split: "train"
    val_config:
      groups: ["groundtruth_polygon_split_window_32"]
      tags:
        split: "val"
    test_config:
      groups: ["groundtruth_polygon_split_window_32"]
      tags:
        split: "val"
trainer:
  max_epochs: 100
  callbacks:
    - class_path: lightning.pytorch.callbacks.LearningRateMonitor
      init_args:
        logging_interval: "epoch"
    - class_path: lightning.pytorch.callbacks.ModelCheckpoint
      init_args:
        save_top_k: 1
        save_last: true
        monitor: val_loss
        mode: min
    - class_path: rslearn.train.callbacks.freeze_unfreeze.FreezeUnfreeze
      init_args:
        module_selector: ["model", "encoder", 0]
        unfreeze_at_epoch: 2
rslp_project: placeholder
rslp_experiment: placeholder
```

Now we can train the model:

### 3.  Finetune model
```shell
export GROUP_PATH=/weka/dfive-default/rslearn-eai/datasets/burn-scar/oerun/dataset/windows/post_random_split
find $GROUP_PATH -maxdepth 2 -name "metadata.json" -exec cat {} \; | grep -oE "train|val|test" | sort | uniq -c | awk 'BEGIN{printf "{"} {printf "%s\"%s\": %d", (NR>1?", ":""), $2, $1} END{print "}"}'
python -m rslp.main olmoearth_run finetune --project_path /weka/dfive-default/yawenz/rslearn_projects/olmoearth_run_data/nandi/finetune --scratch_path /weka/dfive-default/yawenz/datasets/scratch_ft_v3

## 4. Comparing different set-up (multimodal, tasks)
## 5. Using your fine-tuned model
