# Nhật ký prompt — kessie-mlops-lab

Mọi yêu cầu của người dùng đã dựng nên dự án này, theo thứ tự thời gian. Mỗi yêu cầu dẫn tới thay đổi trong repo có một mục, được ghi trong cùng PR với thay đổi đó. Chỉ thêm mục mới, không sửa hay xoá mục cũ (yêu cầu sau thay đổi yêu cầu trước thì ghi mục mới và trỏ về mục cũ).

Quy tắc:
- **Yêu cầu:** rút gọn, giữ ý định sản phẩm và các ràng buộc người dùng nêu; bỏ phần trao đổi qua lại.
- **Quyết định:** những gì người dùng đã chốt khi agent hỏi lại (phương án được chọn, phần bị loại).
- Không ghi secret, token, mật khẩu, URL môi trường thật, email hay dữ liệu cá nhân.
- Prompt giao việc cho một giai đoạn lớn vẫn nằm ở `prompts/NN-slug.txt`; mục nhật ký chỉ trỏ tới file đó.

Mẫu một mục:

```markdown
## YYYY-MM-DD · <lệnh hoặc ngữ cảnh, ví dụ `/kessie-skills:proj build #12`>
- **Yêu cầu:** <ý định của người dùng, 1–3 câu>
- **Quyết định:** <đã chốt gì; "—" nếu không có>
- **Kết quả:** <issue/PR, file prompt giai đoạn nếu có>
```

---

## 2026-11-21 · `/kessie-skills:proj` → `kickoff tiếp nhận .`
- **Yêu cầu:** Hỏi bước tiếp theo; agent đề xuất tiếp nhận repo đang có code (`kickoff tiếp nhận .`). Người dùng bổ sung: dùng uv và Colab để chạy notebook; mục đích của Raikiri là một model tiếng Việt nhỏ gọn dùng kiến trúc Mobius và sparse attention.
- **Quyết định:** Chạy notebook bằng Colab CLI (`google-colab-cli`), không dùng Colab nối runtime local. Cấu hình chuyển sang `config.json` theo quy tắc chung (env ghi đè, không mặc định trong code). PR kickoff gồm CLAUDE.md, idea brief, đặc tả, ADR 0001–0005, CI unit test, Dependabot, nhật ký prompt; phần chuyển sang uv, notebook chạy bằng Colab CLI và chuyển config được tách thành issue riêng. Loại dự án: data/pipeline huấn luyện, phát hành lên HF Hub.
- **Kết quả:** PR kickoff (nhánh `chore/kickoff-takeover`).

## 2026-11-21 · sau PR kickoff (#2)
- **Yêu cầu:** Đồng ý ("ok") với ba đề xuất sau PR kickoff: tạo issue cho phần việc đã tách, bật bảo vệ `main`, thêm skill của stack vào CLAUDE.md.
- **Quyết định:** Thêm `pytorch-patterns`, `mle-workflow`, `python-testing` vào mục "Skill bổ trợ". Issue #3 (uv), #4 (Colab CLI), #5 (`config.json`), #6 (README). Bảo vệ `main` do chủ repo tự bật.
- **Kết quả:** PR #2, issue #3–#6.

## 2026-11-21 · `/kessie-skills:proj plan`
- **Yêu cầu:** Merge PR #2, xoá nhánh local, duyệt đặc tả, lên kế hoạch milestone 0.1.0.
- **Quyết định:** Đặc tả v1 (idea brief, outline, Raikiri AC-01 → AC-16) được duyệt. Milestone 0.1.0 "Raikiri chạy đầu-cuối bằng Colab CLI": #3 → #5 → kiểm tra đầu vào → #4 → Verify T4 → #6. Bỏ issue Verify Docker (không có máy Linux có GPU); AC-15 ghi vào "Giới hạn hiện tại".
- **Kết quả:** PR duyệt đặc tả, milestone 0.1.0, issue mới cho kiểm tra đầu vào và Verify T4.

## 2026-11-21 · `/kessie-skills:proj build #3`
- **Yêu cầu:** Merge PR #17 rồi làm #3: chuyển môi trường sang uv.
- **Quyết định:** `pyproject.toml` + `uv.lock` ở gốc repo (project ảo). Trên Colab và Docker giữ torch có sẵn của runtime: cài bằng `uv export --prune torch` + `uv pip install --system`. CI chỉ cài nhóm dev. Audit thấy 6 lỗ hổng ở `transformers==5.2.0`; ghi vào `docs/SECURITY.md`, chưa nâng vì đụng ADR 0001.
- **Kết quả:** PR cho #3 (nhánh `chore/3-uv`).
