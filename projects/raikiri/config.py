"""Raikiri configuration: values live in config.json, environment variables override them.

Code never supplies values (ADR 0005). Each key can be overridden with
RAIKIRI_<SECTION>_<KEY>, for example RAIKIRI_DATA_MAX_SAMPLES=1000.
"""

import json
import os
import sys
import typing
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Optional


CONFIG_PATH = Path(__file__).resolve().parent / "config.json"


class ConfigError(ValueError):
    """Configuration is missing, malformed, or invalid."""


@dataclass(frozen=True)
class DataConfig:
    dataset_name: str
    dataset_split: str
    text_column: str
    sequence_length: int
    validation_fraction: float
    max_samples: Optional[int]
    tokenizer_vocab_size: int
    tokenizer_dir: str
    seed: int


@dataclass(frozen=True)
class ModelConfig:
    name: str
    # Pinned because this repository supplies executable Transformers remote code.
    architecture_repo: str
    architecture_revision: str
    hidden_size: int
    num_hidden_layers: int
    num_attention_heads: int
    num_key_value_heads: int
    head_dim: int
    num_memory_blocks: int
    num_memory_experts: int
    experts_per_token: int
    expert_intermediate_size: int
    local_expert_intermediate_size: int
    full_attention_every: int
    sliding_window: int
    # auto => FlashAttention-2 on Ampere+, SDPA on a Colab T4 (Turing).
    # Use "flex_attention" for a block-sparse sliding-window kernel on supported GPUs.
    attention_backend: str


@dataclass(frozen=True)
class TrainConfig:
    # Field names match transformers.TrainingArguments; train.py passes them through.
    output_dir: str
    num_train_epochs: float
    learning_rate: float
    weight_decay: float
    warmup_ratio: float
    per_device_train_batch_size: int
    per_device_eval_batch_size: int
    gradient_accumulation_steps: int
    logging_steps: int
    eval_steps: int
    save_steps: int
    save_total_limit: int
    fp16: bool
    bf16: bool
    gradient_checkpointing: bool
    seed: int


SECTIONS = {"data": DataConfig, "model": ModelConfig, "train": TrainConfig}


def _env_name(section, key):
    return "RAIKIRI_{}_{}".format(section, key).upper()


def _type_matches(value, annotation):
    if typing.get_origin(annotation) is typing.Union:
        return any(_type_matches(value, option) for option in typing.get_args(annotation))
    if annotation is type(None):
        return value is None
    if annotation is bool:
        return isinstance(value, bool)
    if annotation is int:
        return isinstance(value, int) and not isinstance(value, bool)
    if annotation is float:
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return isinstance(value, annotation)


def _from_env(raw, annotation, env_name):
    if annotation is str:
        return raw
    try:
        return json.loads(raw)
    except json.JSONDecodeError as error:
        raise ConfigError("{}={!r} is not a valid {} value".format(env_name, raw, _type_name(annotation))) from error


def _type_name(annotation):
    if typing.get_origin(annotation) is typing.Union:
        return " or ".join(_type_name(option) for option in typing.get_args(annotation))
    return "null" if annotation is type(None) else annotation.__name__


def _build_section(section, cls, values, path):
    if not isinstance(values, dict):
        raise ConfigError("section '{}' in {} must be an object".format(section, path))
    hints = typing.get_type_hints(cls)
    known = {field.name for field in fields(cls)}
    unknown = sorted(set(values) - known)
    if unknown:
        raise ConfigError("unknown key '{}.{}' in {}".format(section, unknown[0], path))

    resolved = {}
    for name in (field.name for field in fields(cls)):
        env_name = _env_name(section, name)
        if env_name in os.environ:
            value = _from_env(os.environ[env_name], hints[name], env_name)
            source = env_name
        elif name in values:
            value = values[name]
            source = "'{}.{}' in {}".format(section, name, path)
        else:
            raise ConfigError(
                "missing key '{}.{}' - add it to {} (or set {})".format(section, name, path, env_name)
            )
        if not _type_matches(value, hints[name]):
            raise ConfigError("{} must be {}, got {!r}".format(source, _type_name(hints[name]), value))
        resolved[name] = float(value) if hints[name] is float else value
    return cls(**resolved)


def _validate(data):
    if data.max_samples is not None and data.max_samples < 2:
        raise ConfigError("data.max_samples must be null or at least 2, got {}".format(data.max_samples))
    if data.dataset_name.startswith("/") and not Path(data.dataset_name).is_dir():
        raise ConfigError("dataset directory does not exist: {}".format(data.dataset_name))


def load_config(path=None):
    """Return (DataConfig, ModelConfig, TrainConfig) from config.json plus environment overrides."""
    path = Path(path).expanduser().resolve() if path is not None else CONFIG_PATH
    try:
        values = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ConfigError("config file does not exist: {}".format(path)) from error
    except json.JSONDecodeError as error:
        raise ConfigError("{} is not valid JSON: {}".format(path, error)) from error
    if not isinstance(values, dict):
        raise ConfigError("{} must contain a JSON object".format(path))

    unknown = sorted(set(values) - set(SECTIONS))
    if unknown:
        raise ConfigError("unknown section '{}' in {}".format(unknown[0], path))
    missing = [section for section in SECTIONS if section not in values]
    if missing:
        raise ConfigError("missing section '{}' - add it to {}".format(missing[0], path))

    data, model, train = (
        _build_section(section, cls, values[section], path) for section, cls in SECTIONS.items()
    )
    _validate(data)
    return data, model, train


def exit_on_config_error(error):
    """Print a short red message and stop; configuration errors never show a traceback."""
    print("\033[31m[Raikiri] Config error: {}\033[0m".format(error), file=sys.stderr, flush=True)
    sys.exit(1)
