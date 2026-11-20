"""Every install path uses the uv lock and keeps the runtime's CUDA torch."""

import json
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCKED_INSTALL = ("uv export", "--frozen", "--no-dev", "--prune torch", "uv pip install --system")
OLD_REQUIREMENTS = "projects/raikiri/requirements.txt"


def _setup_cell_source():
    cells = json.loads((ROOT / "notebooks" / "train-raikiri.ipynb").read_text(encoding="utf-8"))["cells"]
    return "".join(next(cell for cell in cells if cell.get("id") == "setup")["source"])


def test_notebook_installs_from_uv_lock_without_replacing_torch():
    source = _setup_cell_source()

    assert all(part in source for part in LOCKED_INSTALL)
    assert OLD_REQUIREMENTS not in source


def test_dockerfile_installs_from_uv_lock_without_replacing_torch():
    source = (ROOT / "projects" / "raikiri" / "Dockerfile").read_text(encoding="utf-8")

    assert "COPY pyproject.toml uv.lock" in source
    assert all(part in source for part in LOCKED_INSTALL)
    assert OLD_REQUIREMENTS not in source


def test_transformers_stays_pinned_to_the_remote_code_revision():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert "transformers==5.2.0" in project["project"]["dependencies"]
    assert (ROOT / "uv.lock").is_file()


def test_colab_cli_is_pinned_in_its_own_uv_project():
    # google-colab-cli needs Python >= 3.13; Raikiri must stay installable on 3.11/3.12.
    tool_dir = ROOT / "tools" / "colab-cli"
    tool = tomllib.loads((tool_dir / "pyproject.toml").read_text(encoding="utf-8"))
    raikiri = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    raikiri_packages = raikiri["project"]["dependencies"] + raikiri["dependency-groups"]["dev"]

    assert tool["project"]["dependencies"] == ["google-colab-cli"]
    assert (tool_dir / "uv.lock").is_file()
    assert not any(name.startswith("google-colab-cli") for name in raikiri_packages)


def test_colab_notebook_outputs_are_not_committed():
    # `colab exec -f` writes <notebook>_output.ipynb with every cell output next to the notebook.
    assert "*_output.ipynb" in (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
