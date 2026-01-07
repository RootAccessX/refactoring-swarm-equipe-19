"""
Sandbox Manager - Security layer for safe code execution.
Prevents writes outside the sandbox directory.
"""

import os
from pathlib import Path
from typing import Optional


class SandboxManager:
    """
    Manages a secure sandbox environment for code refactoring.
    Ensures all file operations stay within the allowed directory.
    """
    
    def __init__(self, sandbox_root: str):
        """
        Initialize the sandbox manager.
        
        Args:
            sandbox_root: Root directory of the sandbox
        """
        self.sandbox_root = Path(sandbox_root).resolve()
        
        # Create sandbox if it doesn't exist
        self.sandbox_root.mkdir(parents=True, exist_ok=True)
    
    def is_safe_path(self, filepath: str) -> bool:
        """
        Check if a file path is within the sandbox.
        
        Args:
            filepath: Path to check
        
        Returns:
            True if path is safe (within sandbox), False otherwise
        """
        try:
            # Resolve to absolute path
            abs_path = Path(filepath).resolve()
            
            # Check if it's within sandbox
            try:
                abs_path.relative_to(self.sandbox_root)
                return True
            except ValueError:
                # Path is not relative to sandbox_root
                return False
        except Exception:
            return False
    
    def get_safe_path(self, filepath: str) -> Optional[Path]:
        """
        Get a safe path within the sandbox or None if unsafe.
        
        Args:
            filepath: Path to validate
        
        Returns:
            Path object if safe, None otherwise
        """
        if self.is_safe_path(filepath):
            return Path(filepath).resolve()
        return None
    
    def validate_write(self, filepath: str) -> bool:
        """
        Validate that a write operation is allowed.
        
        Args:
            filepath: Path to write to
        
        Returns:
            True if write is allowed, False otherwise
        
        Raises:
            SecurityError: If write is outside sandbox
        """
        if not self.is_safe_path(filepath):
            raise SecurityError(
                f"Security violation: Attempted to write outside sandbox.\n"
                f"Sandbox root: {self.sandbox_root}\n"
                f"Attempted path: {filepath}"
            )
        return True
    
    def validate_read(self, filepath: str) -> bool:
        """
        Validate that a read operation is allowed.
        
        Args:
            filepath: Path to read from
        
        Returns:
            True if read is allowed, False otherwise
        
        Raises:
            SecurityError: If read is outside sandbox
        """
        if not self.is_safe_path(filepath):
            raise SecurityError(
                f"Security violation: Attempted to read outside sandbox.\n"
                f"Sandbox root: {self.sandbox_root}\n"
                f"Attempted path: {filepath}"
            )
        return True
    
    def list_files(self, pattern: str = "*.py") -> list:
        """
        List files in the sandbox matching a pattern.
        
        Args:
            pattern: Glob pattern (default: *.py)
        
        Returns:
            List of Path objects
        """
        return list(self.sandbox_root.rglob(pattern))
    
    def get_sandbox_root(self) -> Path:
        """Get the sandbox root directory."""
        return self.sandbox_root
    
    def create_subdirectory(self, subdir: str) -> Path:
        """
        Create a subdirectory within the sandbox.
        
        Args:
            subdir: Name of subdirectory
        
        Returns:
            Path to created directory
        
        Raises:
            SecurityError: If path would be outside sandbox
        """
        target_dir = self.sandbox_root / subdir
        
        if not self.is_safe_path(str(target_dir)):
            raise SecurityError(f"Cannot create directory outside sandbox: {subdir}")
        
        target_dir.mkdir(parents=True, exist_ok=True)
        return target_dir


class SecurityError(Exception):
    """Raised when a security violation is detected."""
    pass
