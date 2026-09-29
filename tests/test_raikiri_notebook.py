"""Notebook order and model-card inputs for the Colab training flow."""

import ast
import json
from pathlib import Path


NOTEBOOK = Path(__file__).resolve().parents[1] / "notebooks" / "train-raikiri.ipynb"


def test_training_shell_cell_is_followed_by_tensorboard():
    cells = json.loads(NOTEBOOK.read_text(encoding="utf-8"))["cells"]
    training_index = next(index for index, cell in enumerate(cells) if cell.get("id") == "training")
    training = "".join(cells[training_index]["source"])

    assert "!python -u projects/raikiri/train.py" in training
    assert "subprocess" not in training
    assert cells[training_index + 1]["id"] == "tensorboard"
    assert "%tensorboard --logdir artifacts/raikiri/tensorboard" in "".join(
        cells[training_index + 1]["source"]
    )
    assert all("%tensorboard" not in "".join(cell["source"]) for cell in cells[:training_index])


def test_model_card_reads_saved_training_loss(tmp_path):
    cells = json.loads(NOTEBOOK.read_text(encoding="utf-8"))["cells"]
    sample_cell = next(cell for cell in cells if cell.get("id") == "samples")
    source = "".join(sample_cell["source"])

    assert "import sys" in source
    assert "training_metrics.json" in source
    assert "Last logged training loss" in source
    assert "README.md" in source

    (tmp_path / "training_metrics.json").write_text(
        json.dumps(
            {
                "last_logged_train_loss": 2.25,
                "last_logged_step": 20,
                "average_train_loss": 2.5,
                "eval_loss": 2.4,
                "global_step": 20,
            }
        ),
        encoding="utf-8",
    )
    assignments = [
        statement
        for statement in ast.parse(source).body
        if isinstance(statement, ast.Assign)
        and any(
            isinstance(target, ast.Name)
            and target.id in {"training_metrics", "last_logged_loss", "last_loss_line", "model_card"}
            for target in statement.targets
        )
    ]
    namespace = {"json": json, "model_dir": tmp_path}
    exec(compile(ast.Module(body=assignments, type_ignores=[]), str(NOTEBOOK), "exec"), namespace)

    assert "Last logged training loss: 2.2500 at optimizer step 20" in namespace["model_card"]
    assert "Average training loss: 2.5000" in namespace["model_card"]
    assert "Final evaluation loss: 2.4000" in namespace["model_card"]
