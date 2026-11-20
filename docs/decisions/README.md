# Quyết định kiến trúc (ADR)

Mỗi quyết định quan trọng là một file `NNNN-tieu-de-ngan.md` (đánh số tăng dần, không sửa nội dung sau khi "Chấp nhận" — muốn đổi thì viết ADR mới với trạng thái "Thay thế NNNN").

| # | Tiêu đề | Trạng thái | Ngày |
|---|---|---|---|
| [0001](0001-mobius-remote-code-ghim-revision.md) | Remote code Intern-S2-Mobius ghim revision + adapter | Chấp nhận (hồi tố) | 2026-11-21 |
| [0002](0002-sparse-attention-hybrid.md) | Sparse attention: lai linear/full, cửa sổ trượt, backend tự chọn | Chấp nhận (hồi tố) | 2026-11-21 |
| [0003](0003-huan-luyen-trainer-docker.md) | Huấn luyện bằng HF Trainer; Docker Compose; công bố lên HF Hub | Chấp nhận (hồi tố) | 2026-11-21 |
| [0004](0004-uv-va-colab-cli.md) | uv cho môi trường; Colab CLI để chạy notebook | Chấp nhận | 2026-11-21 |
| [0005](0005-cau-hinh-config-json.md) | Cấu hình `config.json` + env ghi đè, không mặc định trong code | Chấp nhận | 2026-11-21 |
| [0006](0006-cach-chay-colab-cli-va-secret.md) | Hai cách chạy (Colab CLI, Colab web); Colab CLI trong project uv riêng; nguồn `HF_TOKEN` theo từng cách | Chấp nhận | 2026-11-21 |
| [0007](0007-token-colab-cli-trong-file.md) | Token OAuth của Colab CLI lưu trong file 0600 (wrapper `scripts/colab`), không dùng Keychain | Chấp nhận | 2026-11-21 |

## Mẫu

```markdown
# NNNN. <Tiêu đề>

- Trạng thái: Đề xuất | Chấp nhận | Bị loại | Thay thế bởi NNNN
- Ngày: YYYY-MM-DD · Người quyết định: <người dùng>

## Bối cảnh
<Vấn đề, ràng buộc (ngân sách, một người làm, nền tảng đích, dữ liệu nhạy cảm…).>

## Các phương án
| Phương án | Ưu | Nhược | Chi phí/khóa nhà cung cấp |
|---|---|---|---|

## Quyết định
<Chọn gì. Một đoạn.>

## Hệ quả
- Được: …  · Mất: …  · Việc phải làm: …
- Điều kiện xem xét lại: <khi nào mở lại quyết định này>
```

Phương án **bị loại** cũng ghi lại (trạng thái "Bị loại") để agent không đề xuất lại.
