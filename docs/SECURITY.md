# Security notes — kessie-mlops-lab

## Biện pháp đã triển khai
- Xác thực: không có tài khoản người dùng. Secret duy nhất là `HF_TOKEN` (quyền ghi), lưu ở `.env` hoặc Colab Secrets.
- Code bên ngoài: `trust_remote_code=True` chỉ với revision `internlm/Intern-S2-Mobius` đã ghim (ADR 0001).
- Cấu hình: chỉ đọc JSON (`config.json` hoặc file JSON được truyền vào) và biến môi trường; không thực thi file cấu hình (ADR 0005, #5).
- Lỗi: chỉ hiển thị thông báo đã map theo mã; không hiển thị/log payload server, token, credentials.
- Secret: chỉ biến public trong client; secret nằm ở server/vault/CI secrets.
- Log: không log dữ liệu cá nhân hoặc tài chính.

## Dependency audit
- Lệnh:
  ```bash
  uv export --frozen --no-dev --no-emit-project --no-hashes -o /tmp/audit.txt
  uvx pip-audit -r /tmp/audit.txt --no-deps --disable-pip
  ```
- Lần chạy gần nhất: 2026-11-21 (PR của #3). Kết quả: 6 cảnh báo, tất cả ở `transformers==5.2.0`; các gói khác không có cảnh báo.
- Cảnh báo đã biết và lý do chấp nhận tạm thời: `transformers==5.2.0` bị ghim theo remote code Mobius (ADR 0001).
  - PYSEC-2026-2289: RCE qua `config.json` độc hại; sửa ở 5.3.0.
  - PYSEC-2026-2290: chạy code khi nạp LightGlue; chưa có bản sửa.
  - PYSEC-2026-3929: ghi file tuỳ ý (path traversal) trong `save_pretrained()` của tokenizer/processor; sửa ở 5.10.0.
  - PYSEC-2026-4174: `load_custom_generate()` ghi file Python từ xa; chưa có bản sửa.
  - Lý do chấp nhận tạm thời: Raikiri chỉ nạp config từ revision upstream đã ghim, tokenizer là artifact của chính repo, không dùng LightGlue hay `load_custom_generate`. Không nạp config, model hay tokenizer từ nguồn khác khi chưa nâng `transformers`. Việc nâng cần kiểm tra lại adapter trong `model.py` và cần chủ repo quyết (ADR 0001). Không dùng "fix --force" làm hạ cấp framework.

## Giới hạn vận hành
- TensorBoard không có đăng nhập; mặc định bind `127.0.0.1`. Mở ra ngoài thì phải có firewall hoặc proxy có xác thực.
- Chưa kiểm toán: cách truyền `HF_TOKEN` qua Colab CLI; nội dung remote code upstream.
