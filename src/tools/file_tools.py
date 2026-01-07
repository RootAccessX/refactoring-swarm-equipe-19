"""
File Tools - Safe read/write operations for the Refactoring Swarm.
Provides controlled file I/O with security checks.
"""

import os
from pathlib import Path
from typing import List, Optional


def read_file(filepath: str) -> str:
    """
    Safely read a file's contents.
    
    Args:
        filepath: Path to the file to read
    
    Returns:
        File contents as string
    
    Raises:
        FileNotFoundError: If file doesn't exist
        IOError: If file cannot be read
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")
    except Exception as e:
        raise IOError(f"Error reading file {filepath}: {str(e)}")


def write_file(filepath: str, content: str) -> bool:
    """
    Safely write content to a file.
    
    Args:
        filepath: Path to the file to write
        content: Content to write
    
    Returns:
        True if successful
    
    Raises:
        IOError: If file cannot be written
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        raise IOError(f"Error writing file {filepath}: {str(e)}")


def list_python_files(directory: str) -> List[Path]:
    """
    Recursively list all Python files in a directory.
    
    Args:
        directory: Path to directory to search
    
    Returns:
        List of Path objects pointing to .py files
    """
    path = Path(directory)
    if not path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    if not path.is_dir():
        raise ValueError(f"Not a directory: {directory}")
    
    # Find all .py files recursively
    python_files = list(path.rglob("*.py"))
    
    # Filter out __pycache__ and virtual environment files
    python_files = [
        f for f in python_files 
        if '__pycache__' not in f.parts and 'venv' not in f.parts
    ]
    
    return python_files


def file_exists(filepath: str) -> bool:
    """
    Check if a file exists.
    
    Args:
        filepath: Path to check
    
    Returns:
        True if file exists, False otherwise
    """
    return os.path.exists(filepath) and os.path.isfile(filepath)


def backup_file(filepath: str, backup_suffix: str = ".backup") -> Optional[str]:
    """
    Create a backup copy of a file before modifying it.
    
    Args:
        filepath: Path to file to backup
        backup_suffix: Suffix to add to backup filename
    
    Returns:
        Path to backup file if successful, None otherwise
    """
    if not file_exists(filepath):
        return None
    
    backup_path = filepath + backup_suffix
    try:
        content = read_file(filepath)
        write_file(backup_path, content)
        return backup_path
    except Exception:
        return None
