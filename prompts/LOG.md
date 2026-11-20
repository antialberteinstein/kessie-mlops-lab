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
