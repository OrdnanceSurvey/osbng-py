"""Support for parameterised testing."""

import json
from pathlib import Path


def _load_test_cases(file_path: str | Path) -> dict:
    """Load test cases from a JSON file.

    Args:
        file_path (str | Path): Path to the JSON file containing test cases.

    Returns:
        dict: Test cases as a dictionary.

    """
    # Convert to Path object if a string is provided
    p = Path(file_path)
    with p.open(encoding="utf-8") as f:
        return json.load(f)
