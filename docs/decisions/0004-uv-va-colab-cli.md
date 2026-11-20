# 0004. uv cho môi trường; Colab CLI để chạy notebook trên runtime Colab

- Trạng thái: Chấp nhận; cách cài Colab CLI và cách chạy được thay bởi [0006](0006-cach-chay-colab-cli-va-secret.md)
- Ngày: 2026-11-21 · Người quyết định: chủ repo

## Bối cảnh
Hiện tại dependency cài bằng `pip install -r projects/raikiri/requirements.txt`, và notebook chạy bằng cách mở Colab trên web rồi chọn "Run all". Chủ repo muốn chạy notebook từ terminal và có môi trường tái lập được. Máy phát triển là macOS arm64, không có CUDA.

## Các phương án
| Phương án | Ưu | Nhược |
|---|---|---|
| **uv + Colab CLI chính chủ** (`google-colab-cli`) | Chạy notebook trên T4 từ terminal (`colab new --gpu T4`, `colab exec -f`, `colab stop`); lock file tái lập được | CLI mới; chưa có tài liệu về secret/biến môi trường và đồng bộ thư mục |
| Colab nối vào runtime local (Jupyter trên máy này) | Không tốn compute unit | Mac không có CUDA, notebook đang yêu cầu CUDA; không có `google.colab.userdata` |
| Giữ pip + Colab web | Không phải đổi gì | Không tái lập được; phải thao tác trên trình duyệt |

## Quyết định
- **uv** quản lý môi trường: `pyproject.toml` + `uv.lock` thay cho `requirements.txt`. Test chạy bằng `uv run`. Giữ ghim `transformers==5.2.0` (xem ADR 0001).
- **Colab CLI** (`uv tool install google-colab-cli`) là cách chạy notebook chính: `colab new -s raikiri --gpu T4` → `colab exec -s raikiri -f notebooks/train-raikiri.ipynb` → `colab download …` → `colab stop -s raikiri`. Notebook vẫn tự clone repo trên VM, nên không cần đồng bộ thư mục. Nút "Open in Colab" vẫn dùng được như đường phụ.
- Cho tới khi issue chuyển đổi được merge, CI chạy test bằng `uv run --no-project --with pytest`.

## Hệ quả
- Được: một lệnh từ terminal; lock file chung cho máy local, CI và Docker.
- Việc phải làm (issue riêng): tạo `pyproject.toml`/`uv.lock`; cập nhật Dockerfile, notebook, README; cách truyền `HF_TOKEN` khi chạy không tương tác (`getpass` sẽ treo; chưa biết `google.colab.userdata` có chạy dưới CLI không).
- Bị loại: Colab nối runtime local trên Mac (không có CUDA); giữ pip + Colab web làm đường chính.
- Điều kiện xem xét lại: Colab CLI ngừng hỗ trợ, hoặc chuyển sang máy có GPU riêng.
