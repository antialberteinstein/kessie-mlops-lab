# 0003. Huấn luyện bằng Hugging Face Trainer; Docker Compose cho máy Linux có GPU

- Trạng thái: Chấp nhận (ghi lại hồi tố từ code hiện có)
- Ngày: 2026-11-21 · Người quyết định: chủ repo

## Bối cảnh
Cần một vòng lặp huấn luyện ít code, có checkpoint, eval và log TensorBoard, chạy được cả trên Colab lẫn máy Linux có GPU NVIDIA.

## Quyết định
- `train.py` dùng `transformers.Trainer` + Accelerate, `report_to="tensorboard"`, fp16 và gradient checkpointing. Tokenizer BPE byte-level 16k được huấn luyện từ corpus rồi dùng lại nếu đã có `tokenizer.json`.
- Dữ liệu: Hugging Face Datasets ở chế độ streaming, lấy `max_samples` dòng đầu, rồi tokenize và đóng gói thành đoạn `sequence_length` token.
- Kết quả cuối ghi vào `training_metrics.json`; log TensorBoard đặt ở `<output_dir>/../tensorboard`.
- `compose.raikiri.yaml`: service `train` (GPU) và `tensorboard` dùng chung image `projects/raikiri/Dockerfile`; dataset mount chỉ đọc, artifact mount có quyền ghi.
- Model cuối được công bố lên Hugging Face Hub dưới `<username>/raikiri` (hiện để public) kèm model card và mẫu sinh.

## Hệ quả
- Được: ít code tự viết; một đường chạy chung cho Colab và Docker.
- Mất: phụ thuộc hành vi của Trainer ở `transformers==5.2.0` (ví dụ đọc `TENSORBOARD_LOGGING_DIR` từ môi trường).
- Điều kiện xem xét lại: cần huấn luyện đa GPU, hoặc vòng lặp tuỳ biến mà Trainer không hỗ trợ.
