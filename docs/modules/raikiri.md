# Raikiri — Module breakdown

> Trạng thái: **Đã duyệt 2026-11-21.** Đặc tả cuối cùng vẫn là `docs/RequirementsOutline.md` §3.

## 1. Khả năng cần đạt
- Huấn luyện Raikiri từ đầu trên một GPU T4 với cấu hình trong `projects/raikiri/config.json`.
- Chạy toàn bộ notebook trên Colab từ terminal bằng Colab CLI, không mở trình duyệt.
- Xem tiến trình và kết quả trên TensorBoard; có `training_metrics.json` chứa `eval_loss`.
- Sinh văn bản tiếng Việt từ checkpoint cuối.
- Công bố model, tokenizer, model card và mẫu sinh lên Hugging Face Hub.
- Chạy cùng quy trình huấn luyện bằng Docker Compose trên máy Linux có GPU.

## 2. Người dùng và giao diện
- Terminal: `uv run …`, `colab …`, `docker compose …`. Mỗi giai đoạn in `[Raikiri] <giai đoạn>...` và `done in Ns` hoặc `failed after Ns`.
- TensorBoard: scalar loss train/eval, tab Text chứa mẫu sinh.

## 3. Luồng
### 3.1. Huấn luyện trên Colab (đường chính)
1. `colab new -s raikiri --gpu T4`.
2. `colab exec -s raikiri -f notebooks/train-raikiri.ipynb`: notebook clone repo, cài dependency, kiểm tra CUDA, huấn luyện, mở TensorBoard, sinh mẫu, công bố.
3. `colab download` các artifact cần giữ, rồi `colab stop -s raikiri`.
### 3.2. Huấn luyện bằng Docker
`docker compose -f compose.raikiri.yaml up --build -d`; dataset mount chỉ đọc, artifact mount ra host.
### 3.3. Chạy lại
Tokenizer đã có (`tokenizer.json`) thì dùng lại, không huấn luyện lại.

## 4. Quy tắc cố định
- `hidden_size = num_attention_heads × head_dim`; `sliding_window ≤ sequence_length`. Vi phạm thì báo lỗi trước khi dựng model.
- Kiến trúc lấy từ `internlm/Intern-S2-Mobius` ở revision đã ghim; không tải code ở revision khác.
- Chỉ tải lên Hub các file ở thư mục model cuối, không tải checkpoint trung gian.
- Lấy `max_samples` dòng đầu bằng streaming, không tải toàn bộ split.

## 5. Hợp đồng dữ liệu
| Artifact | Nội dung | Ràng buộc |
|---|---|---|
| `checkpoints/model.safetensors` | trọng số model cuối | `lm_head` dùng chung trọng số với embedding |
| `checkpoints/training_metrics.json` | `last_logged_train_loss`, `last_logged_step`, `average_train_loss`, `eval_loss`, `global_step` | luôn có `eval_loss` |
| `tokenizer/tokenizer.json` | BPE byte-level, special token `<unk> <pad> <s> </s>` | dùng lại khi chạy lại |
| `checkpoints/sample_generations.md`, `README.md` | mẫu sinh, model card | được tải lên Hub |

- Không đổi schema dữ liệu. Thay đổi cấu hình theo ADR 0005.

## 6. Nâng cấp và giới hạn
- Checkpoint cũ chỉ nạp lại được với đúng revision upstream và đúng cấu hình model đã dùng khi huấn luyện.
- Chưa có benchmark ngoài `eval_loss`.

## 7. Tiêu chí nghiệm thu
| Mã | Tình huống | Kết quả |
|---|---|---|
| AC-01 | Chạy unit test trên máy không có GPU và không cài torch | Tất cả đạt; CI chạy cùng lệnh |
| AC-02 | Huấn luyện cấu hình mặc định trên T4 | Kết thúc không lỗi; có `model.safetensors`, tokenizer, `training_metrics.json` chứa `eval_loss` (cần runtime thật) |
| AC-03 | Mở TensorBoard sau khi huấn luyện | Có scalar loss train và eval, tab Text có mẫu sinh (cần runtime thật) |
| AC-04 | Nạp checkpoint cuối và sinh từ 3 prompt tiếng Việt | Ra 3 đoạn văn bản, ghi vào `sample_generations.md` (cần runtime thật) |
| AC-05 | Checkpoint thiếu hoặc lệch khoá | Dừng với thông báo nêu khoá thiếu hoặc thừa; không nạp một phần |
| AC-06 | `colab exec -f notebooks/train-raikiri.ipynb` trên session T4 | Chạy hết notebook không cần thao tác tay (cần runtime thật) |
| AC-07 | Công bố khi không có `HF_TOKEN` trong lúc chạy không tương tác | Dừng với thông báo rõ, không treo chờ nhập; không tạo repo rỗng |
| AC-08 | Thiếu một khoá bắt buộc ở cả env lẫn `config.json` | Dừng khi khởi động; thông báo có màu nêu tên khoá và file chứa nó; không in stack trace; mã thoát khác 0 |
| AC-09 | Đặt biến môi trường cho một khoá đã có trong `config.json` | Giá trị từ env được dùng |
| AC-10 | Tìm giá trị mặc định trong code nạp cấu hình | Không còn giá trị mặc định hay fallback |
| AC-11 | Chạy lại khi đã có `tokenizer.json` | Dùng lại tokenizer, không huấn luyện lại |
| AC-12 | Cột văn bản không tồn tại trong dataset | Dừng với thông báo nêu tên cột |
| AC-13 | Chạy huấn luyện trên runtime không có CUDA | Dừng trước khi huấn luyện, thông báo cần GPU |
| AC-14 | Xem log và notebook output sau khi công bố | Không có `HF_TOKEN` hay giá trị secret nào |
| AC-15 | `docker compose … up` trên máy Linux có GPU | Huấn luyện xong; artifact nằm trên host; TensorBoard mở được ở cổng đã cấu hình (cần máy thật) |
| AC-16 | `hidden_size ≠ heads × head_dim` hoặc `sliding_window > sequence_length` | Báo lỗi trước khi dựng model |

## 8. Bàn giao
- Code kèm unit test (không cần GPU), cập nhật README và CHANGELOG.
- Báo cáo nêu rõ AC nào đã xác minh trên T4 hoặc máy Linux thật, AC nào chưa.
- Đã xác minh khi tiếp nhận (2026-11-21): AC-01 (8 test đạt bằng `uv run --no-project --with pytest pytest`). Các AC còn lại chưa xác minh.
