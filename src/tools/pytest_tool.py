"""
Pytest Tool - Wrapper for unit test execution.
Executes pytest and returns structured results.
"""

import subprocess
import json
import os
from typing import Dict, List


def run_pytest(target_path: str, timeout: int = 60) -> Dict:
    """
    Run pytest on a file or directory and return structured results.
    
    Args:
        target_path: Path to test file or directory
        timeout: Maximum execution time in seconds
    
    Returns:
        Dictionary containing:
        - passed: Number of tests passed
        - failed: Number of tests failed
        - total: Total number of tests
        - success: Whether all tests passed
        - details: Detailed test results
        - error: Error message if execution failed
    """
    result = {
        "passed": 0,
        "failed": 0,
        "total": 0,
        "success": False,
        "details": [],
        "error": None,
        "raw_output": ""
    }
    
    if not os.path.exists(target_path):
        result["error"] = f"Path not found: {target_path}"
        return result
    
    try:
        # Run pytest with JSON report
        cmd = [
            "pytest",
            target_path,
            "-v",  # Verbose
            "--tb=short",  # Short traceback
            "--json-report",  # Generate JSON report
            "--json-report-file=temp_pytest_report.json"
        ]
        
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.getcwd()
        )
        
        result["raw_output"] = process.stdout
        
        # Try to read JSON report if it exists
        json_report_path = "temp_pytest_report.json"
        if os.path.exists(json_report_path):
            try:
                with open(json_report_path, 'r') as f:
                    report_data = json.load(f)
                    result.update(_parse_json_report(report_data))
                os.remove(json_report_path)  # Cleanup
            except Exception as e:
                result["error"] = f"Failed to parse JSON report: {str(e)}"
        else:
            # Fallback: parse text output
            result.update(_parse_text_output(process.stdout))
        
        # Determine success
        result["success"] = result["failed"] == 0 and result["total"] > 0
        
    except subprocess.TimeoutExpired:
        result["error"] = f"Pytest timed out after {timeout} seconds"
    except FileNotFoundError:
        result["error"] = "Pytest not installed. Run: pip install pytest pytest-json-report"
    except Exception as e:
        result["error"] = f"Pytest execution error: {str(e)}"
    
    return result


def _parse_json_report(report_data: Dict) -> Dict:
    """
    Parse pytest JSON report.
    
    Args:
        report_data: JSON report data
    
    Returns:
        Parsed results dictionary
    """
    summary = report_data.get("summary", {})
    
    return {
        "passed": summary.get("passed", 0),
        "failed": summary.get("failed", 0),
        "total": summary.get("total", 0),
        "details": report_data.get("tests", [])
    }


def _parse_text_output(output: str) -> Dict:
    """
    Parse pytest text output.
    
    Args:
        output: Raw pytest output
    
    Returns:
        Parsed results dictionary
    """
    import re
    
    result = {
        "passed": 0,
        "failed": 0,
        "total": 0
    }
    
    # Look for summary line: "=== 5 passed, 2 failed in 1.23s ==="
    match = re.search(r'(\d+) passed', output)
    if match:
        result["passed"] = int(match.group(1))
    
    match = re.search(r'(\d+) failed', output)
    if match:
        result["failed"] = int(match.group(1))
    
    result["total"] = result["passed"] + result["failed"]
    
    return result


def has_tests(directory: str) -> bool:
    """
    Check if directory contains test files.
    
    Args:
        directory: Path to check
    
    Returns:
        True if test files found
    """
    import os
    from pathlib import Path
    
    path = Path(directory)
    if not path.exists():
        return False
    
    # Look for files starting with test_ or ending with _test.py
    test_files = list(path.rglob("test_*.py")) + list(path.rglob("*_test.py"))
    
    return len(test_files) > 0
