#!/usr/bin/env python3
"""
Test runner for the deployment automation project
"""

import sys
import subprocess
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and return the result"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.stdout:
            print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ Command timed out")
        return False
    except Exception as e:
        print(f"❌ Command failed: {e}")
        return False

def main():
    """Main test runner"""
    print("🚀 Starting Java Application Deployment Tests")
    print("=" * 60)
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Test results
    test_results = []
    
    # 1. Python script validation
    test_results.append(run_command(
        "python3 -m py_compile deploy.py",
        "Python script syntax validation"
    ))
    
    # 2. Python unit tests
    test_results.append(run_command(
        "python3 -m pytest tests/test_deploy.py -v",
        "Python unit tests"
    ))
    
    # 3. Dockerfile validation
    test_results.append(run_command(
        "docker run --rm -i hadolint/hadolint < Dockerfile",
        "Dockerfile linting"
    ))
    
    # 4. Terraform validation
    os.chdir("infrastructure")
    test_results.append(run_command(
        "terraform fmt -check",
        "Terraform formatting check"
    ))
    
    test_results.append(run_command(
        "terraform validate",
        "Terraform configuration validation"
    ))
    
    # 5. GitHub Actions workflow validation
    os.chdir("..")
    test_results.append(run_command(
        "yamllint .github/workflows/deploy.yml",
        "GitHub Actions workflow validation"
    ))
    
    # 6. Docker build test
    test_results.append(run_command(
        "docker build -t java-app-deployment-test .",
        "Docker image build test"
    ))
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(test_results)
    total = len(test_results)
    
    if passed == total:
        print(f"✅ All tests passed! ({passed}/{total})")
        return 0
    else:
        print(f"❌ Some tests failed ({passed}/{total})")
        return 1

if __name__ == "__main__":
    sys.exit(main())