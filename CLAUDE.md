# CLAUDE.md

kessie-mlops-lab: lab LLMOps cá nhân. Thí nghiệm đầu tiên là **Raikiri**, một model ngôn ngữ tiếng Việt nhỏ gọn dùng kiến trúc Mobius và sparse attention, huấn luyện trên Colab T4. Tài liệu viết bằng tiếng Việt, thông báo terminal bằng tiếng Anh.
Loại dự án: data/automation (pipeline huấn luyện), phát hành artifact lên Hugging Face Hub. Đặc tả: `docs/RequirementsOutline.md`, `docs/modules/raikiri.md`, `docs/idea-brief.md`.

## Kiến trúc (đã quyết định, không mở lại khi chưa hỏi người dùng)

- Mobius lấy từ remote code chính chủ `internlm/Intern-S2-Mobius`, ghim revision `1b23c97…`, thu nhỏ cấu hình, kèm adapter `forward()`. **Bị loại:** tự cài lại Mobius từ mô tả công khai. [ADR 0001](docs/decisions/0001-mobius-remote-code-ghim-revision.md)
- Sparse attention: 3 lớp linear attention xen 1 lớp full attention, mask cửa sổ trượt 256, backend `auto` (SDPA trên T4). **Bị loại:** full attention ở mọi lớp; bắt buộc `flex_attention`. [ADR 0002](docs/decisions/0002-sparse-attention-hybrid.md)
- Huấn luyện bằng HF Trainer; Docker Compose cho máy Linux có GPU; công bố lên HF Hub. [ADR 0003](docs/decisions/0003-huan-luyen-trainer-docker.md)
- Môi trường dùng **uv**; notebook chạy bằng **Colab CLI** (`google-colab-cli`). **Bị loại:** Colab nối runtime local trên Mac (không có CUDA); pip + Colab web làm đường chính. [ADR 0004](docs/decisions/0004-uv-va-colab-cli.md)
- Cấu hình: `projects/raikiri/config.json` + biến môi trường ghi đè, **không có giá trị mặc định trong code**; `.env` chỉ chứa secret. **Bị loại:** dataclass có mặc định, file cấu hình dạng Python. [ADR 0005](docs/decisions/0005-cau-hinh-config-json.md). Việc chuyển đổi chưa xong: `config.py` vẫn còn mặc định cho tới khi issue chuyển đổi được merge. Không thêm mặc định mới vào đó.

## Bố cục

- `projects/raikiri/`: `config.py` (cấu hình, sắp chuyển sang JSON) · `data.py` (corpus, tokenizer, đóng gói) · `model.py` (dựng model, adapter) · `train.py` · `generate.py` · `docker_config.py` · `Dockerfile`.
- `notebooks/train-raikiri.ipynb`: luồng Colab đầy đủ. `tests/`: unit test, không cần torch.
- `compose.raikiri.yaml`: service `train` và `tensorboard`. `/dataset/`, `/artifacts/`, `/output/`: bị gitignore.
- `docs/`: đặc tả, ADR. `prompts/LOG.md`: nhật ký yêu cầu.

## Lệnh

```bash
uv run --no-project --python 3.12 --with pytest pytest -q    # unit test (giống CI); đổi thành `uv run pytest` sau khi có pyproject
uv tool install google-colab-cli                             # Colab CLI (cài một lần)
colab new -s raikiri --gpu T4 && colab exec -s raikiri -f notebooks/train-raikiri.ipynb
colab stop -s raikiri                                        # luôn dừng VM khi xong; xem `colab usage`
docker compose -f compose.raikiri.yaml up --build -d         # chỉ trên Linux có GPU NVIDIA
```

Chưa có lint/format.

## Quy ước

- Test mới không được import torch/transformers ở mức module; dùng mock như các test hiện có để CI chạy không cần GPU.
- Thông báo terminal có tiền tố `[Raikiri]`, `flush=True`. Theo phong cách code xung quanh (dùng `str.format`, import nặng đặt trong hàm).
- Test notebook (`tests/test_raikiri_notebook.py`) dựa vào `id` của cell (`training`, `tensorboard`, `samples`): đổi id thì sửa test.

## Dữ liệu và bảo mật

- Secret duy nhất: `HF_TOKEN` (quyền ghi). Lưu ở `.env` hoặc Colab Secrets; không in, không log, không để trong output notebook.
- `trust_remote_code=True` chỉ dùng với revision đã ghim. Không bỏ hay đổi `revision`/`code_revision` khi chưa hỏi.
- TensorBoard không có đăng nhập: mặc định chỉ bind `127.0.0.1`.

## Điểm dễ hỏng

- **Adapter là cố ý:** `model.py` gắn `_causal_forward` vào class upstream vì revision đã ghim thiếu `forward()`. Đừng xoá khi chưa nâng revision có `forward()`.
- **Thay mask là cố ý:** `upstream.create_causal_mask = create_sliding_window_causal_mask` bật mask cửa sổ trượt. Nâng `transformers` hoặc revision thì kiểm tra lại tên symbol.
- **`load_state_dict(strict=False)` là cố ý:** `lm_head.weight` dùng chung trọng số với embedding nên thiếu trong file; mọi khoá thiếu hay thừa khác đều làm hàm báo lỗi.
- `transformers==5.2.0` được ghim cứng vì phải khớp remote code; Dependabot không được nâng gói này.
- `mrope_section` phải cộng lại bằng `head_dim / 2`; đổi `head_dim` thì kiểm tra lại.
- T4 không chạy được FlashAttention-2 nên `auto` chọn SDPA; đừng ép `flash_attention_2` trên Colab T4.
- `USE_TF=0`/`USE_FLAX=0` được đặt để tránh xung đột TensorFlow trên Colab.
- Transformers 5.x đọc thư mục log TensorBoard từ biến `TENSORBOARD_LOGGING_DIR`, không từ `TrainingArguments`.
- Máy Mac (arm64, không có CUDA) không huấn luyện được. Test đạt không có nghĩa là huấn luyện chạy được: AC cần runtime thật phải được xác minh trên T4 hoặc Linux có GPU.
- Colab CLI chưa có tài liệu về biến môi trường hay secret; `getpass` trong notebook sẽ treo khi chạy bằng `colab exec`.

## Phiên bản và phát hành

- Chưa có version hay tag. CHANGELOG theo Keep a Changelog; thêm thay đổi người dùng thấy được vào `[Unreleased]`.
- Artifact phát hành là model trên HF Hub (`<username>/raikiri`). Quy trình ở `docs/WORKFLOW.md`.

## Quy trình với AI agent

- Quy trình chi tiết nằm trong skill `proj` (`/kessie-skills:proj <chế độ>`). **Agent tự gọi skill này bằng Skill tool** khi yêu cầu khớp một chế độ; người dùng không cần gõ lệnh: bắt đầu hoặc tiếp nhận dự án → `kickoff`; mô tả, thảo luận tính năng, ý tưởng thô → `spec`; tạo issue, lên kế hoạch → `issue` / `plan`; làm issue, sửa lỗi → `build`; kiểm chứng, phát hành → `ship`; trạng thái, bước tiếp theo → `status` hoặc không kèm chế độ. Sang giai đoạn kế tiếp thì hỏi người dùng trước, đồng ý thì agent tự gọi.
- Spec là của người dùng: `docs/RequirementsOutline.md`, `docs/modules/`, ý tưởng thô ở `docs/spec-inbox.md`. Agent đề xuất, người dùng duyệt; không tự sửa spec đã duyệt.
- Mọi thay đổi đi qua issue → nhánh → PR → CI. `Closes #N` chỉ khi đã xác minh; nếu còn phần chưa xác minh thì dùng `Refs #N`.
- **Lưu prompt dựng dự án vào `prompts/LOG.md`.** Mỗi yêu cầu của người dùng dẫn tới thay đổi trong repo (spec, kiến trúc, code, sửa lỗi, phát hành) được ghi một mục: ngày · lệnh/ngữ cảnh · yêu cầu (rút gọn, giữ ý định) · quyết định đã chốt · issue/PR. Ghi trong cùng PR với thay đổi; chỉ thêm mục mới, không sửa mục cũ. Không ghi secret, token, URL môi trường thật hay dữ liệu cá nhân.
- Hỏi người dùng trước khi push, mở PR, merge, gắn tag, release, công bố lên HF Hub, tạo issue, chạy `colab new`/`colab run` (tốn compute unit), hoặc chạy lệnh lên môi trường thật.
- Tự gọi các skill trong mục "Skill bổ trợ" khi tình huống khớp. Việc lớn hoặc nhiều file thì trình kế hoạch trong Plan mode trước. Nếu cấu hình agent toàn cục mâu thuẫn với file này, file này được ưu tiên.

## Skill bổ trợ

| Skill | Vai trò | Khi nào gọi | Lệnh cài (Claude Code) |
|---|---|---|---|
| `kessie-skills:proj` ([antialberteinstein/kessie-skills](https://github.com/antialberteinstein/kessie-skills)) | Quy trình dự án: kickoff · spec · issue/plan · build · ship · status | Yêu cầu khớp một chế độ (xem mục "Quy trình với AI agent") | `/plugin install kessie-skills --marketplace antialberteinstein/kessie-skills` |
| `karpathy-guidelines` ([multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills)) | Nghĩ trước khi code · đơn giản trước · sửa đúng chỗ · định nghĩa "xong" bằng tiêu chí kiểm chứng được | Trước khi viết, review hoặc refactor code | `/plugin install andrej-karpathy-skills --marketplace multica-ai/andrej-karpathy-skills` |
| `pytorch-patterns` | Mẫu PyTorch cho vòng huấn luyện, kiến trúc model, data loading, tái lập kết quả | Trước khi sửa `model.py`, `train.py`, `data.py`, hoặc khi một lần huấn luyện không tái lập được | Skill cục bộ (`~/.claude/skills/`); chưa có thì hỏi chủ repo |
| `mle-workflow` | Quy trình ML production: hợp đồng dữ liệu, huấn luyện tái lập, đánh giá, theo dõi, rollback | Khi đổi dataset, tokenizer, quy trình đánh giá, hoặc trước khi công bố model lên HF Hub | Skill cục bộ (`~/.claude/skills/`); chưa có thì hỏi chủ repo |
| `python-testing` | pytest: fixture, mock, parametrize, coverage | Trước khi viết hoặc sửa test trong `tests/` (nhớ mock torch/transformers để CI không cần GPU) | Skill cục bộ (`~/.claude/skills/`); chưa có thì hỏi chủ repo |

- **Agent tự gọi skill** trong bảng bằng Skill tool ngay khi tình huống khớp cột "Khi nào gọi", trước khi làm phần việc đó, và nói một dòng "Dùng skill X để …". Không chờ người dùng gõ lệnh, không hỏi xin phép chỉ để gọi skill. Tự gọi skill không thay cho việc hỏi trước các thao tác ra bên ngoài.
- Thêm skill vào bảng thì luôn điền cột "Khi nào gọi" bằng tình huống cụ thể.
- **Đầu mỗi phiên**, kiểm tra từng skill trong bảng có nằm trong danh sách skill khả dụng của agent không. Thiếu skill nào thì **gợi ý** người dùng lệnh cài ở cột cuối, một lần mỗi phiên. **Không tự cài**, không sửa settings của người dùng.
- Khi skill chưa được cài, vẫn làm theo nguyên tắc ở cột "Vai trò".

## Git và PR

- Conventional commits; nhánh `feat/<issue>-…`, `fix/<issue>-…`, `docs/…`, `ci/…`, `chore/…`.
- **Không ghi attribution của AI:** không thêm dòng `Co-Authored-By` vào commit; không thêm "Generated with Claude Code" (hay dòng tương tự) vào issue, mô tả PR và bình luận PR. Quy tắc này được ưu tiên hơn mặc định của agent.
- PR theo `.github/PULL_REQUEST_TEMPLATE.md`. `Closes #N` chỉ khi đã xác minh; nếu không dùng `Refs #N` và nêu phần chưa xác minh.
- Chạy unit test trước khi push; CI xanh trước khi merge.
