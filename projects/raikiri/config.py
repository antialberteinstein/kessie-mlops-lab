"""Importable experiment configuration; edit this file before a training run."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class DataConfig:
    dataset_name: str = "vietgpt/wikipedia_vi"
    dataset_split: str = "train"
    text_column: str = "text"
    sequence_length: int = 512
    validation_fraction: float = 0.02
    max_samples: Optional[int] = 50_000
    tokenizer_vocab_size: int = 16_000
    tokenizer_dir: str = "artifacts/raikiri/tokenizer"
    seed: int = 42


@dataclass(frozen=True)
class ModelConfig:
    name: str = "raikiri"
    # Pinned because this repository supplies executable Transformers remote code.
    architecture_repo: str = "internlm/Intern-S2-Mobius"
    architecture_revision: str = "1b23c974ac860b182c61732299ae4fc432a8cf54"
    hidden_size: int = 384
    num_hidden_layers: int = 8
    num_attention_heads: int = 6
    num_key_value_heads: int = 2
    head_dim: int = 64
    num_memory_blocks: int = 2
    num_memory_experts: int = 32
    experts_per_token: int = 2
    expert_intermediate_size: int = 128
    local_expert_intermediate_size: int = 768
    full_attention_every: int = 4
    sliding_window: int = 256
    # auto => FlashAttention-2 on Ampere+, SDPA on a Colab T4 (Turing).
    # Use "flex_attention" for a block-sparse sliding-window kernel on supported GPUs.
    attention_backend: str = "auto"


@dataclass(frozen=True)
class TrainConfig:
    output_dir: str = "artifacts/raikiri/checkpoints"
    num_train_epochs: float = 1.0
    learning_rate: float = 3e-4
    weight_decay: float = 0.1
    warmup_ratio: float = 0.03
    per_device_train_batch_size: int = 4
    per_device_eval_batch_size: int = 4
    gradient_accumulation_steps: int = 8
    logging_steps: int = 10
    eval_steps: int = 250
    save_steps: int = 250
    save_total_limit: int = 2
    fp16: bool = True
    bf16: bool = False
    gradient_checkpointing: bool = True
    seed: int = 42


DATA = DataConfig()
MODEL = ModelConfig()
TRAIN = TrainConfig()
