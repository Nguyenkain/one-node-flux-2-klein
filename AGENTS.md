# AGENTS.md

## Project overview
- This repo is a ComfyUI custom node named `One Node · FLUX.2 [klein]`.
- The backend is concentrated in `nodes.py`.
- The frontend widget is concentrated in `web/one_node_flux_2_klein.js`.
- Static workflow templates live in `workflows/`.
- User-facing defaults and prompt/config data live in `config.json`.

## Architecture map
- `__init__.py`: exports the node mappings and web directory.
- `nodes.py`: registers HTTP routes, reads/writes config, scans models, manages gallery metadata, and exposes the no-op output node shell used by the UI.
- `web/one_node_flux_2_klein.js`: renders the full in-node UI and orchestrates frontend behavior.
- `workflows/*.json`: mode-specific workflow templates for T2I, I2I, Edit, Paint/Inpaint/Outpaint, Faceswap, and background removal.
- `favorites.json`: local persistent gallery favorites.

## Working conventions
- Keep changes surgical; do not restructure the repo unless explicitly requested.
- Prefer extending existing backend routes in `nodes.py` before introducing new modules.
- Keep frontend UI behavior in `web/one_node_flux_2_klein.js` consistent with current patterns.
- Treat `config.json` as user-editable data; preserve backward compatibility when adding keys.
- Put new architecture notes in `docs/` instead of large comments in code.

## Suggested extension areas
- Add new feature notes under `docs/features/`.
- Add API/route notes under `docs/api/`.
- Add helper scripts under `scripts/` only when they are directly useful for development or maintenance.
