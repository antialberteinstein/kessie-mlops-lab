# Changelog

Mọi thay đổi đáng chú ý của kessie-mlops-lab được ghi tại đây. Định dạng theo [Keep a Changelog](https://keepachangelog.com/vi/1.1.0/), phiên bản theo [Semantic Versioning](https://semver.org/lang/vi/).

<!-- Nhóm dùng trong mỗi phiên bản: ### Thêm · ### Thay đổi · ### Sửa · ### Gỡ bỏ · ### Bảo mật · ### Bảo trì · ### Ghi chú nâng cấp (migration, cần build lại, cấu hình mới) -->

## [Unreleased]

### Thay đổi
- Môi trường quản lý bằng uv: `pyproject.toml` + `uv.lock` ở gốc repo thay cho `projects/raikiri/requirements.txt`. Notebook và Docker cài theo lock nhưng giữ torch CUDA có sẵn của runtime (#3).
- Colab CLI được khoá phiên bản trong project uv riêng `tools/colab-cli/` (Python 3.13); chạy bằng `uv run --project tools/colab-cli colab …` (#3, ADR 0006).
- Thêm `scripts/colab`: chạy Colab CLI của repo, lưu token OAuth trong file 0600 thay vì macOS Keychain (#4, ADR 0007).

### Bảo trì
- Thêm nền quy trình: CLAUDE.md, idea brief, đặc tả, ADR 0001–0005, CI chạy unit test bằng uv, Dependabot, nhật ký prompt.

[Unreleased]: https://github.com/antialberteinstein/kessie-mlops-lab/commits/main
