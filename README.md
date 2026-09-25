# kessie-mlops-lab

A small personal LLMOps lab. Each experiment lives in `projects/`; generated
datasets and checkpoints live in `artifacts/`.

## Raikiri

Raikiri is the first experiment: a compact Vietnamese language model using the
Intern-S2-Mobius architecture.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/antialberteinstein/kessie-mlops-lab/blob/main/notebooks/train-raikiri.ipynb)

The Colab notebook clones this repository, installs the dependencies, starts
TensorBoard, and trains Raikiri on a T4 GPU.

```bash
python -m pip install -r projects/raikiri/requirements.txt
python projects/raikiri/train.py
python projects/raikiri/generate.py
```

See [`projects/raikiri`](projects/raikiri) for configuration and Colab notes.
