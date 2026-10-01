"""Raikiri paths and dataset selection for the Docker Compose training job."""

import os
from dataclasses import replace
from pathlib import Path

from config import DATA as DEFAULT_DATA
from config import MODEL as DEFAULT_MODEL
from config import TRAIN as DEFAULT_TRAIN


dataset_name = os.environ.get("RAIKIRI_DATASET_NAME", "/datasets").strip()
if not dataset_name:
    raise ValueError("RAIKIRI_DATASET_NAME must not be empty")
if dataset_name.startswith("/") and not Path(dataset_name).is_dir():
    raise ValueError("Dataset directory does not exist: {}".format(dataset_name))

max_samples = int(os.environ.get("RAIKIRI_MAX_SAMPLES", DEFAULT_DATA.max_samples))
if max_samples < 2:
    raise ValueError("RAIKIRI_MAX_SAMPLES must be at least 2")

DATA = replace(
    DEFAULT_DATA,
    dataset_name=dataset_name,
    max_samples=max_samples,
    text_column=os.environ.get("RAIKIRI_TEXT_COLUMN", DEFAULT_DATA.text_column),
    tokenizer_dir="/workspace/artifacts/raikiri/tokenizer",
)
MODEL = DEFAULT_MODEL
TRAIN = replace(DEFAULT_TRAIN, output_dir="/workspace/artifacts/raikiri/checkpoints")
