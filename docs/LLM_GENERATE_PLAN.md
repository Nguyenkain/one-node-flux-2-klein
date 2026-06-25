# Plan: Tích hợp LLM tab vào nút "Generate"

## Hiện trạng

- Tab LLM có nút "Analyze Image" riêng (dòng ~6004)
- `genBtn.onclick` (dòng 7650) có guard: `if(activePill==="llm"){showError("LLM tab uses its own button");return;}`
- Tab LLM dùng workflow `llm_workflow.json` riêng
- Result từ LLM about là text, không phải image → không thể dùng `execution_success` → `showFinal()` vì nó expect image output

## Cần làm

### 1. Gỡ guard + nút "Analyze Image" riêng

**Dòng 7650-7651**: Xóa guard block
```javascript
// XÓA dòng này:
if(activePill==="llm"){showError("LLM tab uses its own 'Analyze Image' button.");return;}
```

**Dòng ~6004-6138**: Giữ lại `llmAnalyzeBtn` và flow của nó nhưng ẩn nút đi, chỉ giữ code handler để reuse.

### 2. Thêm validate LLM vào genBtn

Sau validate prompt (dòng 7652), thêm validate cho LLM:
```javascript
if(activePill==="llm"){
  if(!llmSlot.hasFile()){_slotErr(llmSlot, llmSlotLbl);return;}
  if(!S.llmModel||S.llmModel==="none"){showError("LLM: select a model in Settings.");return;}
}
```

### 3. Fork workflow load cho LLM

Sau validate, thêm fork sớm nhất. Hiện tại flow load workflow ở dòng 7729-7741:
```javascript
// Thêm dòng này trước dòng 7735:
if(activePill==="llm") wfUrl = "/flux_klein/workflow_llm";
```

### 4. Fork patching → inject text vào promptTA

LLM không cần image workflow patching. Sau khi queue + poll xong, kết quả text được điền thẳng vào `promptTA` (ô prompt chính phía dưới).

```javascript
if(activePill==="llm"){
  set("FK:LLM_LOAD", "image", S.llmImage||"placeholder.png");
  const llmUserPrompt = S.prompt.trim() || "Describe this image in detail.";
  set("FK:LLM_VISION", "prompt", llmUserPrompt);
  set("FK:LLM_VISION", "model", S.llmModel||"model.gguf");
  set("FK:LLM_VISION", "mmproj", S.llmMmproj||"none");
  set("FK:LLM_VISION", "system_prompt", S.llmSystemPromptFile||"none");
  
  try{
    const resp = await api.fetchApi("/prompt",{method:"POST",headers:{"Content-Type":"application/json"},
      body:JSON.stringify({prompt,client_id:api.clientId})});
    const result = await resp.json();
    if(result.error){showError(fmtErr(result.error));resetBtn();return;}
    const promptId = result.prompt_id;
    
    // Poll history for text result
    let done=false, tries=0;
    while(!done && tries<300){
      await new Promise(r=>setTimeout(r,2000));
      tries++;
      try{
        const hR = await api.fetchApi(`/history/${promptId}`);
        const hD = await hR.json();
        const entry = hD[promptId];
        if(entry){
          if(entry.status&&entry.status.status_str==="error"){
            showError("LLM failed: "+((entry.status.messages||[]).map(m=>m[1]||"").join("; ")));
            resetBtn();return;
          }
          for(const [nid, nd] of Object.entries(entry.outputs||{})){
            let txt=null;
            if(nd.text&&Array.isArray(nd.text)&&nd.text.length>0){txt=nd.text[0];}
            else{for(const [k,v] of Object.entries(nd)){if(Array.isArray(v)&&v.length>0&&typeof v[0]==='string'){txt=v[0];break;}}}
            if(txt){
              // Inject straight into main prompt textarea
              S.prompt=txt;S.promptLLM=txt;persist();
              promptTA.value=txt;_promptTARef=promptTA;
              done=true;
            }
          }
        }
      }catch(e){console.warn("[FluxKlein] LLM poll:",e);}
    }
    if(!done){showError("LLM: timeout.");}
  }catch(e){showError("LLM error: "+fmtErr(e));}
  resetBtn();
  return;
}
```

### 5. Xóa toàn bộ UI LLM riêng (llmResultBox, llmCopyBtn, llmAnalyzeBtn)

Không cần nữa vì kết quả xuất hiện trực tiếp trong promptTA:
- Xóa `llmResultWrap`, `llmResultBox`, `llmResultLabel`
- Xóa `llmCopyBtn`
- Xóa `llmAnalyzeBtn` + spinner `llmSpinner`
- Xóa `_llmSetRunning`
- Chỉ giữ `llmSlot` (upload ảnh) + `llmPromptTA` (optional user prompt guide)

### 6. UX

- **GenBtn**: Animation "Generating…" giống các tab khác, dùng chung `genBtn.disabled` + gradient
- **Kết quả**: Text hiện ra trực tiếp trong ô Prompt chính phía dưới → user có thể edit rồi Generate tiếp

## File structure change

Chỉ sửa **1 file**: `web/one_node_flux_2_klein.js`

### Sửa:
- Dòng 7650: Xóa `if(activePill==="llm")...` guard
- Dòng 7650+: Thêm validate LLM: check `llmSlot.hasFile()` + `S.llmModel`
- Dòng 7735: Thêm `if(activePill==="llm") wfUrl = "/flux_klein/workflow_llm";`
- Dòng 7752: Sau `const prompt=JSON.parse(...)`, thêm LLM fork block như trên
- Dòng 5998: Ẩn `llmAnalyzeBtn` (display:none)
- Dòng 6004: Xóa `llmAnalyzeBtn.onclick` handler cũ

### Lợi ích
- Tab LLM dùng chung nút Generate → UI nhất quán
- Dùng chung progress UI ("Generating…", gradient animation)
- Dùng chung stop button, error handling
- Kết quả hiển thị ngay trong llmResultBox

## Risk
- LLM polling chạy trong async block nhưng không chạy `execution_success` flow
  → Không conflict với image-based tabs
  → `resetBtn()` gọi ở cuối LLM path để cleanup state
- Generation time dài (có thể vài phút) → polling 300×2s = 10 phút đủ

---
*Plan created: 2026-06-22*
