"""Train Raikiri from the default or a user-supplied Python config."""

import argparse
import importlib.util
import os
import time
from contextlib import contextmanager
from dataclasses import asdict, fields, is_dataclass
from pathlib import Path

# Raikiri trains with PyTorch only. Avoid importing unrelated TensorFlow/Keras
# integrations from shared environments where their native dependencies may clash.
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("USE_FLAX", "0")

from config import DATA as DEFAULT_DATA
from config import MODEL as DEFAULT_MODEL
from config import TRAIN as DEFAULT_TRAIN
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


def load_config(config_path=None):
    """Return DATA, MODEL, and TRAIN from a trusted Python config file."""
    if config_path is None:
        return DEFAULT_DATA, DEFAULT_MODEL, DEFAULT_TRAIN

    path = Path(config_path).expanduser().resolve()
    if path.suffix.lower() != ".py":
        raise ValueError("The config must be a Python file ending in .py")
    if not path.is_file():
        raise FileNotFoundError("Config file does not exist: {}".format(path))

    module_name = "_raikiri_user_config_{}".format(abs(hash(path)))
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ValueError("Could not load config file: {}".format(path))

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as error:
        raise ValueError("Could not execute config file {}: {}".format(path, error)) from error

    names = ("DATA", "MODEL", "TRAIN")
    missing = [name for name in names if not hasattr(module, name)]
    if missing:
        raise ValueError("Config file is missing: {}".format(", ".join(missing)))

    values = (module.DATA, module.MODEL, module.TRAIN)
    defaults = (DEFAULT_DATA, DEFAULT_MODEL, DEFAULT_TRAIN)
    invalid = [
        name
        for name, value, default in zip(names, values, defaults)
        if not is_dataclass(value)
        or isinstance(value, type)
        or any(not hasattr(value, field.name) for field in fields(default))
    ]
    if invalid:
        raise ValueError("Config values have the wrong type: {}".format(", ".join(invalid)))
    return values


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
        trainer.train()
    with training_stage("Evaluating model"):
        trainer.evaluate()
    with training_stage("Saving model"):
        trainer.save_model(train_config.output_dir)
        tokenizer.save_pretrained(train_config.output_dir)
    print("[Raikiri] Training complete: {}".format(train_config.output_dir), flush=True)


def build_parser():
    parser = argparse.ArgumentParser(
        description="Train Raikiri with the default config or a trusted Python config file."
    )
    parser.add_argument(
        "config",
        nargs="?",
        type=Path,
        help="optional .py file exporting DATA, MODEL, and TRAIN",
    )
    return parser


def main(argv=None):
    parser = build_parser()
    arguments = parser.parse_args(argv)
    try:
        configs = load_config(arguments.config)
    except (FileNotFoundError, ValueError) as error:
        parser.error(str(error))
    run_training(*configs)


if __name__ == "__main__":
    main()
