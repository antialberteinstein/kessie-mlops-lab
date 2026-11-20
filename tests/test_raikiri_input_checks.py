"""Early input checks and existing safety behavior (AC-05, AC-11, AC-12, AC-13)."""

import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

import pytest


RAIKIRI_DIR = Path(__file__).resolve().parents[1] / "projects" / "raikiri"
sys.path.insert(0, str(RAIKIRI_DIR))
import data  # noqa: E402
import model  # noqa: E402
import train  # noqa: E402


# AC-13: no CUDA -> stop before any data is loaded.

def fake_torch(cuda_available):
    module = ModuleType("torch")
    module.cuda = SimpleNamespace(is_available=lambda: cuda_available)
    return module


def test_training_stops_before_loading_data_without_cuda():
    with (
        patch.dict(sys.modules, {"torch": fake_torch(False)}),
        patch.object(train, "run_training") as run_training,
        pytest.raises(SystemExit) as stopped,
    ):
        train.main([])

    assert "CUDA" in str(stopped.value.code)
    run_training.assert_not_called()


def test_training_starts_when_cuda_is_available():
    with (
        patch.dict(sys.modules, {"torch": fake_torch(True)}),
        patch.object(train, "run_training") as run_training,
    ):
        train.main([])

    run_training.assert_called_once()


# AC-12: missing text column -> clear error before tokenizer training.

class ColumnsDataset:
    def __init__(self, columns):
        self.column_names = columns

    @classmethod
    def from_generator(cls, generator, gen_kwargs):
        rows = list(generator(**gen_kwargs))
        return cls(sorted(rows[0]))

    def train_test_split(self, test_size, seed):
        return {"train": self, "test": self}


def corpus_config(text_column):
    return SimpleNamespace(
        dataset_name="sample/wiki", dataset_split="train", max_samples=None,
        validation_fraction=0.25, seed=42, text_column=text_column,
    )


def fake_datasets(columns):
    module = ModuleType("datasets")
    module.Dataset = ColumnsDataset
    module.DatasetDict = lambda **splits: splits
    module.load_dataset = lambda name, split, streaming=False: ColumnsDataset(columns)
    return module


def test_missing_text_column_names_the_column_and_available_columns():
    with patch.dict(sys.modules, {"datasets": fake_datasets(["title", "body"])}):
        with pytest.raises(ValueError) as error:
            data.load_corpus(corpus_config("text"))

    message = str(error.value)
    assert "'text'" in message
    assert "title" in message and "body" in message


def test_present_text_column_is_accepted():
    with patch.dict(sys.modules, {"datasets": fake_datasets(["text", "title"])}):
        corpus = data.load_corpus(corpus_config("text"))

    assert set(corpus) == {"train", "validation"}


# AC-11: an existing tokenizer.json is reused, never retrained.

def test_existing_tokenizer_is_reused_without_training(tmp_path):
    (tmp_path / "tokenizer.json").write_text("{}", encoding="utf-8")
    loaded = []

    tokenizers = ModuleType("tokenizers")
    for name in ("decoders", "models", "pre_tokenizers", "trainers"):
        setattr(tokenizers, name, SimpleNamespace())
    tokenizers.Tokenizer = lambda *args, **kwargs: pytest.fail("tokenizer must not be retrained")

    transformers = ModuleType("transformers")
    transformers.AutoTokenizer = SimpleNamespace(from_pretrained=lambda path: loaded.append(path) or "saved")
    transformers.PreTrainedTokenizerFast = None

    config = SimpleNamespace(tokenizer_dir=str(tmp_path))
    with patch.dict(sys.modules, {"tokenizers": tokenizers, "transformers": transformers}):
        result = data.load_or_train_tokenizer(train_dataset=None, config=config)

    assert result == "saved"
    assert loaded == [tmp_path]


# AC-05: checkpoint with missing or unexpected keys is rejected.

class FakeModel:
    def __init__(self, missing, unexpected):
        self.result = (missing, unexpected)
        self.tied = False

    def load_state_dict(self, state, strict):
        assert strict is False
        return self.result

    def tie_weights(self):
        self.tied = True


def load_with(tmp_path, missing, unexpected):
    (tmp_path / "model.safetensors").write_bytes(b"")
    safetensors_torch = ModuleType("safetensors.torch")
    safetensors_torch.load_file = lambda path, device: {}
    fake = FakeModel(missing, unexpected)
    with (
        patch.dict(sys.modules, {"safetensors": ModuleType("safetensors"), "safetensors.torch": safetensors_torch}),
        patch.object(model, "build_model", return_value=fake),
    ):
        return model.load_trained_model(None, tmp_path, None, None), fake


def test_checkpoint_missing_only_tied_lm_head_loads(tmp_path):
    loaded, fake = load_with(tmp_path, ["lm_head.weight"], [])

    assert loaded is fake
    assert fake.tied


@pytest.mark.parametrize(
    "missing, unexpected, key",
    [
        (["lm_head.weight", "model.norm.weight"], [], "model.norm.weight"),
        ([], ["extra.weight"], "extra.weight"),
    ],
)
def test_checkpoint_key_mismatch_names_the_key(tmp_path, missing, unexpected, key):
    with pytest.raises(RuntimeError, match=key):
        load_with(tmp_path, missing, unexpected)


def test_missing_checkpoint_file_is_reported(tmp_path):
    with patch.object(model, "build_model", return_value=FakeModel([], [])):
        with pytest.raises(FileNotFoundError, match="model.safetensors"):
            model.load_trained_model(None, tmp_path, None, None)
