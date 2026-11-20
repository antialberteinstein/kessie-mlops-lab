# 0007. Token OAuth của Colab CLI lưu trong file 0600, không dùng macOS Keychain

- Trạng thái: Chấp nhận
- Ngày: 2026-11-21 · Người quyết định: chủ repo

## Bối cảnh
Colab CLI 0.8.0 lưu token OAuth bằng thư viện `keyring`; trên macOS đó là Keychain. Shell không tương tác (coding agent, script) không trả lời được hộp thoại xin quyền Keychain, nên bị từ chối (`-128 Keychain Access Denied`), rồi CLI đòi đăng nhập lại ở mọi lệnh. Ở terminal của người dùng thì không gặp lỗi này.

## Các phương án
| Phương án | Ưu | Nhược |
|---|---|---|
| **`PYTHON_KEYRING_BACKEND=keyrings.alt.file.PlaintextKeyring`, đặt trong wrapper `scripts/colab`** | Không sửa code bên thứ ba; chỉ áp dụng cho Colab CLI của repo; file được tạo với quyền 0600 | Token lưu dạng văn bản thường (không mã hoá) |
| `--auth adc` (gcloud) | Cách chính chủ | Cần cài gcloud và đăng nhập thêm |
| Sửa code trong `.venv` của Colab CLI | — | Bị ghi đè khi `uv sync`, không nằm trong git |
| Giữ Keychain, người dùng tự chạy mọi lệnh `colab` | Không đổi gì | Agent không chạy được Colab CLI |

## Quyết định
Mọi lệnh Colab CLI của repo chạy qua `scripts/colab`. Wrapper này đặt backend file của `keyrings.alt` (dependency trong `tools/colab-cli`). Token nằm ở `~/.local/share/python_keyring/keyring_pass.cfg`, quyền 0600, ngoài repo.

## Hệ quả
- Được: agent và script dùng lại được lần đăng nhập của người dùng.
- Mất: ai đọc được file trong tài khoản người dùng thì lấy được refresh token (scope Colab và Drive `drive.file`). Mức an toàn tương đương file ADC của gcloud.
- Muốn quay lại Keychain: bỏ dòng `PYTHON_KEYRING_BACKEND` trong `scripts/colab`, rồi đăng nhập lại.
- Kết quả chạy thử (session CPU, token giả):
  - `colab upload <file> .raikiri-secrets.env` đặt file ở `/.raikiri-secrets.env` (gốc VM; kernel chạy ở `/content`).
  - Kernel đọc được file và xoá được.
  - Token không xuất hiện trong `~/.config/colab-cli/history/`.
- Điều kiện xem xét lại: Colab CLI hỗ trợ lưu token trong file, hoặc có cách cấp quyền Keychain cho tiến trình không tương tác.
