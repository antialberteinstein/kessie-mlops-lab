FROM pytorch/pytorch:2.6.0-cuda11.8-cudnn9-runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    USE_TF=0 \
    USE_FLAX=0 \
    HF_HOME=/workspace/artifacts/raikiri/hf-cache

WORKDIR /workspace

COPY --from=ghcr.io/astral-sh/uv:0.13.9 /uv /bin/uv
# Install locked dependencies but keep the image's CUDA build of torch (ADR 0004).
COPY pyproject.toml uv.lock /tmp/raikiri-env/
RUN uv export --project /tmp/raikiri-env --frozen --no-dev --no-emit-project --no-hashes --prune torch \
        -o /tmp/raikiri-requirements.txt \
    && uv pip install --system --no-cache -r /tmp/raikiri-requirements.txt

COPY projects/raikiri /workspace/projects/raikiri

EXPOSE 6006
CMD ["python", "-u", "projects/raikiri/train.py"]
