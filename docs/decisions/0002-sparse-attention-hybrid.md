# 0002. Sparse attention: lai linear/full attention, cửa sổ trượt, backend tự chọn

- Trạng thái: Chấp nhận (ghi lại hồi tố từ code hiện có)
- Ngày: 2026-11-21 · Người quyết định: chủ repo

## Bối cảnh
Mục tiêu của Raikiri là model nhỏ dùng sparse attention, huấn luyện được trên T4 (Turing, không chạy được FlashAttention-2 chuẩn).

## Các phương án
| Phương án | Ưu | Nhược |
|---|---|---|
| Lai 3 lớp linear attention : 1 lớp full attention, mask cửa sổ trượt, chọn backend theo GPU | Dùng cơ chế có sẵn của upstream; chạy được trên T4 bằng SDPA | Mask cửa sổ trượt được bật bằng cách thay một symbol của upstream |
| Full attention ở mọi lớp | Đơn giản | Không thưa; tốn bộ nhớ ở chuỗi dài |
| Bắt buộc kernel block-sparse (`flex_attention`) | Thưa thật ở mức kernel | Không chắc chạy trên T4 |

## Quyết định
`layer_types`: cứ lớp thứ `full_attention_every` (4) là `full_attention`, các lớp khác là `linear_attention`. Mask nhân quả được thay bằng `create_sliding_window_causal_mask` với `sliding_window` = 256 (không vượt `sequence_length`). `attention_backend = "auto"`: FlashAttention-2 khi GPU từ Ampere trở lên và đã cài flash-attn, ngược lại dùng SDPA. `flex_attention` là lựa chọn tự bật trên phần cứng hỗ trợ. MoE top-k cũng làm tính toán thưa ở tầng FFN.

## Hệ quả
- Được: chạy trên T4; chi phí attention giảm ở 3/4 số lớp.
- Mất: phụ thuộc tên symbol `create_causal_mask` trong module upstream.
- Bị loại: full attention ở mọi lớp; bắt buộc `flex_attention`.
- Điều kiện xem xét lại: chuyển sang GPU Ampere trở lên, hoặc upstream tự hỗ trợ sliding window.
