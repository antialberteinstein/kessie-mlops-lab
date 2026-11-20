# 0006. Hai cách chạy notebook; Colab CLI trong project uv riêng; nguồn `HF_TOKEN` theo từng cách

- Trạng thái: Chấp nhận (thay phần cách cài và cách chạy Colab CLI trong 0004)
- Ngày: 2026-11-21 · Người quyết định: chủ repo

## Bối cảnh
- ADR 0004 ghi cài Colab CLI bằng `uv tool install`. Chủ repo muốn cài nó trong uv của chính repo để phiên bản được khoá.
- `google-colab-cli` (0.8.0) yêu cầu Python ≥ 3.13, trong khi môi trường Raikiri phải cài được trên Colab (3.12) và image Docker (3.11).
- Notebook cần `HF_TOKEN` để công bố model. Hiện nó hỏi bằng `getpass`, và ô đó sẽ treo khi chạy bằng `colab exec`.
- Đọc mã nguồn Colab CLI 0.8.0 cho thấy:
  - `colab exec --env K=V` chèn `os.environ['K'] = 'V'` vào đầu **mọi ô**, và đoạn code này được ghi nguyên văn vào `~/.config/colab-cli/history/<session>.jsonl`.
  - `colab upload` chỉ ghi đường dẫn vào history, không ghi nội dung file.
  - `colab exec -f x.ipynb` ghi `x_output.ipynb` chứa toàn bộ output ở máy.

## Quyết định
- **Hai cách chạy notebook:**
  1. **Colab CLI** (cách chính, từ terminal).
  2. **Colab web** (nút "Open in Colab").

  Docker Compose chỉ dùng để huấn luyện trực tiếp trên máy có CUDA. Docker không công bố model nên không cần `HF_TOKEN`.
- **Colab CLI cài trong project uv riêng** `tools/colab-cli/` (`pyproject.toml` + `uv.lock`, Python 3.13), chạy bằng `uv run --project tools/colab-cli colab …`. Môi trường Raikiri ở gốc repo không đổi.
- **Nguồn `HF_TOKEN` theo cách chạy** (triển khai trong #4):

  | Cách chạy | Nguồn | Cách nhận biết |
  |---|---|---|
  | Colab CLI | `.env` ở máy, được `colab upload` lên VM thành một file ngoài thư mục repo; notebook đọc xong thì xoá | File đó tồn tại |
  | Colab web | Colab Secrets `HF_TOKEN` (`google.colab.userdata`) | Không có file upload |

  Token được kiểm tra ở ô đầu, trước khi huấn luyện. Thiếu token thì dừng kèm hướng dẫn, không hỏi nhập bằng `getpass`. Token không bao giờ được in ra.
- `*_output.ipynb` được gitignore.

## Hệ quả
- Được: phiên bản Colab CLI được khoá trong repo; token không nằm trong code, tham số dòng lệnh, history hay output.
- Mất: có hai lock file (gốc repo và `tools/colab-cli/`); Dependabot theo dõi cả hai.
- Bị loại:
  - Nhóm dependency `colab` trong project gốc kèm venv 3.13 (lệch Python với Colab, xung đột scipy).
  - `uv tool install` (không khoá phiên bản trong repo).
  - `colab exec --env HF_TOKEN=…` (token bị ghi vào history ở mọi ô).
  - `getpass` qua CLI (treo, bị timeout).
- Chưa xác minh: thư mục gốc của đường dẫn `colab upload` trên VM, và việc kernel đọc được file đó. Cần chạy thử trên session CPU trước khi làm #4.
- Điều kiện xem xét lại: Colab CLI có cơ chế secret không ghi vào history, hoặc hỗ trợ Python 3.12.
