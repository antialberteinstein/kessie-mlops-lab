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

## 2026-11-21 · thiết kế secret cho Colab CLI (tiếp #3, chuẩn bị #4)
- **Yêu cầu:** Hỏi cách xử lý secret khi chạy bằng Colab CLI. Người dùng chốt: có hai cách chạy, Colab CLI (dùng `.env`) và Colab web (dùng Colab Secrets); Docker chỉ để chạy trực tiếp trên máy có CUDA; Colab CLI cài vào uv của project.
- **Quyết định:** `google-colab-cli` cần Python ≥ 3.13 nên đặt trong project uv riêng `tools/colab-cli/` (người dùng chọn thay vì chuyển venv local sang 3.13). Token cho Colab CLI: `colab upload` file từ `.env`, notebook đọc xong thì xoá; không dùng `--env` vì token bị ghi vào history ở mọi ô (đã đọc mã nguồn 0.8.0). Bỏ `getpass`. Ghi ADR 0006; phần notebook làm ở #4.
- **Kết quả:** thêm vào PR #18.

## 2026-11-21 · đăng nhập Colab CLI và chạy thử secret (#4)
- **Yêu cầu:** Merge PR #18 rồi chạy thử upload secret trên session CPU. Shell của agent không đọc được token trong Keychain; người dùng yêu cầu bỏ việc phụ thuộc Keychain.
- **Quyết định:** Không sửa code Colab CLI. Thêm wrapper `scripts/colab`, đặt `PYTHON_KEYRING_BACKEND=keyrings.alt.file.PlaintextKeyring` (token trong file 0600). Người dùng đăng nhập lại qua wrapper. Ghi ADR 0007.
- **Kết quả chạy thử:** `colab upload f .raikiri-secrets.env` → `/.raikiri-secrets.env`; kernel đọc được và xoá được; token giả không có trong history; session đã dừng. Nhánh `feat/4-colab-cli-auth`.

## 2026-11-21 · `/kessie-skills:proj build #5`
- **Yêu cầu:** Push PR #19 rồi làm #5: cấu hình Raikiri bằng `config.json` + env, không mặc định trong code.
- **Quyết định (kế hoạch đã duyệt):**
  - `config.json` chứa đúng giá trị cũ; dataclass giữ tên nhưng bỏ mặc định; env `RAIKIRI_<MỤC>_<KHOÁ>` ghi đè.
  - Báo lỗi khi thiếu khoá, có khoá lạ hoặc sai kiểu.
  - `train.py` nhận file JSON khác; bỏ `docker_config.py`.
  - Compose dùng `compose.raikiri.env` + `${VAR:?}`; biến host đổi tên sang `RAIKIRI_HOST_*`.
- **Kết quả:** PR cho #5 (nhánh `feat/5-config-json`).

## 2026-11-21 · `/kessie-skills:proj build #15`
- **Yêu cầu:** Merge PR #20 rồi làm #15: kiểm tra đầu vào sớm và thêm test cho checkpoint, tokenizer.
- **Quyết định:**
  - `train.py` gọi `require_cuda()` sau khi nạp cấu hình, trước khi tải dữ liệu (AC-13).
  - `load_corpus` kiểm tra cột văn bản trước khi tách tập (AC-12).
  - AC-05 và AC-11 đã có code, chỉ thêm test.
- **Kết quả:** PR cho #15 (nhánh `feat/15-input-checks`).
