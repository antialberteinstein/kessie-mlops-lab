"""config.json + environment overrides; no defaults in code (ADR 0005, AC-08 to AC-10)."""

import dataclasses
import json
import subprocess
import sys
from pathlib import Path

import pytest


RAIKIRI_DIR = Path(__file__).resolve().parents[1] / "projects" / "raikiri"
sys.path.insert(0, str(RAIKIRI_DIR))
import config  # noqa: E402


def repo_config():
    return json.loads((RAIKIRI_DIR / "config.json").read_text(encoding="utf-8"))


def write_config(tmp_path, values):
    path = tmp_path / "config.json"
    path.write_text(json.dumps(values), encoding="utf-8")
    return path


@pytest.fixture(autouse=True)
def clear_overrides(monkeypatch):
    import os

    for name in list(os.environ):
        if name.startswith(("RAIKIRI_DATA_", "RAIKIRI_MODEL_", "RAIKIRI_TRAIN_")):
            monkeypatch.delenv(name)


def test_repository_config_json_loads_every_section():
    data, model, train = config.load_config()

    assert data.dataset_name == repo_config()["data"]["dataset_name"]
    assert model.architecture_revision == repo_config()["model"]["architecture_revision"]
    assert isinstance(train.learning_rate, float)


def test_dataclasses_have_no_default_values():
    for cls in (config.DataConfig, config.ModelConfig, config.TrainConfig):
        for field in dataclasses.fields(cls):
            assert field.default is dataclasses.MISSING, f"{cls.__name__}.{field.name}"
            assert field.default_factory is dataclasses.MISSING, f"{cls.__name__}.{field.name}"


def test_environment_overrides_json_values(tmp_path, monkeypatch):
    monkeypatch.setenv("RAIKIRI_DATA_MAX_SAMPLES", "123")
    monkeypatch.setenv("RAIKIRI_DATA_TEXT_COLUMN", "content")
    monkeypatch.setenv("RAIKIRI_TRAIN_FP16", "false")

    data, _, train = config.load_config()

    assert data.max_samples == 123
    assert data.text_column == "content"
    assert train.fp16 is False


def test_null_max_samples_from_environment_disables_the_cap(monkeypatch):
    monkeypatch.setenv("RAIKIRI_DATA_MAX_SAMPLES", "null")

    data, _, _ = config.load_config()

    assert data.max_samples is None


def test_environment_value_with_wrong_type_is_rejected(monkeypatch):
    monkeypatch.setenv("RAIKIRI_TRAIN_LEARNING_RATE", "fast")

    with pytest.raises(config.ConfigError, match="RAIKIRI_TRAIN_LEARNING_RATE"):
        config.load_config()


def test_missing_key_names_the_key_and_file(tmp_path):
    values = repo_config()
    del values["train"]["learning_rate"]
    path = write_config(tmp_path, values)

    with pytest.raises(config.ConfigError) as error:
        config.load_config(path)

    assert "train.learning_rate" in str(error.value)
    assert str(path) in str(error.value)


def test_unknown_key_is_rejected(tmp_path):
    values = repo_config()
    values["train"]["learnig_rate"] = 0.1
    path = write_config(tmp_path, values)

    with pytest.raises(config.ConfigError, match="train.learnig_rate"):
        config.load_config(path)


def test_json_value_with_wrong_type_is_rejected(tmp_path):
    values = repo_config()
    values["model"]["hidden_size"] = "384"
    path = write_config(tmp_path, values)

    with pytest.raises(config.ConfigError, match="model.hidden_size"):
        config.load_config(path)


def test_too_few_samples_are_rejected(monkeypatch):
    monkeypatch.setenv("RAIKIRI_DATA_MAX_SAMPLES", "1")

    with pytest.raises(config.ConfigError, match="max_samples"):
        config.load_config()


def test_missing_local_dataset_directory_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv("RAIKIRI_DATA_DATASET_NAME", str(tmp_path / "missing"))

    with pytest.raises(config.ConfigError, match="does not exist"):
        config.load_config()


def test_existing_local_dataset_directory_is_accepted(tmp_path, monkeypatch):
    monkeypatch.setenv("RAIKIRI_DATA_DATASET_NAME", str(tmp_path))

    data, _, _ = config.load_config()

    assert data.dataset_name == str(tmp_path)


def test_train_entry_point_reports_missing_key_without_traceback(tmp_path):
    values = repo_config()
    del values["data"]["seed"]
    path = write_config(tmp_path, values)

    result = subprocess.run(
        [sys.executable, str(RAIKIRI_DIR / "train.py"), str(path)],
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 1
    assert "data.seed" in result.stderr
    assert str(path) in result.stderr
    assert "\033[31m" in result.stderr
    assert "Traceback" not in result.stderr
