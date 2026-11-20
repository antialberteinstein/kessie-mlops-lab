# Quy trình làm việc — kessie-mlops-lab

## Nhánh và commit
- Nhánh mặc định `main` (được bảo vệ: cần PR + CI xanh).
- Nhánh theo issue: `feat/<N>-slug`, `fix/<N>-slug`; khác: `docs/…`, `ci/…`, `chore/…`.
- Conventional commits: `feat(scope): …`, `fix(scope): …`, `docs: …`, `ci: …`, `chore(deps): …`, `test: …`.

## Issue → PR
1. Mỗi việc có một issue (form Bug/Feature). Issue đủ nhỏ cho một PR.
2. Tạo nhánh, làm, chạy kiểm tra local, cập nhật CHANGELOG `[Unreleased]` nếu người dùng thấy thay đổi.
3. PR theo template. `Closes #N` chỉ khi đã xác minh; nếu còn phần cần môi trường thật → `Refs #N`.
4. CI xanh → merge (merge commit) → xoá nhánh.

## CI
- Workflow `CI`: chạy khi push `main`, PR, chạy tay, và được workflow release gọi lại.
- Gồm: unit test (`uv run --no-project --python 3.12 --with pytest pytest -q`), không cần torch hay GPU. Chưa có lint/format.
- Không chạy huấn luyện trong CI (cần GPU). AC cần runtime thật được xác minh tay trên Colab T4 hoặc Linux có GPU, và ghi vào PR.
- CI dùng cấu hình giả, không cần secret thật. Audit dependency ở chế độ cảnh báo.

## Phát hành
1. PR phiên bản: cập nhật version (chưa có; chốt khi phát hành bản đầu), đổi `[Unreleased]` → `[X.Y.Z] - YYYY-MM-DD`, cập nhật link so sánh và badge.
2. Sau merge: `git tag -a vX.Y.Z -m "…" && git push origin vX.Y.Z` trên `main`.
3. `gh release create vX.Y.Z --verify-tag [--prerelease] --notes-file notes.md` (ghi chú lấy từ CHANGELOG).
4. Công bố model lên Hugging Face Hub (hỏi trước; ghi revision commit HF vào ghi chú phát hành).
- Không di chuyển/dùng lại tag. Phát hành sai → bản patch mới. Không có build number.
