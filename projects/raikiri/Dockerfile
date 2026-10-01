FROM pytorch/pytorch:2.6.0-cuda11.8-cudnn9-runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    USE_TF=0 \
    USE_FLAX=0 \
    HF_HOME=/workspace/artifacts/raikiri/hf-cache

WORKDIR /workspace

COPY projects/raikiri/requirements.txt /tmp/raikiri-requirements.txt
RUN python -m pip install --no-cache-dir -r /tmp/raikiri-requirements.txt

COPY projects/raikiri /workspace/projects/raikiri

EXPOSE 6006
CMD ["python", "-u", "projects/raikiri/train.py", "projects/raikiri/docker_config.py"]
