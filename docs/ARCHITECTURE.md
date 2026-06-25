# Architecture Summary

## Core pieces

- `nodes.py` is the Python backend entrypoint and the main integration layer with ComfyUI.
- `web/one_node_flux_2_klein.js` is the single large frontend widget implementation.
- `workflows/` stores the mode-specific graph templates that the UI assembles or submits.
- `config.json` stores prompt templates, defaults, and feature settings.

## Runtime flow

1. ComfyUI loads `__init__.py`.
2. The repo exposes `FluxKleinOneNode` and serves the frontend from `web/`.
3. The frontend requests config, model lists, metadata, and gallery data through routes registered in `nodes.py`.
4. The node UI drives different generation modes using the workflow JSON templates.

## Existing backend responsibilities

- Persist config updates.
- Scan installed models, VAEs, text encoders, and LoRAs.
- Read LoRA trigger metadata from `.safetensors` headers.
- Manage gallery metadata, favorites, deletion, and folder opening.
- Resolve paths defensively for input/output operations.

## Existing frontend responsibilities

- Render the all-in-one node UI.
- Switch between modes such as T2I, I2I, Edit, Paint, and Faceswap.
- Load server config and model choices.
- Coordinate preview/final image display and settings panels.

## Good next refactors

- Split frontend UI into smaller modules if the project grows further.
- Extract backend route helpers from `nodes.py` only when a clear boundary emerges.
- Add focused documentation for each feature before larger changes.
