"""Create label_raster from label.

If you run this, you will need to update the config.json for the dataset
to include the following entry:

"label_raster": {
      "band_sets": [
        {
          "bands": [
            "label"
          ],
          "dtype": "int32"
        }
      ],
      "type": "raster"
    },
"""

import argparse
import multiprocessing

import tqdm
from olmoearth_run.runner.tools.data_splitters.data_splitter_interface import (
    DataSplitterInterface,
)
from olmoearth_run.runner.tools.data_splitters.random_data_splitter import (
    RandomDataSplitter,
)
from rslearn.dataset.dataset import Dataset
from rslearn.dataset.window import Window
from rslearn.utils.mp import star_imap_unordered
from upath import UPath

LULC_CLASS_NAMES = [
    "invalid",
    "Water",
    "Bare Ground",
    "Rangeland",
    "Flooded Vegetation",
    "Trees",
    "Cropland",
    "Buildings",
]
CROPTYPE_CLASS_NAMES = [
    "invalid",
    "corn",
    "cassava",
    "rice",
    "sesame",
    "beans",
    "millet",
    "sorghum",
]
PROPERTY_NAME = "category"
BAND_NAME = "label"


def update_train_val_split(window: Window, splitter: DataSplitterInterface) -> None:
    """Create label raster for the given window."""
    if window.options["split"] in ["train", "val"]:
        split = splitter.choose_split_for_window(window)
        print(f"Window was {window.options['split']}, changing to {split}")
        window.options["split"] = split
        window.save()


if __name__ == "__main__":
    multiprocessing.set_start_method("forkserver")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ds_path",
        type=str,
        required=True,
        help="Path to the dataset",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=64,
        help="Number of worker processes to use",
    )
    args = parser.parse_args()

    dataset = Dataset(UPath(args.ds_path))
    windows = dataset.load_windows(workers=args.workers, show_progress=True)
    splitter = RandomDataSplitter(train_prop=0.8, val_prop=0.2, test_prop=0.0)
    # splitter = SpatialDataSplitter(
    #     train_prop=0.8, val_prop=0.2, test_prop=0.0, grid_size=32
    # )
    jobs = [dict(splitter=splitter, window=w) for w in windows]
    p = multiprocessing.Pool(args.workers)
    outputs = star_imap_unordered(p, update_train_val_split, windows)
    for _ in tqdm.tqdm(outputs, total=len(windows)):
        pass
    p.close()
