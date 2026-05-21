# One Node · Flux-2 Klein

A ComfyUI custom node that wraps the full Flux 2 Klein workflow into a single self-contained UI widget. No graph to build, no nodes to connect — just one node with everything inside.

> If this saves you time, you can support the work here: [buymeacoffee.com/yanokusnir](https://buymeacoffee.com/yanokusnir)

---

## What it does

The node has five modes, switchable with a single click:

**T2I** — text to image. Pick a resolution preset or set custom dimensions.

**I2I** — image to image. Drop in an image, set the denoise strength, optionally resize by longer side before generation.

**Edit** — this is where the node really shines. Load one or two reference images and describe what you want changed. The model edits the image while preserving the original structure, lighting, and composition. Has a built-in before/after comparer so you can see exactly what changed.

**Paint** — three tools in one:
- Sketch: a full canvas with layers, brushes, shapes, zoom, and a Remove Background button. Draw something and generate from it.
- Inpaint: paint a mask over the area you want to change, write what should be there instead.
- Outpaint: expand the image in any direction by dragging the edges.

**Faceswap** — swap a face from a source image onto a target. Requires a Faceswap LoRA.

---

## Other features

- Gallery with favorites, lightbox, before/after compare, and "Load settings into UI" to restore any previous generation including the prompt, resolution, images, and LoRAs.
- Prompt Discover panel with curated shortcuts for editing, relighting, style changes and more. Fully editable — add your own categories and prompts.
- Up to 3 simultaneous LoRAs with automatic trigger word detection and custom trigger word overrides per LoRA.
- Advanced control panel for steps, CFG, sampler, scheduler, and seed — hidden by default, enable it in Settings when you need it.
- Metadata saved into every PNG and organized in a separate `metadata/` folder so your output folder stays clean.
- Remove Background tool powered by BiRefNet, available inside the Sketch canvas.
- Keyboard shortcuts: `Space` to generate, `G` gallery, `D` discover, `F` fullscreen, `Esc` to close any overlay.

---

## Installation

You need one additional custom node:

**ComfyUI-Inpaint-CropAndStitch** by lquesada — required for inpaint and outpaint modes.
https://github.com/lquesada/ComfyUI-Inpaint-CropAndStitch

Then clone this repo into your ComfyUI `custom_nodes` folder:

```
cd ComfyUI/custom_nodes
git clone https://github.com/yanokusnir-ai/one-node-flux-2-klein.git
```

Restart ComfyUI. The node appears as **One Node · Flux-2 Klein**.

---

## Models

You will need a Flux 2 Klein diffusion model, a compatible text encoder, and the Flux 2 VAE. Links and setup instructions are in the Help overlay inside the node — click the **✦ Help** button after adding the node.

For Remove Background: a BiRefNet model placed in `models/background_removal/`.

---

## License note on Flux 2 Klein 9B

This node works with both the 4B and 9B variants of Flux 2 Klein. The 4B model is released under Apache 2.0 and can be used freely including commercially.

The 9B model is released under the **FLUX Non-Commercial License** by Black Forest Labs. This means you can use it for personal and research purposes, but commercial use is not permitted. If you use the 9B model, you are responsible for complying with that license. You can review it at https://huggingface.co/black-forest-labs/FLUX.2-klein-9B.

This node itself is fully open source with no restrictions.

---

## Support

If you find this useful and want to support further development:

[buymeacoffee.com/yanokusnir](https://buymeacoffee.com/yanokusnir)
