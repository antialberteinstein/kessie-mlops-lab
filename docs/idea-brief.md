# Idea brief — kessie-mlops-lab / Raikiri

**Ngày:** 2026-11-21 · **Người quyết định:** chủ repo · **Trạng thái:** Đã duyệt 2026-11-21

> Ghi lại hồi tố khi tiếp nhận repo đang có code. Phần đã chốt trong hội thoại được đánh dấu "(đã chốt)".

## Vấn đề
Một người cần một phòng thí nghiệm LLMOps nhỏ để thử kiến trúc LLM mới, huấn luyện lại được và công bố model. Thí nghiệm đầu tiên là **Raikiri**: một mô hình ngôn ngữ tiếng Việt nhỏ gọn dùng kiến trúc **Mobius** (Shanghai AI Lab, công bố tại WAIC 2026; tách bộ nhớ tri thức khỏi suy luận) và **sparse attention** (đã chốt). Hiện tại việc huấn luyện chạy qua notebook Colab trên web hoặc qua Docker Compose; môi trường cài bằng `pip`.

## Người dùng đích
- Chủ repo, một người, tự huấn luyện và đánh giá. Không có dữ liệu người dùng cuối.
- Người tải model đã công bố trên Hugging Face Hub để thử sinh văn bản tiếng Việt.

## Phạm vi v1
1. Huấn luyện Raikiri từ đầu trên **một GPU T4** (Colab), chạy từ terminal bằng **Colab CLI** (đã chốt).
2. Môi trường tái lập bằng **uv** (đã chốt); cấu hình đọc từ **`config.json`**, biến môi trường ghi đè, không có giá trị mặc định trong code (đã chốt).
3. Theo dõi huấn luyện bằng TensorBoard; ghi `eval_loss` và các chỉ số vào `training_metrics.json`.
4. Sinh văn bản tiếng Việt mẫu từ checkpoint cuối.
5. Công bố model, tokenizer, model card và mẫu sinh lên Hugging Face Hub.

## Ngoài phạm vi v1
- Tự cài đặt lại kiến trúc Mobius (dùng remote code chính chủ, xem ADR 0001).
- Instruction tuning, chat, RLHF.
- API phục vụ suy luận, quantization, triển khai production.
- Huấn luyện đa GPU hoặc phân tán.
- Benchmark tiếng Việt ngoài `eval_loss` / perplexity.
- Thí nghiệm thứ hai trong lab.

## Ràng buộc
- Loại dự án: **G. Data / pipeline huấn luyện**, phát hành artifact lên Hugging Face Hub.
- Phần cứng: Colab T4 (16 GB, Turing: không FlashAttention-2, dùng fp16). Máy phát triển là macOS arm64, không có CUDA: chỉ chạy test, không huấn luyện.
- Dữ liệu nhạy cảm: không có dữ liệu cá nhân. Secret duy nhất là `HF_TOKEN` (quyền ghi).
- Ngôn ngữ: tài liệu tiếng Việt; model và dữ liệu tiếng Việt.
- Ngân sách: compute unit Colab (`colab usage` để xem); chưa đặt trần.

## Thước đo thành công
- Một lệnh Colab CLI huấn luyện xong cấu hình mặc định trên T4 mà không phải mở trình duyệt, và model xuất hiện trên Hugging Face Hub kèm model card.
- Ngưỡng chất lượng: xem câu hỏi còn mở.

## Câu hỏi còn mở
- Ngưỡng `eval_loss` hoặc perplexity nào thì coi là đạt cho v1?
- Trần compute unit cho mỗi lần huấn luyện?
- Repo Hugging Face để public (như notebook hiện tại) hay private?
