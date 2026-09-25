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
