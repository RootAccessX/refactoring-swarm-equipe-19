"""
Pylint Tool - Wrapper for static code analysis.
Executes pylint and returns structured results.
"""

import subprocess
import re
import json
from typing import Dict, List, Optional


def run_pylint(filepath: str, timeout: int = 30) -> Dict:
    """
    Run pylint on a Python file and return structured results.
    
    Args:
        filepath: Path to the Python file to analyze
        timeout: Maximum execution time in seconds
    
    Returns:
        Dictionary containing:
        - score: Pylint score (0-10)
        - issues: List of issues found
        - raw_output: Raw pylint output
        - success: Whether pylint ran successfully
    """
    result = {
        "score": 0.0,
        "issues": [],
        "raw_output": "",
        "success": False,
        "error": None
    }
    
    try:
        # Run pylint with JSON output format
        cmd = ["pylint", filepath, "--output-format=json"]
        
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        result["raw_output"] = process.stdout
        
        # Parse JSON output
        if process.stdout:
            try:
                issues_data = json.loads(process.stdout)
                result["issues"] = issues_data
            except json.JSONDecodeError:
                # Fallback to text parsing if JSON fails
                result["issues"] = _parse_text_output(process.stdout)
        
        # Extract score from stderr (pylint outputs score there)
        score = _extract_score(process.stderr)
        if score is not None:
            result["score"] = score
        
        result["success"] = True
        
    except subprocess.TimeoutExpired:
        result["error"] = f"Pylint timed out after {timeout} seconds"
    except FileNotFoundError:
        result["error"] = "Pylint not installed. Run: pip install pylint"
    except Exception as e:
        result["error"] = f"Pylint execution error: {str(e)}"
    
    return result


def _extract_score(output: str) -> Optional[float]:
    """
    Extract pylint score from output text.
    
    Args:
        output: Pylint output text
    
    Returns:
        Score as float or None if not found
    """
    # Pylint score format: "Your code has been rated at 7.50/10"
    match = re.search(r'rated at ([\d.]+)/10', output)
    if match:
        return float(match.group(1))
    return None


def _parse_text_output(output: str) -> List[Dict]:
    """
    Parse pylint text output into structured issues.
    
    Args:
        output: Raw pylint text output
    
    Returns:
        List of issue dictionaries
    """
    issues = []
    lines = output.split('\n')
    
    for line in lines:
        # Format: filename:line:column: message-id: message
        match = re.match(r'^(.+):(\d+):(\d+): ([A-Z]\d+): (.+)$', line)
        if match:
            issues.append({
                "path": match.group(1),
                "line": int(match.group(2)),
                "column": int(match.group(3)),
                "message-id": match.group(4),
                "message": match.group(5)
            })
    
    return issues


def get_score_only(filepath: str) -> float:
    """
    Quick function to get just the pylint score.
    
    Args:
        filepath: Path to Python file
    
    Returns:
        Pylint score (0-10) or 0 if error
    """
    result = run_pylint(filepath)
    return result.get("score", 0.0)


def has_critical_issues(filepath: str) -> bool:
    """
    Check if file has critical (E) or fatal (F) issues.
    
    Args:
        filepath: Path to Python file
    
    Returns:
        True if critical issues found
    """
    result = run_pylint(filepath)
    issues = result.get("issues", [])
    
    for issue in issues:
        # Check message-id prefix (E=error, F=fatal)
        msg_id = issue.get("message-id", "")
        if msg_id.startswith(('E', 'F')):
            return True
    
    return False
