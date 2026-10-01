"""Configuration used by the containerized Raikiri training job."""

import sys
from pathlib import Path

import pytest


RAIKIRI_DIR = Path(__file__).resolve().parents[1] / "projects" / "raikiri"
sys.path.insert(0, str(RAIKIRI_DIR))
from train import load_config  # noqa: E402


def test_docker_config_uses_mounted_dataset_and_artifact_paths(tmp_path, monkeypatch):
    monkeypatch.setenv("RAIKIRI_DATASET_NAME", str(tmp_path))
    monkeypatch.setenv("RAIKIRI_MAX_SAMPLES", "123")
    monkeypatch.setenv("RAIKIRI_TEXT_COLUMN", "content")

    data, model, train = load_config(RAIKIRI_DIR / "docker_config.py")

    assert data.dataset_name == str(tmp_path)
    assert data.max_samples == 123
    assert data.text_column == "content"
    assert data.tokenizer_dir == "/workspace/artifacts/raikiri/tokenizer"
    assert train.output_dir == "/workspace/artifacts/raikiri/checkpoints"
    assert model.name == "raikiri"


def test_docker_config_rejects_missing_mounted_dataset(tmp_path, monkeypatch):
    monkeypatch.setenv("RAIKIRI_DATASET_NAME", str(tmp_path / "missing"))

    with pytest.raises(ValueError, match="Dataset directory does not exist"):
        load_config(RAIKIRI_DIR / "docker_config.py")
