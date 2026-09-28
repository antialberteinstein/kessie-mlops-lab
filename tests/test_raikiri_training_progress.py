"""Progress reporting for the Raikiri training entry point."""

import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from unittest.mock import patch


RAIKIRI_DIR = Path(__file__).resolve().parents[1] / "projects" / "raikiri"
sys.path.insert(0, str(RAIKIRI_DIR))
import train  # noqa: E402


@dataclass
class TrainConfig:
    output_dir: str
    logging_steps: int = 10


class Rows:
    def __len__(self):
        return 12


class FakeTrainer:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def train(self):
        pass

    def evaluate(self):
        pass

    def save_model(self, output_dir):
        pass


class FakeTokenizer:
    def save_pretrained(self, output_dir):
        pass


def fake_transformers():
    module = ModuleType("transformers")
    module.Trainer = FakeTrainer
    module.TrainingArguments = lambda **kwargs: kwargs
    module.default_data_collator = object()
    return module


def test_training_reports_preparation_stages_and_completion(tmp_path, capsys):
    config = TrainConfig(str(tmp_path / "checkpoints"))
    corpus = {"train": Rows(), "validation": Rows()}
    dataset = {"train": Rows(), "validation": Rows()}
    output_before_loading = []

    def load_corpus_after_progress(_config):
        output_before_loading.append(capsys.readouterr().out)
        return corpus

    with (
        patch.dict(sys.modules, {"transformers": fake_transformers()}),
        patch.object(train, "load_corpus", side_effect=load_corpus_after_progress),
        patch.object(train, "load_or_train_tokenizer", return_value=FakeTokenizer()),
        patch.object(train, "prepare_dataset", return_value=dataset),
        patch.object(train, "build_model", return_value=object()),
    ):
        train.run_training(object(), train.DEFAULT_MODEL, config)

    assert "Loading corpus..." in output_before_loading[0]
    output = output_before_loading[0] + capsys.readouterr().out
    for stage in (
        "Loading corpus",
        "Preparing tokenizer",
        "Tokenizing and packing dataset",
        "Building model",
        "Training model",
        "Evaluating model",
        "Saving model",
    ):
        assert stage in output
    assert "Training complete" in output


def test_training_reports_failed_stage_before_raising(tmp_path, capsys):
    config = TrainConfig(str(tmp_path / "checkpoints"))
    with (
        patch.dict(sys.modules, {"transformers": fake_transformers()}),
        patch.object(train, "load_corpus", side_effect=RuntimeError("network unavailable")),
    ):
        try:
            train.run_training(object(), train.DEFAULT_MODEL, config)
        except RuntimeError as error:
            assert str(error) == "network unavailable"
        else:
            raise AssertionError("Expected the corpus loading error")

    output = capsys.readouterr().out
    assert "Loading corpus" in output
    assert "failed" in output.lower()
