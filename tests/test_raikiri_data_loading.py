"""Bounded loading of the Raikiri corpus."""

import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import patch


RAIKIRI_DIR = Path(__file__).resolve().parents[1] / "projects" / "raikiri"
sys.path.insert(0, str(RAIKIRI_DIR))
import data  # noqa: E402


class FakeDataset:
    def __init__(self, rows):
        self.rows = rows

    @classmethod
    def from_generator(cls, generator, gen_kwargs):
        return cls(list(generator(**gen_kwargs)))

    def train_test_split(self, test_size, seed):
        assert test_size == 0.25
        assert seed == 42
        return {"train": self.rows[:3], "test": self.rows[3:]}


class FakeStream:
    features = {"text": "string"}

    def take(self, count):
        assert count == 4
        return iter({"text": str(index)} for index in range(count))


def test_capped_corpus_streams_only_requested_rows():
    calls = []
    module = ModuleType("datasets")
    module.Dataset = FakeDataset
    module.DatasetDict = lambda **splits: splits

    def load_dataset(name, split, streaming=False):
        calls.append((name, split, streaming))
        return FakeStream()

    module.load_dataset = load_dataset
    config = SimpleNamespace(
        dataset_name="sample/wiki", dataset_split="train", max_samples=4,
        validation_fraction=0.25, seed=42,
    )
    with patch.dict(sys.modules, {"datasets": module}):
        result = data.load_corpus(config)

    assert calls == [("sample/wiki", "train", True)]
    assert len(result["train"]) + len(result["validation"]) == 4


def test_uncapped_corpus_uses_regular_dataset():
    calls = []
    module = ModuleType("datasets")
    module.Dataset = FakeDataset
    module.DatasetDict = lambda **splits: splits

    def load_dataset(name, split, streaming=False):
        calls.append((name, split, streaming))
        return FakeDataset([{"text": str(index)} for index in range(4)])

    module.load_dataset = load_dataset
    config = SimpleNamespace(
        dataset_name="sample/wiki", dataset_split="train", max_samples=None,
        validation_fraction=0.25, seed=42,
    )
    with patch.dict(sys.modules, {"datasets": module}):
        result = data.load_corpus(config)

    assert calls == [("sample/wiki", "train", False)]
    assert len(result["train"]) + len(result["validation"]) == 4
