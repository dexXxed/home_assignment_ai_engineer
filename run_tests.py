#!/usr/bin/env python3
"""
Test runner for the diagram generator service
Provides different test execution options
"""
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """
    Run a command and handle the output
    
    Args:
        cmd: Command to run
        description: Description of what the command does
    """
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode != 0:
        print(f"\n[FAILED] {description} failed with exit code {result.returncode}")
        return False
    else:
        print(f"\n[SUCCESS] {description} completed successfully")
        return True


def main():
    """Main test runner function"""
    # Ensure we're in the right directory
    project_root = Path(__file__).parent
    
    # Available test options
    test_options = {
        "all": ("Run all tests", ["python", "-m", "pytest", "tests/", "-v"]),
        "core": ("Run core module tests", ["python", "-m", "pytest", "tests/core/", "-v"]),
        "utils": ("Run utils module tests", ["python", "-m", "pytest", "tests/utils/", "-v"]),
        "api": ("Run API tests", ["python", "-m", "pytest", "tests/api/", "-v"]),
        "tools": ("Run tools tests", ["python", "-m", "pytest", "tests/tools/", "-v"]),
        "agents": ("Run agents tests", ["python", "-m", "pytest", "tests/agents/", "-v"]),
        "coverage": ("Run tests with coverage", ["python", "-m", "pytest", "tests/", "--cov=diagram_generator", "--cov-report=html", "--cov-report=term"]),
        "fast": ("Run tests without verbose output", ["python", "-m", "pytest", "tests/", "-q"]),
        "failed": ("Run only failed tests", ["python", "-m", "pytest", "tests/", "--lf", "-v"]),
        "check": ("Run a quick smoke test", ["python", "-m", "pytest", "tests/core/test_constants.py::TestResponseTypes::test_response_type_values", "-v"])
    }
    
    if len(sys.argv) == 1:
        print("Diagram Generator Test Runner")
        print("="*40)
        print("Available test options:")
        for key, (description, _) in test_options.items():
            print(f"  {key:10} - {description}")
        print("\nUsage: python run_tests.py [option]")
        print("Example: python run_tests.py all")
        return
    
    option = sys.argv[1].lower()
    
    if option not in test_options:
        print(f"[ERROR] Unknown option: {option}")
        print("Available options:", ", ".join(test_options.keys()))
        return
    
    description, cmd = test_options[option]
    
    # Run the test
    success = run_command(cmd, description)
    
    if success:
        print(f"\n[COMPLETE] Test execution completed successfully!")
        if option == "coverage":
            print("[INFO] Coverage report generated in htmlcov/index.html")
    else:
        print(f"\n[FAILED] Test execution failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 