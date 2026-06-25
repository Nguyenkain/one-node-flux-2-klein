# Plan: Thêm Tab LLM cho Vision-LLM Image Description

## Tổng quan
Thêm tab LLM thứ 6 vào giao diện One Node FLUX.2 [klein] để mô tả hình ảnh bằng local LLM model (llama.cpp với vision support).

## Kiến trúc hiện tại
- **Frontend**: `web/one_node_flux_2_klein.js` (509KB+)
- **Backend**: `nodes.py` với web routes `/api/one-node-flux-klein/*`
- **Tabs hiện tại**: T2I, I2I, EDIT, PAINT, FACESWAP
- **Tab switching**: biến `activePill`, function `setPill()`
- **Models folder**: `ComfyUI/models/LLM/` (đã tồn tại)
- **Prompts folder**: `ComfyUI/models/LLM/prompts/` (đã có `LLM-system.txt`)

## Các thay đổi cần thực hiện

### 1. Frontend (`web/one_node_flux_2_klein.js`)

#### 1.1 Tab button
**Vị trí**: Dòng ~1292-1297
```javascript
const pillLLM = Pill("LLM", activePill==="llm", ()=>setPill("llm"));
topBarLeft.append(pillT2I, pillI2I, pillEdit, pillInpaint, pillFaceswap, pillLLM);
```

#### 1.2 State management
**Thêm vào localStorage state `S`**:
```javascript
S.llmModel       // tên file .gguf model
S.llmMmproj      // tên file .gguf mmproj (multimodal projector)
S.llmSystemPromptFile // tên file .txt trong prompts/
S.llmImage       // tên file ảnh đầu vào
S.llmUserPrompt  // câu hỏi/prompt từ user (nếu cần)
S.llmResult      // kết quả description từ LLM
```

#### 1.3 Panel UI (dòng ~5654+ sau FACESWAP panel)
```
┌─ LLM Panel ──────────────────────────────────┐
│ ┌─────────────────────────┐                  │
│ │  Image slot (upload)    │                  │
│ │  (giống i2i/edit slots) │                  │
│ └─────────────────────────┘                  │
│                                               │
│ User Prompt (optional textarea):             │
│ ┌───────────────────────────────────────┐    │
│ │ "Describe this image in detail..."   │    │
│ └───────────────────────────────────────┘    │
│                                               │
│ [Analyze Image] button (lime, like Generate) │
│                                               │
│ Results:                                      │
│ ┌───────────────────────────────────────┐    │
│ │ (description text từ LLM)             │    │
│ └───────────────────────────────────────┘    │
└───────────────────────────────────────────────┘
```

#### 1.4 Settings section
**Thêm vào Settings modal** (dòng ~6000+):
```
┌─ LLM Settings ────────────────────────┐
│ Model (dropdown):                     │
│   [*.gguf files in models/LLM/]       │
│                                        │
│ MMProj (dropdown):                    │
│   [*.gguf files in models/LLM/]       │
│                                        │
│ System Prompt (dropdown):             │
│   [*.txt files in models/LLM/prompts/]│
└────────────────────────────────────────┘
```

#### 1.5 Visibility logic
**Cập nhật `_updateUI()` hoặc tương đương**:
```javascript
llmPanel.style.display = activePill === "llm" ? "flex" : "none";
```

### 2. Backend (`nodes.py`)

#### 2.1 Scan endpoints (giống pattern hiện tại)
```python
@PromptServer.instance.routes.get("/api/one-node-flux-klein/llm-models")
async def get_llm_models(request):
    """Scan models/LLM/*.gguf"""
    
@PromptServer.instance.routes.get("/api/one-node-flux-klein/llm-mmprojs")
async def get_llm_mmprojs(request):
    """Scan models/LLM/*mmproj*.gguf hoặc *vision*.gguf"""
    
@PromptServer.instance.routes.get("/api/one-node-flux-klein/llm-prompts")
async def get_llm_prompts(request):
    """Scan models/LLM/prompts/*.txt"""
```

#### 2.2 Workflow execution endpoint
```python
@PromptServer.instance.routes.post("/api/one-node-flux-klein/llm-analyze")
async def llm_analyze(request):
    """
    Request body:
    {
      "image": "filename.png",
      "user_prompt": "Describe this image..."  # optional
    }
    
    Response (streaming hoặc polling):
    {
      "prompt_id": "uuid",
      "status": "queued" | "running" | "completed",
      "result": "description text..."  # khi completed
    }
    """
    # 1. Load workflow template từ llm_workflow.json
    # 2. Patch nodes với settings từ config.json:
    #    - S.llmModel -> node llm_vision.model
    #    - S.llmMmproj -> node llm_vision.mmproj
    #    - S.llmSystemPromptFile -> đọc content, inject vào system_prompt
    # 3. Patch image input: node load_image.inputs.image = image_filename
    # 4. Patch user prompt (nếu có)
    # 5. Queue workflow: /prompt endpoint
    # 6. Return prompt_id cho frontend polling /history
```

#### 2.3 Workflow template
**Tạo file mới**: `workflows/llm_workflow.json`
```json
{
  "nodes": {
    "FK:LLM_LOAD": {
      "class_type": "LoadImage",
      "inputs": {"image": "placeholder.png"}
    },
    "FK:LLM_VISION": {
      "class_type": "fc09a263-6758-4092-9881-cec1064e43f6",
      "inputs": {
        "image": ["FK:LLM_LOAD", 0],
        "anything": ""  
      }
    },
    "FK:LLM_OUTPUT": {
      "class_type": "easy showAnything",
      "inputs": {"anything": ["FK:LLM_VISION", 0]}
    }
  }
}
```

**Patching logic** (giống T2I/EDIT workflow):
```python
wf["FK:LLM_LOAD"]["inputs"]["image"] = image_name
wf["FK:LLM_VISION"]["inputs"]["anything"] = user_prompt or ""
# Settings injection (như UNETLoader/VAELoader pattern)
wf["FK:LLM_VISION"]["model"] = config["llmModel"]
wf["FK:LLM_VISION"]["mmproj"] = config["llmMmproj"]
wf["FK:LLM_VISION"]["system_prompt"] = read_prompt_file(config["llmSystemPromptFile"])
```

### 3. Dependencies

#### 3.1 Custom node requirement
**Cần cài đặt custom node**: `fc09a263-6758-4092-9881-cec1064e43f6`

Tìm trong ComfyUI Manager hoặc workflow JSON để xác định tên package.
Pattern: tìm `properties.cnr_id` hoặc `aux_id` của node type này.

#### 3.2 Model requirements
- Model: vision-capable GGUF (LLaVA, BakLLaVA, Obsidian, MiniCPM-V, Gemma-Vision, etc.)
- MMProj: matching multimodal projector file
- System prompt: `LLM-system.txt` với vision task instructions

Folder structure:
```
models/LLM/
├── model.gguf              # main vision model
├── mmproj.gguf             # multimodal projector
└── prompts/
    └── LLM-system.txt      # system prompt
```

### 4. Workflow tích hợp (dựa trên LLM-all-in-One-v.8.8.json)

**Phân tích workflow hiện tại** (`workflows/LLM-all-in-One-v.8.8.json`):

```
LoadImage (362)
    ↓ IMAGE
Switch Node (964) ← chọn giữa LLM/i2i/t2i
    ↓ image + string (prompt)
LLM Vision Wrapper (368) ← ProxyWidgets: model/mmproj/system_prompt
    ↓ output (STRING)
ShowAnything (364) ← hiển thị kết quả
```

**Node chính**: 
- Type: `fc09a263-6758-4092-9881-cec1064e43f6` (UUID custom node)
- ProxyWidgets trỏ đến node 944 chứa settings: `model`, `mmproj`, `system_prompt`
- Input: IMAGE + STRING (prompt)
- Output: STRING (description)

**Backend sẽ replicate workflow này**:

```python
# Workflow structure for LLM tab
llm_workflow = {
    "nodes": {
        "load_image": {
            "class_type": "LoadImage",
            "inputs": {"image": image_filename}
        },
        "llm_vision": {
            "class_type": "fc09a263-6758-4092-9881-cec1064e43f6",
            "inputs": {
                "image": ["load_image", 0],
                "anything": user_prompt  # STRING prompt
            },
            # Settings từ tab Settings
            "model": llm_model_path,
            "mmproj": mmproj_path,
            "system_prompt": system_prompt_content
        },
        "show_result": {
            "class_type": "easy showAnything",
            "inputs": {
                "anything": ["llm_vision", 0]
            }
        }
    }
}
```

**Cách triển khai**:
1. **Option A** (Recommended): Tạo workflow JSON template giống pattern T2I/EDIT hiện tại
2. **Option B**: Gọi trực tiếp custom node qua ComfyUI API
3. **Option C**: Standalone llama.cpp (không qua ComfyUI workflow)

**Chọn Option A**: Tận dụng workflow system có sẵn, nhất quán với code hiện tại.

### 5. File structure sau khi hoàn thành
```
custom_nodes/one-node-flux-2-klein/
├── web/
│   └── one_node_flux_2_klein.js   (+ LLM tab UI ~200 LOC)
├── nodes.py                        (+ 4 scan endpoints + workflow endpoint)
├── workflows/
│   ├── t2i_workflow.json           (existing)
│   ├── edit_workflow.json          (existing)
│   └── llm_workflow.json           (NEW - LLM vision workflow template)
└── docs/
    └── LLM_TAB_PLAN.md             (this file)

ComfyUI/models/LLM/
├── *.gguf                          (vision models)
├── *mmproj*.gguf                   (projectors)
└── prompts/
    └── *.txt                       (system prompts)
```

### 6. Testing checklist
- [ ] Scan endpoints return correct file lists (`/llm-models`, `/llm-mmprojs`, `/llm-prompts`)
- [ ] Settings dropdowns populate with scanned files
- [ ] Image upload works in LLM slot
- [ ] Analyze button triggers workflow queue
- [ ] Workflow patching works (model/mmproj/prompt injection)
- [ ] Custom node `fc09a263-...` executes successfully
- [ ] Result displays in panel after completion
- [ ] State persists across page reload
- [ ] Tab switching works (LLM ↔ other tabs)
- [ ] Error handling for missing model/mmproj/image

### 7. Edge cases & error handling
- Custom node not installed → show install guide with node name
- Model/mmproj mismatch → catch node error, show user warning
- Image not uploaded → disable analyze button
- Workflow execution timeout → show error + prompt_id for debugging
- Empty result → "No description generated"
- Missing system prompt file → use default prompt or block execution

### 8. UX polish
- Show spinner during execution (polling /history for prompt_id)
- Disable analyze button while processing
- Copy-to-clipboard button for result text
- Result can feed to T2I prompt (button "Use as T2I prompt")
- Progress indicator from ComfyUI websocket (if available)

---

## Implementation priority
1. **Phase 1**: Create `llm_workflow.json` template ← test manually first
2. **Phase 2**: Backend scan endpoints (3 GET routes)
3. **Phase 3**: Backend workflow execution endpoint (POST `/llm-analyze`)
4. **Phase 4**: Frontend tab UI (button + panel + slot)
5. **Phase 5**: Settings integration (3 dropdowns)
6. **Phase 6**: UX polish (spinner, errors, copy button)

## Estimated effort
- Phase 1: ~30 min (workflow template + manual test)
- Phase 2: ~45 min (scan logic, reuse existing patterns)
- Phase 3: ~90 min (workflow patching + queue)
- Phase 4: ~120 min (tab UI, matching existing tabs)
- Phase 5: ~30 min (dropdowns in settings modal)
- Phase 6: ~45 min (polish)
**Total**: ~6 hours implementation + testing

## Key differences from original plan
- ❌ No standalone llama.cpp integration
- ✅ Use ComfyUI workflow system (consistent with T2I/EDIT)
- ✅ Reuse custom node `fc09a263-6758-4092-9881-cec1064e43f6` from existing workflow
- ✅ Backend becomes workflow orchestrator, not direct LLM caller
- ✅ Leverage ComfyUI's queue/history system for async execution

---
*Plan updated: 2026-06-22 - Based on LLM-all-in-One-v.8.8.json analysis*
