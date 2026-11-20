# kessie-mlops-lab — Requirements Outline

> Trạng thái: **Nháp, chờ duyệt** trong PR kickoff. Đây là nguồn sự thật về hành vi; agent đề xuất, người dùng duyệt. Khi prompt, module breakdown hay issue mâu thuẫn với file này, file này thắng. Cập nhật lần cuối: 2026-11-21.

## 1. Mục tiêu và phạm vi
- Người dùng: chủ repo (một người), cùng người tải model từ Hugging Face Hub.
- Vấn đề: cần một lab nhỏ để huấn luyện, đánh giá và công bố LLM thử nghiệm. Tóm tắt ở `docs/idea-brief.md`.
- Loại dự án: **G. Data / pipeline huấn luyện**, phát hành artifact lên Hugging Face Hub.
- Nền tảng chạy: runtime Colab T4 (điều khiển bằng Colab CLI), máy Linux có GPU NVIDIA (Docker Compose). Máy macOS chỉ dùng để phát triển và chạy test.
- Trong phạm vi v1: một module, **Raikiri** (§3).
- Ngoài phạm vi v1: xem `docs/idea-brief.md` mục "Ngoài phạm vi v1".

## 2. Giao diện dòng lệnh và notebook
- `train.py`: huấn luyện từ cấu hình trong `config.json` (ADR 0005).
- `generate.py`: sinh văn bản từ checkpoint đã lưu.
- `notebooks/train-raikiri.ipynb`: luồng đầy đủ trên Colab (cài đặt → huấn luyện → TensorBoard → sinh mẫu → công bố), chạy bằng `colab exec` (ADR 0004).
- `compose.raikiri.yaml`: service `train` và `tensorboard`.
- Thông báo trên terminal bằng tiếng Anh, có tiền tố `[Raikiri]`; tài liệu viết bằng tiếng Việt.

## 3. Module: Raikiri
Model ngôn ngữ tiếng Việt nhỏ gọn dùng kiến trúc Mobius và sparse attention (ADR 0001, 0002).
### 3.1. Dữ liệu và tokenizer
Dataset Hugging Face hoặc thư mục local; giới hạn số dòng; tách tập validation; tokenizer BPE byte-level huấn luyện một lần rồi dùng lại.
### 3.2. Huấn luyện và đánh giá
Huấn luyện trên một GPU; log TensorBoard; ghi `training_metrics.json`.
### 3.3. Sinh văn bản và công bố
Sinh mẫu tiếng Việt; tạo model card; tải lên Hugging Face Hub.
### 3.4. Cấu hình và môi trường
`config.json` + env ghi đè; uv; Colab CLI.

Chi tiết luồng và tiêu chí nghiệm thu: `docs/modules/raikiri.md`.

## 4. Tài khoản và secret
- Không có tài khoản người dùng. Secret duy nhất là `HF_TOKEN` (quyền ghi): lưu trong `.env` khi chạy local, hoặc trong Colab Secrets khi chạy trên Colab. Không bao giờ ghi token vào log, notebook output hay git.

## 5. Dữ liệu và quyền
- Không có dữ liệu cá nhân. Dataset và artifact (`/dataset/`, `/artifacts/`) bị gitignore và không commit.
- Repo model trên Hugging Face hiện để public (câu hỏi còn mở trong idea brief).

## 6. Chất lượng và nghiệm thu
- Unit test không cần GPU hay torch, chạy trong CI.
- Huấn luyện thật phải được xác minh trên runtime T4, Docker phải được xác minh trên máy Linux có GPU, trước khi đóng issue liên quan. Bảng AC ở `docs/modules/raikiri.md`.

## 7. Giới hạn hiện tại
- Chỉ có `eval_loss`, chưa có benchmark tiếng Việt.
- Phải tin remote code của upstream ở revision đã ghim.
- Chưa có ngưỡng chất lượng hay trần compute unit.

## Lịch sử quyết định

| Ngày | Quyết định | Lý do | Ảnh hưởng (AC, dữ liệu cũ) |
|---|---|---|---|
| 2026-11-21 | Khởi tạo đặc tả khi tiếp nhận repo | Repo đã có code nhưng chưa có đặc tả | — |
| 2026-11-21 | Chạy notebook bằng Colab CLI; môi trường dùng uv | Chủ repo chốt | AC-06, AC-07 |
| 2026-11-21 | Cấu hình bằng `config.json` + env, không mặc định trong code | Chủ repo chốt, theo quy tắc chung | AC-08 → AC-10 |
