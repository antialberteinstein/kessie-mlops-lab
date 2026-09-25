# kessie-mlops-lab

A small personal LLMOps lab. Each experiment lives in `projects/`; generated
datasets and checkpoints live in `artifacts/`.

## Raikiri

Raikiri is the first experiment: a compact Vietnamese language model using the
Intern-S2-Mobius architecture.

```bash
python -m pip install -r projects/raikiri/requirements.txt
python projects/raikiri/train.py
python projects/raikiri/generate.py
```

See [`projects/raikiri`](projects/raikiri) for configuration and Colab notes.
