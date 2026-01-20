# Toolsmith API Documentation

## Table of Contents

1. [Overview](#overview)
2. [Security Layer](#security-layer)
3. [File Operations](#file-operations)
4. [Code Analysis](#code-analysis)
5. [Testing Tools](#testing-tools)
6. [Code Modification](#code-modification)
7. [Error Handling](#error-handling)
8. [Usage Examples](#usage-examples)

---

## Overview

This document provides comprehensive documentation for all tools developed by the Toolsmith team. These tools form the core API that enables agents to perform file operations, code analysis, testing, and modifications within a secure sandbox environment.

### Design Principles

- **Sandbox Security**: All file operations are restricted to the `./sandbox` directory
- **Automatic Logging**: Every operation is logged via `log_experiment()` for research data collection
- **Error Handling**: All tools implement robust error handling with descriptive messages
- **Type Safety**: All functions include type hints and return structured dictionaries

---

## Security Layer

### Module: `src.tools.sandbox_manager`

#### SecurityError

```python
class SecurityError(Exception):
    """Raised when a file operation violates sandbox restrictions"""
```

Custom exception raised when attempting to access files outside the sandbox directory.

#### is_path_in_sandbox

```python
def is_path_in_sandbox(path: str, sandbox_dir: str = "./sandbox") -> bool
```

Validates that a given path is strictly within the sandbox directory. This function protects against path traversal attacks, symbolic link exploits, and directory name spoofing.

**Parameters:**
- `path` (str): The file or directory path to validate
- `sandbox_dir` (str, optional): Root directory of the sandbox. Default: `"./sandbox"`

**Returns:**
- `bool`: `True` if the path is valid and within sandbox

**Raises:**
- `SecurityError`: If the path resolves outside the sandbox directory

**Security Features:**
- Resolves symbolic links using `os.path.realpath()`
- Normalizes paths to prevent `..` traversal attacks
- Validates path prefix with directory separator to prevent false positives
- Cross-platform compatible (Windows/Linux/macOS)

**Example:**

```python
from src.tools.sandbox_manager import is_path_in_sandbox, SecurityError

# Valid path
is_path_in_sandbox("./sandbox/test_dataset/file.py")  # Returns: True

# Invalid path - raises SecurityError
try:
    is_path_in_sandbox("../etc/passwd")
except SecurityError as e:
    print(f"Access denied: {e}")
```

---

## File Operations

### Module: `src.tools.file_tools`

#### read_file

```python
def read_file(file_path: str, sandbox_dir: str = "./sandbox") -> str
```

Reads the contents of a Python file from within the sandbox.

**Parameters:**
- `file_path` (str): Path to the file to read
- `sandbox_dir` (str, optional): Sandbox root directory. Default: `"./sandbox"`

**Returns:**
- `str`: Complete file content as a string

**Raises:**
- `SecurityError`: If file path is outside sandbox
- `FileNotFoundError`: If the specified file does not exist

**Logging:**
- Agent: "Toolsmith"
- Action: `ActionType.ANALYSIS`
- Details: File path, size, operation status

**Example:**

```python
from src.tools.file_tools import read_file

content = read_file("./sandbox/test_dataset/ok_code.py")
print(f"File contains {len(content)} characters")
```

#### write_file

```python
def write_file(file_path: str, content: str, sandbox_dir: str = "./sandbox") -> bool
```

Writes content to a file within the sandbox. Creates parent directories if they do not exist.

**Parameters:**
- `file_path` (str): Destination file path
- `content` (str): Content to write to the file
- `sandbox_dir` (str, optional): Sandbox root directory. Default: `"./sandbox"`

**Returns:**
- `bool`: `True` if write operation succeeds

**Raises:**
- `SecurityError`: If file path is outside sandbox
- `Exception`: Any file I/O errors encountered during write operation

**Logging:**
- Agent: "Toolsmith"
- Action: `ActionType.FIX`
- Details: File path, bytes written, operation status

**Example:**

```python
from src.tools.file_tools import write_file

fixed_code = '''def hello():
    """Say hello."""
    print("Hello, World!")
'''

success = write_file("./sandbox/fixed_code.py", fixed_code)
```

#### list_files

```python
def list_files(directory: str, sandbox_dir: str = "./sandbox") -> List[str]
```

Lists all Python files (`.py` extension) within a directory, including subdirectories.

**Parameters:**
- `directory` (str): Directory to scan for Python files
- `sandbox_dir` (str, optional): Sandbox root directory. Default: `"./sandbox"`

**Returns:**
- `List[str]`: List of file paths (strings) for all `.py` files found

**Raises:**
- `SecurityError`: If directory is outside sandbox
- `NotADirectoryError`: If the path is not a valid directory

**Logging:**
- Agent: "Toolsmith"
- Action: `ActionType.ANALYSIS`
- Details: Directory path, file count

**Example:**

```python
from src.tools.file_tools import list_files

files = list_files("./sandbox/test_dataset")
for file_path in files:
    print(f"Found: {file_path}")
```

---

## Code Analysis

### Module: `src.tools.pylint_tool`

#### run_pylint_analysis

```python
def run_pylint_analysis(file_path: str, sandbox_dir: str = "./sandbox") -> Dict
```

Performs static code analysis using pylint to identify code quality issues, style violations, and potential errors.

**Parameters:**
- `file_path` (str): Path to the Python file to analyze
- `sandbox_dir` (str, optional): Sandbox root directory. Default: `"./sandbox"`

**Returns:**
- `Dict`: Analysis results containing:
  - `file` (str): Path of the analyzed file
  - `score` (float): Pylint score out of 10
  - `total_issues` (int): Total number of issues detected
  - `errors` (int): Number of error-level issues
  - `warnings` (int): Number of warning-level issues
  - `issues` (List): First 20 issues (full details)
  - `issues_detail` (List[Dict]): First 10 issues with structured data:
    - `line` (int): Line number
    - `column` (int): Column number
    - `type` (str): Issue type (error/warning/convention/refactor)
    - `symbol` (str): Pylint message symbol
    - `message` (str): Human-readable description

**Timeout:**
- Maximum execution time: 30 seconds
- Returns error dict if timeout is exceeded

**Logging:**
- Agent: "Toolsmith"
- Action: `ActionType.ANALYSIS`
- Details: File path, score, issue count

**Example:**

```python
from src.tools.pylint_tool import run_pylint_analysis

result = run_pylint_analysis("./sandbox/test_dataset/bad_code.py")
print(f"Quality Score: {result['score']}/10")
print(f"Total Issues: {result['total_issues']}")

for issue in result['issues_detail']:
    print(f"Line {issue['line']}: {issue['message']}")
```

---

## Testing Tools

### Module: `src.tools.pytest_tool`

#### run_pytest

```python
def run_pytest(directory: str, sandbox_dir: str = "./sandbox") -> Dict
```

Executes all pytest test files in the specified directory and returns comprehensive test results.

**Parameters:**
- `directory` (str): Directory containing test files
- `sandbox_dir` (str, optional): Sandbox root directory. Default: `"./sandbox"`

**Returns:**
- `Dict`: Test execution results containing:
  - `directory` (str): Tested directory path
  - `passed` (int): Number of tests that passed
  - `failed` (int): Number of tests that failed
  - `skipped` (int): Number of skipped tests
  - `total` (int): Total number of tests executed
  - `success_rate` (float): Percentage of tests passed (0-100)
  - `exit_code` (int): Pytest exit code (0 = success)
  - `tests` (List[Dict]): Individual test results with name and status
  - `error_log` (str): Full error output if failures occurred

**Timeout:**
- Maximum execution time: 60 seconds

**Logging:**
- Agent: "Toolsmith"
- Action: `ActionType.ANALYSIS`
- Details: Directory, test counts, success rate

**Example:**

```python
from src.tools.pytest_tool import run_pytest

results = run_pytest("./sandbox/test_dataset")
print(f"Results: {results['passed']}/{results['total']} tests passed")
print(f"Success Rate: {results['success_rate']}%")

if results['failed'] > 0:
    print("Error Log:")
    print(results['error_log'])
```

#### run_single_test

```python
def run_single_test(
    test_file: str,
    test_name: str = None,
    sandbox_dir: str = "./sandbox"
) -> Dict
```

Executes a specific test file or a single test function within a file.

**Parameters:**
- `test_file` (str): Path to the test file
- `test_name` (str, optional): Name of specific test function to run
- `sandbox_dir` (str, optional): Sandbox root directory. Default: `"./sandbox"`

**Returns:**
- `Dict`: Test results containing:
  - `test_file` (str): Path to test file
  - `test_name` (str or None): Name of specific test
  - `passed` (int): Number of tests passed
  - `failed` (int): Number of tests failed
  - `success` (bool): `True` if all tests passed
  - `output` (str): Complete pytest output

**Timeout:**
- Maximum execution time: 30 seconds

**Example:**

```python
from src.tools.pytest_tool import run_single_test

# Run all tests in a file
result = run_single_test("./sandbox/test_dataset/test_ok_code.py")

# Run specific test function
result = run_single_test(
    "./sandbox/test_dataset/test_ok_code.py",
    test_name="test_addition"
)

if result['success']:
    print("Test passed successfully")
```

#### get_failing_tests

```python
def get_failing_tests(directory: str, sandbox_dir: str = "./sandbox") -> Dict
```

Retrieves detailed information about failed tests in a directory.

**Parameters:**
- `directory` (str): Directory containing tests
- `sandbox_dir` (str, optional): Sandbox root directory. Default: `"./sandbox"`

**Returns:**
- `Dict`: Failure information containing:
  - `failed_count` (int): Number of failed tests
  - `failing_tests` (List[Dict]): Details of each failed test
  - `error_log` (str): Complete error output

**Example:**

```python
from src.tools.pytest_tool import get_failing_tests

failures = get_failing_tests("./sandbox/test_dataset")
print(f"Failed: {failures['failed_count']} tests")

for test in failures['failing_tests']:
    print(f"- {test['name']}: {test['status']}")
```

---

## Code Modification

### Module: `src.tools.code_modifier`

#### validate_python_syntax

```python
def validate_python_syntax(code: str) -> None
```

Validates Python code syntax without executing it.

**Parameters:**
- `code` (str): Python code to validate

**Returns:**
- `None`: Returns nothing if syntax is valid

**Raises:**
- `SyntaxError`: If the code contains syntax errors

**Example:**

```python
from src.tools.code_modifier import validate_python_syntax

code = '''
def hello():
    print("Hello")
'''

try:
    validate_python_syntax(code)
    print("Syntax is valid")
except SyntaxError as e:
    print(f"Syntax error: {e}")
```

#### apply_fix

```python
def apply_fix(
    file_path: str,
    fixed_code: str,
    sandbox_dir: str = "./sandbox"
) -> Dict
```

Applies a code fix to a file after validating syntax. Reads the original file, validates the new code, and writes the fixed version.

**Parameters:**
- `file_path` (str): Path to file to be fixed
- `fixed_code` (str): Corrected code content
- `sandbox_dir` (str, optional): Sandbox root directory. Default: `"./sandbox"`

**Returns:**
- `Dict`: Fix operation results containing:
  - `file_path` (str): Path to modified file
  - `original_size` (int): Size of original content in characters
  - `new_size` (int): Size of new content in characters
  - `size_change` (int): Difference in size (new - original)

**Raises:**
- `SecurityError`: If file path is outside sandbox
- `SyntaxError`: If fixed code has syntax errors

**Logging:**
- Agent: "Toolsmith"
- Action: `ActionType.FIX`
- Details: File path, size changes

**Example:**

```python
from src.tools.code_modifier import apply_fix

fixed_code = '''
def calculate_sum(a: int, b: int) -> int:
    """Calculate the sum of two numbers.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Sum of a and b
    """
    return a + b
'''

result = apply_fix("./sandbox/test_dataset/bad_code.py", fixed_code)
print(f"File modified: {result['size_change']} characters changed")
```

#### add_docstring

```python
def add_docstring(file_path: str, sandbox_dir: str = "./sandbox") -> Dict
```

Analyzes a Python file to count missing docstrings in functions and classes.

**Parameters:**
- `file_path` (str): Path to file to analyze
- `sandbox_dir` (str, optional): Sandbox root directory. Default: `"./sandbox"`

**Returns:**
- `Dict`: Docstring analysis containing:
  - `file_path` (str): Path to analyzed file
  - `missing_docstrings` (int): Count of functions/classes without docstrings

**Example:**

```python
from src.tools.code_modifier import add_docstring

result = add_docstring("./sandbox/test_dataset/bad_code.py")
print(f"Missing docstrings: {result['missing_docstrings']}")
```

#### get_code_metrics

```python
def get_code_metrics(file_path: str, sandbox_dir: str = "./sandbox") -> Dict
```

Computes basic code metrics for a Python file.

**Parameters:**
- `file_path` (str): Path to file to analyze
- `sandbox_dir` (str, optional): Sandbox root directory. Default: `"./sandbox"`

**Returns:**
- `Dict`: Code metrics containing:
  - `file_path` (str): Path to analyzed file
  - `lines_of_code` (int): Total lines in file
  - `functions` (int): Number of function definitions
  - `classes` (int): Number of class definitions
  - `has_main` (bool): Whether file has `if __name__ == "__main__"` block

**Example:**

```python
from src.tools.code_modifier import get_code_metrics

metrics = get_code_metrics("./sandbox/test_dataset/ok_code.py")
print(f"Lines: {metrics['lines_of_code']}")
print(f"Functions: {metrics['functions']}")
print(f"Classes: {metrics['classes']}")
```

---

## Error Handling

### Common Exceptions

All tools implement consistent error handling:

1. **SecurityError**
   - Raised when: File path is outside sandbox
   - Resolution: Ensure all paths start with `./sandbox/`

2. **FileNotFoundError**
   - Raised when: Target file does not exist
   - Resolution: Verify file path or create file first

3. **NotADirectoryError**
   - Raised when: Path expected to be directory is not
   - Resolution: Check path and ensure it points to directory

4. **SyntaxError**
   - Raised when: Python code has invalid syntax
   - Resolution: Fix syntax errors before applying changes

5. **TimeoutExpired**
   - Raised when: pylint or pytest execution exceeds timeout
   - Resolution: Simplify test cases or increase timeout limits

### Error Response Format

When an error occurs, tools return a structured error dictionary:

```python
{
    "error": "Description of what went wrong",
    "file_path": "Path to file (if applicable)",
    "operation": "Name of failed operation",
    # ... other relevant fields set to default values
}
```

---

## Usage Examples

### Complete Workflow Example

```python
from src.tools.file_tools import list_files, read_file, write_file
from src.tools.pylint_tool import run_pylint_analysis
from src.tools.pytest_tool import run_pytest
from src.tools.code_modifier import apply_fix, validate_python_syntax

# Step 1: List all Python files in dataset
dataset_dir = "./sandbox/dataset_inconnu"
files = list_files(dataset_dir)
print(f"Found {len(files)} Python files")

# Step 2: Analyze first file
if files:
    target_file = files[0]
    
    # Read original content
    original_code = read_file(target_file)
    
    # Analyze code quality
    analysis = run_pylint_analysis(target_file)
    print(f"Initial score: {analysis['score']}/10")
    print(f"Issues found: {analysis['total_issues']}")
    
    # Step 3: Apply fix (example - agent would generate this)
    fixed_code = """
def example_function(param: str) -> str:
    \"\"\"Example function with proper documentation.
    
    Args:
        param: Input parameter
        
    Returns:
        Processed result
    \"\"\"
    return param.upper()
"""
    
    # Validate before applying
    try:
        validate_python_syntax(fixed_code)
        result = apply_fix(target_file, fixed_code)
        print(f"Fix applied: {result['size_change']} chars changed")
    except SyntaxError as e:
        print(f"Invalid syntax: {e}")
    
    # Step 4: Re-analyze to verify improvement
    new_analysis = run_pylint_analysis(target_file)
    print(f"New score: {new_analysis['score']}/10")
    
    # Step 5: Run tests
    test_results = run_pytest(dataset_dir)
    print(f"Tests: {test_results['passed']}/{test_results['total']} passed")
    print(f"Success rate: {test_results['success_rate']}%")
```

### Integration with Agents

```python
# Example: Auditor Agent using tools
from src.tools.file_tools import list_files, read_file
from src.tools.pylint_tool import run_pylint_analysis
from src.utils.logger import log_experiment, ActionType

def audit_directory(directory: str) -> dict:
    """Audit all files in directory."""
    files = list_files(directory)
    issues_summary = []
    
    for file_path in files:
        analysis = run_pylint_analysis(file_path)
        
        if analysis['score'] < 7.0:
            issues_summary.append({
                'file': file_path,
                'score': analysis['score'],
                'issues': analysis['total_issues']
            })
    
    return {
        'total_files': len(files),
        'files_with_issues': len(issues_summary),
        'details': issues_summary
    }
```

---

## Version Information

- **API Version**: 1.0
- **Python Compatibility**:  3.11
- **Dependencies**: pylint, pytest
- **Sandbox Default**: `./sandbox`

## Support

For issues or questions regarding the Toolsmith API, contact the Toolsmith  or refer to the main project documentation.
