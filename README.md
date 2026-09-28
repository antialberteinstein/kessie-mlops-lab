# kessie-mlops-lab

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-LLM-ee4c2c?logo=pytorch&logoColor=white)
![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Transformers-yellow?logo=huggingface&logoColor=black)
![Google Colab](https://img.shields.io/badge/Google%20Colab-T4-F9AB00?logo=googlecolab&logoColor=white)
![LLMOps](https://img.shields.io/badge/LLMOps-Lab-6f42c1)
![License](https://img.shields.io/badge/License-MIT-green)

Một phòng thí nghiệm **LLMOps cá nhân** quy mô nhỏ dành cho việc thử nghiệm, huấn luyện và triển khai các mô hình ngôn ngữ.

Mỗi thí nghiệm được đặt trong thư mục [`projects/`](projects/), trong khi các dataset được sinh ra, checkpoint và các artifact khác được lưu trong [`artifacts/`](artifacts/).

## Raikiri

**Raikiri** là thí nghiệm đầu tiên của repository: một mô hình ngôn ngữ tiếng Việt nhỏ gọn sử dụng kiến trúc **Intern-S2-Mobius**.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/antialberteinstein/kessie-mlops-lab/blob/main/notebooks/train-raikiri.ipynb)

Notebook trên Google Colab sẽ tự động:

- Clone repository này.
- Cài đặt các dependency cần thiết.
- Khởi động TensorBoard.
- Huấn luyện Raikiri trên GPU NVIDIA T4.

### Chạy cục bộ

```bash
python -m pip install -r projects/raikiri/requirements.txt

python projects/raikiri/train.py

python projects/raikiri/generate.py
```

Xem thêm [`projects/raikiri`](projects/raikiri) để biết cấu hình mô hình, thông tin huấn luyện và hướng dẫn sử dụng Google Colab.

## Cấu trúc repository

```text
kessie-mlops-lab/
├── artifacts/              # Dataset, checkpoint và artifact được sinh ra
├── notebooks/              # Notebook phục vụ thử nghiệm và Colab
├── projects/
│   └── raikiri/            # Experiment Raikiri
└── README.md
```

## Mục tiêu

Repository này được sử dụng như một môi trường thử nghiệm cá nhân cho:

- Huấn luyện và đánh giá các mô hình ngôn ngữ.
- Thử nghiệm kiến trúc LLM mới.
- Quản lý dataset và model checkpoint.
- Theo dõi quá trình huấn luyện bằng TensorBoard.
- Xây dựng workflow LLMOps có thể tái lập.
- Thử nghiệm inference và text generation.
