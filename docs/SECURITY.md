# Security notes — kessie-mlops-lab

## Biện pháp đã triển khai
- Xác thực: không có tài khoản người dùng. Secret duy nhất là `HF_TOKEN` (quyền ghi), lưu ở `.env` hoặc Colab Secrets.
- Code bên ngoài: `trust_remote_code=True` chỉ với revision `internlm/Intern-S2-Mobius` đã ghim (ADR 0001).
- Cấu hình: hiện `train.py` thực thi file cấu hình Python do người dùng truyền vào; sẽ bỏ khi chuyển sang `config.json` (ADR 0005).
- Lỗi: chỉ hiển thị thông báo đã map theo mã; không hiển thị/log payload server, token, credentials.
- Secret: chỉ biến public trong client; secret nằm ở server/vault/CI secrets.
- Log: không log dữ liệu cá nhân hoặc tài chính.

## Dependency audit
- Lệnh: `uvx pip-audit -r projects/raikiri/requirements.txt`. Chưa chạy lần nào.
- Cảnh báo đã biết và lý do chấp nhận tạm thời: chưa có. Không dùng "fix --force" làm hạ cấp framework.

## Giới hạn vận hành
- TensorBoard không có đăng nhập; mặc định bind `127.0.0.1`. Mở ra ngoài thì phải có firewall hoặc proxy có xác thực.
- Chưa kiểm toán: cách truyền `HF_TOKEN` qua Colab CLI; nội dung remote code upstream.
