# kessie-mlops-lab

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-LLM-ee4c2c?logo=pytorch&logoColor=white)
![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Transformers-yellow?logo=huggingface&logoColor=black)
![Google Colab](https://img.shields.io/badge/Google%20Colab-T4-F9AB00?logo=googlecolab&logoColor=white)
![LLMOps](https://img.shields.io/badge/LLMOps-Lab-6f42c1)
![License](https://img.shields.io/badge/License-MIT-green)

A small-scale **personal LLMOps laboratory** for experimenting with, training, and deploying language models.

Each experiment is organized under the [`projects/`](projects/) directory, while generated datasets, checkpoints, and other artifacts are stored in [`artifacts/`](artifacts/).

## Raikiri

**Raikiri** is the first experiment in this repository: a compact Vietnamese language model based on the **Intern-S2-Mobius** architecture.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/antialberteinstein/kessie-mlops-lab/blob/main/notebooks/train-raikiri.ipynb)

The Google Colab notebook automatically:

- Clones this repository.
- Installs the required dependencies.
- Starts TensorBoard.
- Trains Raikiri on an NVIDIA T4 GPU.

### Running locally

```bash
python -m pip install -r projects/raikiri/requirements.txt

python projects/raikiri/train.py

python projects/raikiri/generate.py
```

See [`projects/raikiri`](projects/raikiri) for model configuration, training details, and Google Colab usage instructions.

### Training with Docker

On a Linux host with an NVIDIA GPU and NVIDIA Container Toolkit:

```bash
docker compose -f compose.raikiri.yaml up --build -d
docker compose -f compose.raikiri.yaml logs -f train
```

The dataset is mounted from `./dataset`; checkpoints and TensorBoard logs are
stored in `./artifacts/raikiri`. Open <http://127.0.0.1:6006> for TensorBoard.
See the [Docker instructions](projects/raikiri/README.md#docker-compose-training)
for custom mounts and ports.

## Repository structure

```text
kessie-mlops-lab/
├── artifacts/              # Generated datasets, checkpoints, and artifacts
├── notebooks/              # Experiment and Google Colab notebooks
├── projects/
│   └── raikiri/            # Raikiri experiment
└── README.md
```

## Goals

This repository serves as a personal experimentation environment for:

- Training and evaluating language models.
- Experimenting with new LLM architectures.
- Managing datasets and model checkpoints.
- Monitoring training runs with TensorBoard.
- Building reproducible LLMOps workflows.
- Experimenting with inference and text generation.
