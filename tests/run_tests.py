#!/usr/bin/env python3
"""
Test runner for NMAstudio application.
Runs all test files in the tests directory.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_test_file(test_file):
    """Run a single test file and return the result."""
    print(f"\n{'=' * 60}")
    print(f"Running {test_file}...")
    print(f"{'=' * 60}")

    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )

        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"STDERR: {result.stderr}")

        return result.returncode == 0
    except Exception as e:
        print(f"Error running {test_file}: {e}")
        return False


def main():
    """Run all test files in the tests directory."""
    tests_dir = Path(__file__).parent
    test_files = [
        "test_homepage_console_errors.py",
        "test_psoriasis_data_load.py",
        "test_reset_storage_emptying.py",
        "test_setuppage_console_errors.py",
    ]

    print("Starting NMAstudio test suite...")
    print(f"Tests directory: {tests_dir}")

    passed = 0
    failed = 0

    for test_file in test_files:
        test_path = tests_dir / test_file
        if test_path.exists():
            if run_test_file(str(test_path)):
                passed += 1
                print(f"✓ {test_file} PASSED")
            else:
                failed += 1
                print(f"✗ {test_file} FAILED")
        else:
            print(f"⚠ {test_file} NOT FOUND")
            failed += 1

    print(f"\n{'=' * 60}")
    print(f"Test Results: {passed} passed, {failed} failed")
    print(f"{'=' * 60}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
