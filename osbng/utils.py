"""Provides various utility functions to support the project.

Includes functionality for loading test cases from a JSON file,
which can is used to facilitate parameterised testing and validation processes.
"""

import json


def load_test_cases(file_path: str) -> dict:
    """Load test cases from a JSON file

    Args:
        file_path (str): The path to the JSON file containing the test cases.

    Returns:
        dict: The test cases as a dictionary.
    """
    with open(file_path) as f:
        return json.load(f)
