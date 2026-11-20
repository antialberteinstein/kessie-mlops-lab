# 0001. Dùng remote code Intern-S2-Mobius chính chủ, ghim revision, kèm adapter

- Trạng thái: Chấp nhận (ghi lại hồi tố từ code hiện có)
- Ngày: 2026-11-21 · Người quyết định: chủ repo

## Bối cảnh
Raikiri cần kiến trúc Mobius (Shanghai AI Lab, WAIC 2026): tách bộ nhớ tri thức (Memory Decoder, kho vector tri thức dùng chung giữa các lớp) khỏi suy luận (Mobius Module, toán tử suy luận theo nhu cầu). Tài liệu công khai, ví dụ mục Baidu Baike, chỉ mô tả ở mức khái quát: không có công thức, siêu tham số hay code. Code tham chiếu duy nhất là remote code Transformers ở `internlm/Intern-S2-Mobius`.

## Các phương án
| Phương án | Ưu | Nhược | Chi phí / khoá nhà cung cấp |
|---|---|---|---|
| Remote code chính chủ, ghim revision, thu nhỏ cấu hình | Đúng kiến trúc gốc; ít code | Chạy code từ Hub (`trust_remote_code`); class CausalLM upstream thiếu `forward()` | Phụ thuộc repo HF và `transformers==5.2.0` |
| Tự cài lại Mobius từ mô tả | Toàn quyền kiểm soát | Không có đặc tả đủ chi tiết; dễ sai kiến trúc | Nhiều công |
| Dùng kiến trúc Transformer/MoE phổ biến | Ổn định | Không phải Mobius, sai mục tiêu | — |

## Quyết định
Dùng `AutoConfig` / `AutoModelForCausalLM` với `trust_remote_code=True`, `revision` và `code_revision` cùng ghim `1b23c974ac860b182c61732299ae4fc432a8cf54`, rồi ghi đè cấu hình text thành bản nhỏ: hidden 384, 8 lớp, 6 head (2 KV head), 2 memory block, 32 expert chọn top-2. `model.py` gắn một `forward()` tương thích, tính cả loss cân bằng router, vì revision này không có hàm đó.

## Hệ quả
- Được: giữ đúng shared routed experts (tri thức) và token mixer từng lớp (suy luận) của Mobius.
- Mất: phải tin code ở revision đã ghim; nâng revision hoặc `transformers` có thể làm hỏng adapter.
- Bị loại: tự cài lại Mobius từ mô tả công khai; dùng kiến trúc không phải Mobius.
- Điều kiện xem xét lại: upstream phát hành `forward()` chính thức, hoặc Shanghai AI Lab công bố báo cáo kỹ thuật kèm code tham chiếu khác.
