# 0005. Cấu hình: `config.json` + biến môi trường ghi đè, không có giá trị mặc định trong code

- Trạng thái: Chấp nhận
- Ngày: 2026-11-21 · Người quyết định: chủ repo

## Bối cảnh
Cấu hình hiện có giá trị mặc định nằm trong code ở ba chỗ: dataclass trong `projects/raikiri/config.py`, `os.environ.get(..., default)` trong `docker_config.py`, và `${VAR:-default}` trong `compose.raikiri.yaml`. `train.py` còn nhận một file cấu hình Python tuỳ ý rồi thực thi nó. Cách này trái với quy tắc cấu hình chung của chủ repo.

## Các phương án
| Phương án | Ưu | Nhược |
|---|---|---|
| **`config.json` + env ghi đè, code chỉ đọc** | Một nguồn sự thật; không thực thi file cấu hình; khớp quy tắc chung | Phải viết lại phần nạp cấu hình và test |
| Giữ dataclass `config.py` (ghi thành ngoại lệ) | Không phải đổi gì | Giá trị mặc định rải trong code; thực thi file Python tuỳ ý |

## Quyết định
- `projects/raikiri/config.json` chứa **toàn bộ** cấu hình không nhạy cảm (data, model, train, đường dẫn Docker). File luôn có trong working tree.
- Biến môi trường ghi đè khi được đặt. Quy ước tên, ví dụ `RAIKIRI_DATA_MAX_SAMPLES`, được chốt trong issue triển khai.
- `.env` chỉ chứa secret (`HF_TOKEN`); mẫu ở `.env.example`.
- Thiếu một khoá bắt buộc ở cả env lẫn `config.json` thì dừng ngay khi khởi động với thông báo ngắn, có màu, nêu tên khoá và file chứa nó, không in stack trace.
- Code không có giá trị mặc định hay fallback. Bỏ cơ chế thực thi file cấu hình Python; muốn chạy một cấu hình khác thì truyền một file JSON khác.

## Hệ quả
- Được: cấu hình kiểm tra được, không còn chỗ thực thi code tuỳ ý.
- Việc phải làm (issue riêng): nạp cấu hình, sửa `train.py`, `generate.py`, `docker_config.py`, compose, notebook, test, README.
- Bị loại: giữ dataclass có giá trị mặc định; giữ file cấu hình dạng Python.
- Điều kiện xem xét lại: cấu hình cần logic tính toán mà JSON không biểu diễn được.
