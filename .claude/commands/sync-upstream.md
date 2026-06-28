---
description: Sync from upstream and merge, resolving conflicts by combining both feature sets
---

Đồng bộ từ repo upstream và merge, xử lý conflict.

## Quy trình

1. `git fetch upstream` rồi so sánh: `git log --oneline --left-right --graph HEAD...upstream/master`. Nếu không có commit mới từ upstream → báo "đã up-to-date", dừng.
2. Đảm bảo working tree sạch (`git status`). Nếu bẩn → dừng và báo user, đừng tự stash/commit.
3. `git merge upstream/master`. Nếu auto-merge xong sạch → nhảy tới bước 6.
4. Với mỗi file conflict:
   - Liệt kê các hunk: `grep -n -E '^(<<<<<<<|=======|>>>>>>>)' <file>`
   - Đọc TỪNG hunk kèm context để hiểu mỗi bên sửa gì.
   - **Nguyên tắc ưu tiên repo gốc (upstream), nhưng KHÔNG xóa tính năng của local.** Đa số conflict ở repo này là 2 bộ tính năng độc lập đụng cạnh nhau (vd local: LLM/SeedVR2/Krea/Upscale; upstream: POSE mode). Khi đó **gộp cả hai**.
   - Chỉ lấy nguyên 1 bên (ưu tiên upstream) khi hai bên sửa **đúng cùng 1 dòng / cùng mục đích** (vd biểu thức `_initKey`, danh sách append overlay, nhánh if/else trùng).
   - Khi gộp pill/mode mới: nhớ thêm vào TẤT CẢ các điểm — `_allowedPills`, mảng pill forEach trong `setPill`, `_pillPromptKey`, `persist()`, state init, `updatePillVisibility`, dropdown previewUse, validation trong `genBtn.onclick`, và workflow URL selection.
5. Sau khi xóa hết marker: `grep -n -E '^(<<<<<<<|=======|>>>>>>>)' <file>` phải không còn kết quả.
6. Validate:
   - JS: `node --check web/one_node_flux_2_klein.js`
   - Python: `python -c "import ast; ast.parse(open('nodes.py',encoding='utf-8').read())"`
   - Nếu có pill/workflow mới: `grep -n "workflow_<name>" nodes.py` và kiểm tra file `workflows/*.json` tương ứng tồn tại.
7. Nếu tất cả pass: `git add -A && git commit --no-edit` (giữ message merge mặc định).
8. Báo cáo: commit hash, các tính năng giữ từ local, tính năng thêm từ upstream, kết quả validate. **KHÔNG tự push** — hỏi user trước.

Nếu validate fail → KHÔNG commit, sửa lỗi trước, báo user nếu kẹt.
