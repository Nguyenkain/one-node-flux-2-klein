"""
Basic smoke tests for the node package.
"""

import os
import json
from pathlib import Path


def test_init_imports(node_dir):
    """Verify __init__.py can be parsed and has the expected exports."""
    init_path = node_dir / "__init__.py"
    assert init_path.exists(), "__init__.py missing"

    # Parse the file to check expected symbols
    content = init_path.read_text(encoding="utf-8")
    assert "NODE_CLASS_MAPPINGS" in content
    assert "NODE_DISPLAY_NAME_MAPPINGS" in content
    assert "WEB_DIRECTORY" in content


def test_config_json_valid(node_dir):
    """Verify config.json is valid JSON."""
    config_path = node_dir / "config.json"
    assert config_path.exists(), "config.json missing"

    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert isinstance(data, dict)
    assert "autofill_prompts" in data
    assert "t2i_templates" in data
    assert "discover_prompts" in data


def test_workflows_exist(node_dir):
    """Verify all expected workflow templates are present."""
    workflows_dir = node_dir / "workflows"
    assert workflows_dir.is_dir(), "workflows/ directory missing"

    expected_modes = [
        "t2i", "i2i", "edit", "inpaint", "outpaint", "faceswap", "remove_bg",
        "krea_t2i", "krea_i2i",
    ]
    for mode in expected_modes:
        wf_path = workflows_dir / f"{mode}_workflow.json"
        assert wf_path.exists(), f"Missing workflow: {wf_path.name}"

        # Quick JSON validity check
        with open(wf_path, "r", encoding="utf-8") as f:
            json.load(f)


def test_web_js_exists(node_dir):
    """Verify the frontend widget file exists."""
    js_path = node_dir / "web" / "one_node_flux_2_klein.js"
    assert js_path.exists(), "Frontend JS file missing"
    assert js_path.stat().st_size > 0, "Frontend JS file is empty"


def test_readme_exists(node_dir):
    """Verify README.md is present and non-empty."""
    readme = node_dir / "README.md"
    assert readme.exists(), "README.md missing"
    assert readme.stat().st_size > 0, "README.md is empty"


def test_assets_directory(node_dir):
    """Verify assets/ directory exists with expected media."""
    assets_dir = node_dir / "assets"
    assert assets_dir.is_dir(), "assets/ directory missing"
    # Should have at least one file
    contents = list(assets_dir.iterdir())
    assert len(contents) > 0, "assets/ directory is empty"
