"""
Code Modifier Tool for Toolsmith
Apply code fixes and validate syntax
"""
import ast
import json
from typing import Dict, Optional, Tuple
from src.utils.logger import log_experiment, ActionType
from src.tools.file_tools import (
    read_file, write_file, is_safe_path, create_file_backup
)


class CodeModificationError(Exception):
    """Raised when code modification fails"""
    pass


def validate_python_syntax(code: str, file_path: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """
    Validate Python code syntax.
    
    Args:
        code: Python code to validate
        file_path: Optional file path for logging
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        error_msg = f"Syntax error at line {e.lineno}: {e.msg}"
        
        if file_path:
            log_experiment(
                agent_name="Toolsmith",
                model_used="code_modifier",
                action=ActionType.DEBUG,
                details={
                    "operation": "syntax_validation",
                    "file_path": file_path,
                    "input_prompt": f"Validate syntax: {file_path}",
                    "output_response": error_msg,
                    "error": error_msg
                },
                status="FAILURE"
            )
        
        return False, error_msg
    except Exception as e:
        error_msg = f"Validation error: {str(e)}"
        
        if file_path:
            log_experiment(
                agent_name="Toolsmith",
                model_used="code_modifier",
                action=ActionType.DEBUG,
                details={
                    "operation": "syntax_validation",
                    "file_path": file_path,
                    "input_prompt": f"Validate syntax: {file_path}",
                    "output_response": error_msg,
                    "error": error_msg
                },
                status="FAILURE"
            )
        
        return False, error_msg


def apply_fix(file_path: str, fixed_code: str, sandbox_dir: str = "./sandbox") -> Dict:
    """
    Apply a code fix to a file.
    
    Args:
        file_path: Path to file to modify
        fixed_code: The corrected code
        sandbox_dir: Sandbox root directory
        
    Returns:
        Dictionary with modification result:
        {
            "success": bool,
            "file_path": str,
            "original_size": int,
            "new_size": int,
            "changes": str,
            "error": Optional[str]
        }
        
    Raises:
        SecurityError: If path is outside sandbox
    """
    is_safe_path(file_path, sandbox_dir)
    
    # 1. Validate syntax before writing
    is_valid, error_msg = validate_python_syntax(fixed_code, file_path)
    
    if not is_valid:
        log_experiment(
            agent_name="Toolsmith",
            model_used="code_modifier",
            action=ActionType.DEBUG,
            details={
                "operation": "apply_fix",
                "file_path": file_path,
                "input_prompt": f"Apply fix to: {file_path}",
                "output_response": f"Syntax validation failed: {error_msg}",
                "error": error_msg
            },
            status="FAILURE"
        )
        
        return {
            "success": False,
            "file_path": file_path,
            "error": error_msg
        }
    
    try:
        # 2. Create backup
        original_content = read_file(file_path, sandbox_dir)
        backup_path = create_file_backup(file_path, sandbox_dir)
        
        original_size = len(original_content)
        new_size = len(fixed_code)
        
        # 3. Apply fix
        write_file(file_path, fixed_code, sandbox_dir)
        
        # Determine changes
        changes = f"Lines changed: {len(original_content.split(chr(10)))} -> {len(fixed_code.split(chr(10)))}"
        
        result = {
            "success": True,
            "file_path": file_path,
            "backup_path": backup_path,
            "original_size": original_size,
            "new_size": new_size,
            "size_change": new_size - original_size,
            "changes": changes
        }
        
        log_experiment(
            agent_name="Toolsmith",
            model_used="code_modifier",
            action=ActionType.FIX,
            details={
                "operation": "apply_fix",
                "file_path": file_path,
                "input_prompt": f"Apply fix to: {file_path}",
                "output_response": json.dumps(result),
                "size_change": new_size - original_size,
                "backup": backup_path
            },
            status="SUCCESS"
        )
        
        return result
        
    except Exception as e:
        log_experiment(
            agent_name="Toolsmith",
            model_used="code_modifier",
            action=ActionType.DEBUG,
            details={
                "operation": "apply_fix",
                "file_path": file_path,
                "input_prompt": f"Apply fix to: {file_path}",
                "output_response": f"Error: {str(e)}",
                "error": str(e)
            },
            status="FAILURE"
        )
        
        return {
            "success": False,
            "file_path": file_path,
            "error": str(e)
        }


def add_docstring(file_path: str, sandbox_dir: str = "./sandbox") -> Dict:
    """
    Add docstrings to functions and classes that don't have them.
    
    Args:
        file_path: Path to Python file
        sandbox_dir: Sandbox root directory
        
    Returns:
        Dictionary with modification result
    """
    is_safe_path(file_path, sandbox_dir)
    
    try:
        content = read_file(file_path, sandbox_dir)
        
        # Parse AST
        tree = ast.parse(content)
        
        # Count functions and classes without docstrings
        missing_docs = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    missing_docs += 1
        
        result = {
            "file_path": file_path,
            "missing_docstrings": missing_docs,
            "message": f"Found {missing_docs} items without docstrings"
        }
        
        log_experiment(
            agent_name="Toolsmith",
            model_used="code_modifier",
            action=ActionType.ANALYSIS,
            details={
                "operation": "check_docstrings",
                "file_path": file_path,
                "input_prompt": f"Check docstrings: {file_path}",
                "output_response": json.dumps(result),
                "missing_count": missing_docs
            },
            status="SUCCESS"
        )
        
        return result
        
    except Exception as e:
        log_experiment(
            agent_name="Toolsmith",
            model_used="code_modifier",
            action=ActionType.DEBUG,
            details={
                "operation": "check_docstrings",
                "file_path": file_path,
                "input_prompt": f"Check docstrings: {file_path}",
                "output_response": f"Error: {str(e)}",
                "error": str(e)
            },
            status="FAILURE"
        )
        
        return {
            "file_path": file_path,
            "error": str(e)
        }


def get_code_metrics(file_path: str, sandbox_dir: str = "./sandbox") -> Dict:
    """
    Calculate code metrics for a file.
    
    Args:
        file_path: Path to Python file
        sandbox_dir: Sandbox root directory
        
    Returns:
        Dictionary with code metrics
    """
    is_safe_path(file_path, sandbox_dir)
    
    try:
        content = read_file(file_path, sandbox_dir)
        tree = ast.parse(content)
        
        # Count metrics
        lines = len(content.split('\n'))
        functions = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
        classes = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
        has_main = any(
            isinstance(node, ast.FunctionDef) and node.name == '__main__'
            for node in ast.walk(tree)
        )
        
        metrics = {
            "file_path": file_path,
            "lines_of_code": lines,
            "function_count": functions,
            "class_count": classes,
            "has_main": has_main,
            "complexity": "low" if functions + classes < 5 else "medium" if functions + classes < 15 else "high"
        }
        
        log_experiment(
            agent_name="Toolsmith",
            model_used="code_modifier",
            action=ActionType.ANALYSIS,
            details={
                "operation": "code_metrics",
                "file_path": file_path,
                "input_prompt": f"Calculate metrics: {file_path}",
                "output_response": json.dumps(metrics),
                "lines": lines,
                "functions": functions
            },
            status="SUCCESS"
        )
        
        return metrics
        
    except Exception as e:
        log_experiment(
            agent_name="Toolsmith",
            model_used="code_modifier",
            action=ActionType.DEBUG,
            details={
                "operation": "code_metrics",
                "file_path": file_path,
                "input_prompt": f"Calculate metrics: {file_path}",
                "output_response": f"Error: {str(e)}",
                "error": str(e)
            },
            status="FAILURE"
        )
        
        return {
            "file_path": file_path,
            "error": str(e)
        }


def compare_files(file_path1: str, file_path2: str, sandbox_dir: str = "./sandbox") -> Dict:
    """
    Compare two Python files.
    
    Args:
        file_path1: First file path
        file_path2: Second file path
        sandbox_dir: Sandbox root directory
        
    Returns:
        Dictionary with comparison results
    """
    is_safe_path(file_path1, sandbox_dir)
    is_safe_path(file_path2, sandbox_dir)
    
    try:
        content1 = read_file(file_path1, sandbox_dir)
        content2 = read_file(file_path2, sandbox_dir)
        
        same = content1 == content2
        
        metrics1 = get_code_metrics(file_path1, sandbox_dir)
        metrics2 = get_code_metrics(file_path2, sandbox_dir)
        
        comparison = {
            "file1": file_path1,
            "file2": file_path2,
            "identical": same,
            "file1_lines": metrics1.get("lines_of_code", 0),
            "file2_lines": metrics2.get("lines_of_code", 0),
            "file1_functions": metrics1.get("function_count", 0),
            "file2_functions": metrics2.get("function_count", 0)
        }
        
        log_experiment(
            agent_name="Toolsmith",
            model_used="code_modifier",
            action=ActionType.ANALYSIS,
            details={
                "operation": "compare_files",
                "file1": file_path1,
                "file2": file_path2,
                "input_prompt": f"Compare files: {file_path1} vs {file_path2}",
                "output_response": json.dumps(comparison),
                "identical": same
            },
            status="SUCCESS"
        )
        
        return comparison
        
    except Exception as e:
        log_experiment(
            agent_name="Toolsmith",
            model_used="code_modifier",
            action=ActionType.DEBUG,
            details={
                "operation": "compare_files",
                "file1": file_path1,
                "file2": file_path2,
                "input_prompt": f"Compare files: {file_path1} vs {file_path2}",
                "output_response": f"Error: {str(e)}",
                "error": str(e)
            },
            status="FAILURE"
        )
        
        return {
            "file1": file_path1,
            "file2": file_path2,
            "error": str(e)
        }
