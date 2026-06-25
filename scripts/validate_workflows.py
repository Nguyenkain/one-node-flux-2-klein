"""
Validate all workflow JSON templates in the workflows/ directory.

Usage:
    python scripts/validate_workflows.py

Checks:
    - Valid JSON syntax
    - Top-level is a flat object with node IDs as keys
    - Each node has class_type and inputs
    - Non-empty (at least one node)
"""

import json
import sys
from pathlib import Path

WORKFLOWS_DIR = Path(__file__).resolve().parent.parent / "workflows"


def validate_workflow(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"Invalid JSON: {e}"]

    if not isinstance(data, dict):
        return ["Top-level is not a dict/object"]

    if len(data) == 0:
        return ["Workflow is empty (no nodes)"]

    # Each key is a node ID, each value must have class_type + inputs
    for node_id, node in data.items():
        if not isinstance(node, dict):
            errors.append(f"Node '{node_id}' is not an object (got {type(node).__name__})")
            continue
        if "class_type" not in node:
            errors.append(f"Node '{node_id}' missing 'class_type'")
        if "inputs" not in node:
            errors.append(f"Node '{node_id}' missing 'inputs'")
        elif not isinstance(node["inputs"], dict):
            errors.append(f"Node '{node_id}' 'inputs' is not an object")

    return errors


def main() -> int:
    if not WORKFLOWS_DIR.is_dir():
        print(f"ERROR: workflows/ directory not found at {WORKFLOWS_DIR}")
        return 1

    wf_files = sorted(WORKFLOWS_DIR.glob("*.json"))
    if not wf_files:
        print("WARNING: No workflow JSON files found")
        return 0

    all_ok = True
    for wf_path in wf_files:
        errors = validate_workflow(wf_path)
        if errors:
            all_ok = False
            print(f"FAIL  {wf_path.name}")
            for e in errors:
                print(f"      -> {e}")
        else:
            print(f"OK    {wf_path.name}")

    if all_ok:
        print(f"\nAll {len(wf_files)} workflows are valid.")
        return 0
    else:
        print(f"\nSome workflows have issues. See details above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
