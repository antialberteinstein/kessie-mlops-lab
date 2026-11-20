"""Model shape checks run before the model is built (AC-16)."""

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


RAIKIRI_DIR = Path(__file__).resolve().parents[1] / "projects" / "raikiri"
sys.path.insert(0, str(RAIKIRI_DIR))
import model  # noqa: E402


def shapes(**overrides):
    values = {"hidden_size": 384, "num_attention_heads": 6, "head_dim": 64, "sliding_window": 256}
    values.update(overrides)
    return SimpleNamespace(**values)


def test_hidden_size_must_match_heads_times_head_dim():
    with pytest.raises(ValueError, match="hidden_size"):
        model.configure_model(None, None, shapes(hidden_size=400), SimpleNamespace(sequence_length=512), "sdpa")


def test_sliding_window_cannot_exceed_sequence_length():
    with pytest.raises(ValueError, match="sliding_window"):
        model.configure_model(None, None, shapes(), SimpleNamespace(sequence_length=128), "sdpa")
