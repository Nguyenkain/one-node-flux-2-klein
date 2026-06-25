"""
One-time or repeatable setup helpers for the development environment.

Usage:
    python scripts/dev_setup.py

Performs:
    - Verifies the project is in a ComfyUI custom_nodes folder
    - Checks for required companion nodes
    - Prints model download URLs
"""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
REQUIRED_COMPANION = "ComfyUI-Inpaint-CropAndStitch"


def check_comfyui_env() -> bool:
    """Verify we're inside a ComfyUI custom_nodes directory."""
    custom_nodes = PROJECT_DIR.parent
    comfyui = custom_nodes.parent

    main_py = comfyui / "main.py"
    if main_py.exists():
        print(f"OK    ComfyUI detected at: {comfyui}")
        return True

    print(f"WARN  ComfyUI main.py not found at expected location: {main_py}")
    print(f"      Project lives at: {PROJECT_DIR}")
    print(f"      (this is fine if ComfyUI is installed elsewhere)")
    return False


def check_companion_nodes() -> bool:
    """Check for required companion custom nodes."""
    custom_nodes = PROJECT_DIR.parent
    companion = custom_nodes / REQUIRED_COMPANION

    if companion.is_dir():
        print(f"OK    Companion node found: {REQUIRED_COMPANION}")
        return True

    print(f"MISS  Companion node not found: {REQUIRED_COMPANION}")
    print(f"      Clone it with:")
    print(f"      git clone https://github.com/lquesada/ComfyUI-Inpaint-CropAndStitch.git")
    return False


def print_model_info():
    """Print model download references."""
    print()
    print("Model download references:")
    print("  Text encoder: https://huggingface.co/Comfy-Org/vae-text-encorder-for-flux-klein-9b")
    print("  VAE:          https://huggingface.co/Comfy-Org/vae-text-encorder-for-flux-klein-9b")
    print("  Faceswap:     https://huggingface.co/Alissonerdx/BFS-Best-Face-Swap")
    print("  BiRefNet:     https://huggingface.co/Comfy-Org/BiRefNet")


def main() -> int:
    print(f"Dev setup for: {PROJECT_DIR.name}")
    print("-" * 50)
    check_comfyui_env()
    all_ok = check_companion_nodes()
    print_model_info()
    return 0 if all_ok else 0  # non-fatal warnings


if __name__ == "__main__":
    sys.exit(main())
