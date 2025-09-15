#!/usr/bin/env python3
"""
Test runner script for the portfolio visualizer project.
"""
import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(test_type="all", verbose=False, coverage=False):
    """Run tests with specified options."""
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    # Add coverage if requested
    if coverage:
        cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])
    
    # Select test files based on type
    if test_type == "unit":
        cmd.extend(["./tests/test_i18n.py", "./tests/test_i18n_helpers.py", "./tests/test_language_switching.py"])
    elif test_type == "integration":
        cmd.extend(["./tests/test_integration.py", "./tests/test_routers.py"])
    elif test_type == "templates":
        cmd.append("./tests/test_templates.py")
    elif test_type == "i18n":
        cmd.extend(["./tests/test_i18n.py", "./tests/test_i18n_helpers.py", "./tests/test_language_switching.py", "./tests/test_templates.py"])
    elif test_type == "all":
        cmd.extend(["./tests/"])
    else:
        print(f"Unknown test type: {test_type}")
        return False
    
    # Add test discovery
    cmd.extend(["-x", "--tb=short"])
    
    print(f"Running {test_type} tests...")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 50)
        print("❌ Some tests failed!")
        return False
    except FileNotFoundError:
        print("❌ pytest not found. Please install it with: pip install pytest")
        return False


def main():
    """Main function to parse arguments and run tests."""
    parser = argparse.ArgumentParser(description="Run tests for portfolio visualizer")
    parser.add_argument(
        "type",
        nargs="?",
        default="all",
        choices=["all", "unit", "integration", "templates", "i18n"],
        help="Type of tests to run (default: all)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Run tests in verbose mode"
    )
    parser.add_argument(
        "-c", "--coverage",
        action="store_true",
        help="Run tests with coverage report"
    )
    
    args = parser.parse_args()
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Run tests
    success = run_tests(args.type, args.verbose, args.coverage)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
