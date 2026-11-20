"""Train Raikiri from projects/raikiri/config.json or another JSON config file."""

import argparse
import json
import os
import time
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path

# Raikiri trains with PyTorch only. Avoid importing unrelated TensorFlow/Keras
# integrations from shared environments where their native dependencies may clash.
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("USE_FLAX", "0")

from config import ConfigError, exit_on_config_error, load_config
from data import load_corpus, load_or_train_tokenizer, prepare_dataset
from model import build_model


@contextmanager
def training_stage(label):
    """Show slow training phases immediately in notebook output."""
    print("[Raikiri] {}...".format(label), flush=True)
    started = time.monotonic()
    try:
        yield
    except Exception:
        print("[Raikiri] {} failed after {:.1f}s".format(label, time.monotonic() - started), flush=True)
        raise
    print("[Raikiri] {} done in {:.1f}s".format(label, time.monotonic() - started), flush=True)


def require_cuda():
    """Stop before any download: training uses fp16 and needs an NVIDIA GPU."""
    import torch

    if not torch.cuda.is_available():
        raise SystemExit(
            "[Raikiri] Training needs a CUDA GPU (Colab T4 or a Linux NVIDIA host); none was found."
        )


def run_training(data_config, model_config, train_config):
    """Build and train the model using the supplied configuration objects."""
    with training_stage("Importing training libraries"):
        from transformers import Trainer, TrainingArguments, default_data_collator

    # Transformers 5.x reads this from the environment, not TrainingArguments.logging_dir.
    tensorboard_dir = Path(train_config.output_dir).parent / "tensorboard"
    tensorboard_dir.mkdir(parents=True, exist_ok=True)
    os.environ["TENSORBOARD_LOGGING_DIR"] = str(tensorboard_dir.resolve())

    with training_stage("Loading corpus"):
        corpus = load_corpus(data_config)
    print(
        "[Raikiri] Corpus rows: {} train, {} validation".format(
            len(corpus["train"]), len(corpus["validation"])
        ),
        flush=True,
    )
    with training_stage("Preparing tokenizer"):
        tokenizer = load_or_train_tokenizer(corpus["train"], data_config)
    with training_stage("Tokenizing and packing dataset"):
        dataset = prepare_dataset(corpus, tokenizer, data_config)
    print(
        "[Raikiri] Packed examples: {} train, {} validation".format(
            len(dataset["train"]), len(dataset["validation"])
        ),
        flush=True,
    )
    with training_stage("Building model"):
        model = build_model(tokenizer, model_config, data_config)

    with training_stage("Initializing Trainer"):
        trainer = Trainer(
            model=model,
            args=TrainingArguments(
                **asdict(train_config),
                eval_strategy="steps",
                save_strategy="steps",
                logging_strategy="steps",
                logging_first_step=True,
                report_to="tensorboard",
                run_name=model_config.name,
                remove_unused_columns=False,
            ),
            train_dataset=dataset["train"],
            eval_dataset=dataset["validation"],
            data_collator=default_data_collator,
            processing_class=tokenizer,
        )
    with training_stage("Training model"):
        train_output = trainer.train()
    with training_stage("Evaluating model"):
        eval_metrics = trainer.evaluate()
    with training_stage("Saving model"):
        trainer.save_model(train_config.output_dir)
        tokenizer.save_pretrained(train_config.output_dir)
        last_loss_log = next(
            (entry for entry in reversed(trainer.state.log_history) if "loss" in entry),
            None,
        )
        metrics = {
            "last_logged_train_loss": float(last_loss_log["loss"]) if last_loss_log else None,
            "last_logged_step": int(last_loss_log["step"]) if last_loss_log else None,
            "average_train_loss": float(train_output.metrics["train_loss"]),
            "eval_loss": float(eval_metrics["eval_loss"]),
            "global_step": int(trainer.state.global_step),
        }
        output_dir = Path(train_config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "training_metrics.json").write_text(
            json.dumps(metrics, indent=2) + "\n", encoding="utf-8"
        )
    print(
        "[Raikiri] Last logged training loss: {} at step {}".format(
            metrics["last_logged_train_loss"], metrics["last_logged_step"]
        ),
        flush=True,
    )
    print("[Raikiri] Training complete: {}".format(train_config.output_dir), flush=True)


def build_parser():
    parser = argparse.ArgumentParser(
        description="Train Raikiri from projects/raikiri/config.json; RAIKIRI_<SECTION>_<KEY> overrides a value."
    )
    parser.add_argument(
        "config",
        nargs="?",
        type=Path,
        help="optional path to another JSON config file with the same keys",
    )
    return parser


def main(argv=None):
    parser = build_parser()
    arguments = parser.parse_args(argv)
    try:
        configs = load_config(arguments.config)
    except ConfigError as error:
        exit_on_config_error(error)
    require_cuda()
    run_training(*configs)


if __name__ == "__main__":
    main()
