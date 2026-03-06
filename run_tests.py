#!/usr/bin/env python3
"""
Run all annotator tests with report generation.

This script runs all test files in src/annotator/tests/ and generates
individual reports for each test suite.

Usage:
    python run_tests.py              # Run all tests
    pytest src/annotator/tests/ -v   # Alternative using pytest directly
"""

import sys
import subprocess
from pathlib import Path


def main():
    """Run all tests in the tests directory."""
    tests_dir = Path(__file__).parent / "src" / "annotator" / "tests"
    
    if not tests_dir.exists():
        print(f"Error: Tests directory not found: {tests_dir}")
        return 1
    
    # Find all test files
    test_files = list(tests_dir.glob("test_*.py"))
    
    if not test_files:
        print(f"No test files found in {tests_dir}")
        return 1
    
    print(f"Found {len(test_files)} test file(s)")
    print("=" * 70)
    print()
    
    failed_tests = []
    passed_tests = []
    
    # Run each test file
    for test_file in sorted(test_files):
        print(f"Running {test_file.name}...")
        result = subprocess.run(
            [sys.executable, str(test_file)],
            cwd=Path(__file__).parent
        )
        
        if result.returncode == 0:
            passed_tests.append(test_file.name)
        else:
            failed_tests.append(test_file.name)
        
        print()
    
    # Summary
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"✅ Passed: {len(passed_tests)}")
    for test in passed_tests:
        print(f"   - {test}")
    
    if failed_tests:
        print(f"\n❌ Failed: {len(failed_tests)}")
        for test in failed_tests:
            print(f"   - {test}")
    
    print("=" * 70)
    
    return 1 if failed_tests else 0


if __name__ == "__main__":
    sys.exit(main())
