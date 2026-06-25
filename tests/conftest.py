"""
Pytest fixtures for One Node · FLUX.2 [klein].

Provides mocked ComfyUI dependencies so tests can run without a full ComfyUI installation.
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def node_dir():
    """Absolute path to the project root."""
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def temp_config_dir():
    """Temporary directory with a minimal config.json for testing."""
    with tempfile.TemporaryDirectory() as tmp:
        config = {
            "autofill_prompts": {},
            "lora_triggers_custom": {},
            "t2i_templates": [],
            "discover_prompts": {},
        }
        config_path = Path(tmp) / "config.json"
        config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
        yield Path(tmp)


# ---------------------------------------------------------------------------
# ComfyUI mocks
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def mock_comfyui():
    """Mock the ComfyUI runtime so nodes.py can be imported in tests."""
    with patch.dict(sys.modules, {
        "folder_paths": MagicMock(),
        "server": MagicMock(),
    }):
        yield
