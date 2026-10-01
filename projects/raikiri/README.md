# Raikiri

A compact Vietnamese causal language model built with Hugging Face Datasets,
Transformers Trainer, Accelerate, and PyTorch. Raikiri uses the official pinned
`internlm/Intern-S2-Mobius` architecture with a much smaller configuration.

## Colab T4

```bash
!git clone <your-repository-url> kessie-mlops-lab
%cd kessie-mlops-lab
!pip install -r projects/raikiri/requirements.txt
!python projects/raikiri/train.py
```

The defaults use fp16, gradient checkpointing, and PyTorch SDPA. A T4 cannot run
standard FlashAttention-2, so `attention_backend="auto"` selects SDPA.

## Docker Compose training

Use a Linux host with an NVIDIA GPU, a compatible driver, Docker Compose, and
the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html).
The image is based on PyTorch 2.6 with CUDA 11.8 and installs the dependencies in
[`requirements.txt`](requirements.txt). From the repository root:

```bash
mkdir -p artifacts/raikiri
docker compose -f compose.raikiri.yaml up --build -d
docker compose -f compose.raikiri.yaml logs -f train
```

The `train` service runs `train.py` directly with unbuffered stdout, so progress
and errors appear in `docker compose logs`. The `tensorboard` service uses the
same image and stays available after training finishes at
<http://127.0.0.1:6006>.

The default read-only dataset mount is `./dataset` on the host to `/datasets` in
the container. Hugging Face Datasets reads supported text, CSV, JSON, or Parquet
files in that directory; a local `dataset/tokenizer_train.txt` is one example.
The first 50,000 rows are used by default. The writable artifact mount
is `./artifacts/raikiri` to `/workspace/artifacts/raikiri`, containing
`checkpoints/`, `tokenizer/`, `tensorboard/`, and the Hugging Face cache. These
files remain on the host when the containers stop.

To use other host directories or expose TensorBoard on a remote server:

```bash
RAIKIRI_DATA_DIR=/srv/corpus \
RAIKIRI_ARTIFACT_DIR=/srv/raikiri \
RAIKIRI_TB_BIND=0.0.0.0 \
docker compose -f compose.raikiri.yaml up --build -d
```

Set `RAIKIRI_DATASET_NAME` to another dataset directory inside the container or
a Hugging Face dataset ID, `RAIKIRI_TEXT_COLUMN` if the text field has another
name, `RAIKIRI_MAX_SAMPLES` to change the row cap, and `RAIKIRI_TB_PORT` to
change the host port. TensorBoard has no built-in login, so restrict remote
access with a firewall or authenticated proxy.

Stop both services with `docker compose -f compose.raikiri.yaml down`.

On an Ampere-or-newer GPU, FlashAttention-2 is optional:

```bash
!pip install flash-attn
!python projects/raikiri/train.py
```

For block-sparse sliding-window execution on supported hardware, set
`MODEL.attention_backend` to `"flex_attention"` in `config.py`.

Edit [`config.py`](config.py) before training. It can also be
imported normally:

```python
from config import DATA, MODEL, TRAIN
```

## Simple training commands

You can run the training file directly without installing the package and
without changing to a particular directory:

```bash
python /path/to/kessie-mlops-lab/projects/raikiri/train.py
```

From the directory containing `train.py`, the short form is:

```bash
python train.py
```

To use another configuration, pass a trusted Python file as the only argument:

```bash
python train.py small_config.py
```

The custom file must export `DATA`, `MODEL`, and `TRAIN`. Import the defaults
and replace only the settings you want to change:

```python
# small_config.py
from dataclasses import replace

from config import DATA, MODEL, TRAIN

DATA = replace(DATA, max_samples=1_000)
TRAIN = replace(TRAIN, num_train_epochs=0.1)
```

Config files are executable Python, so only use files you trust.

## Architecture note

Raikiri preserves Möbius's shared routed experts for knowledge storage and its
per-layer token mixers for reasoning. It also keeps sparse top-k experts and a
hybrid linear/full-attention schedule.

The pinned upstream causal-LM class currently omits `forward()`, so
[`model.py`](model.py) contains a small compatibility adapter.
