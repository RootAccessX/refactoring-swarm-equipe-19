# Logger Test Suite

## Overview
Comprehensive test suite for the `src/utils/logger.py` module, validating all logging functionality for the Refactoring Swarm project.

## Test Files

### 1. `test_logger.py` (Manual Testing)
Original manual test script that validates basic logger functionality.

**Run:**
```bash
python tests/logger/test_logger.py
```

**Tests:**
- Basic logging with required fields
- All ActionType enum values
- Mandatory field validation
- Statistics collection
- JSON file structure compliance

---

### 2. `test_logger_pytest.py` (Unit Tests)
Pytest-based unit tests for individual logger functions.

**Run:**
```bash
pytest tests/logger/test_logger_pytest.py -v
```

**Tests:**
- `test_basic_logging()` - Basic logging functionality
- `test_all_action_types()` - All ActionType values work correctly
- `test_missing_input_prompt()` - Validation of mandatory input_prompt
- `test_missing_output_response()` - Validation of mandatory output_response
- `test_extra_fields_preserved()` - Extra fields in details are preserved
- `test_json_file_structure()` - JSON file structure compliance
- `test_unique_ids()` - Each logged entry has unique UUID
- `test_get_experiment_stats()` - Statistics collection works

---

### 3. `test_logger_e2e.py` (End-to-End Tests)
End-to-end tests simulating complete workflows.

**Run:**
```bash
python tests/logger/test_logger_e2e.py
```

**Scenarios:**
- **Complete Refactoring Workflow**: Analysis → Fix Generation → Validation
- **Iterative Refinement**: Multiple improvement iterations
- **Error Handling Workflow**: Bug detection and fixes
- **Multi-Agent Collaboration**: Multiple agents working together

---

## Running All Tests

### Run all logger tests:
```bash
# Manual test
python tests/logger/test_logger.py

# End-to-end tests
python tests/logger/test_logger_e2e.py

# Pytest unit tests (if colorama issues are resolved)
pytest tests/logger/test_logger_pytest.py -v
```

### Run all tests together:
```bash
python tests/logger/test_logger.py && python tests/logger/test_logger_e2e.py
```

---

## Test Coverage

The test suite validates:

### ✅ Core Functionality
- [x] Basic logging with all required parameters
- [x] All ActionType enum values (ANALYSIS, GENERATION, DEBUG, FIX)
- [x] UUID generation for unique log IDs
- [x] Timestamp generation
- [x] JSON file creation and structure

### ✅ Validation
- [x] Mandatory field validation (input_prompt, output_response)
- [x] Empty details dict rejection
- [x] Missing required fields error handling

### ✅ Data Integrity
- [x] JSON structure compliance
- [x] Field presence validation
- [x] Extra field preservation
- [x] Unique ID generation

### ✅ Statistics
- [x] Total experiment count
- [x] Experiments by agent
- [x] Experiments by action type
- [x] Experiments by status

### ✅ Workflows
- [x] Complete refactoring workflows
- [x] Iterative refinement processes
- [x] Error detection and fixing
- [x] Multi-agent collaboration

---

## Test Results Summary

### Last Test Run: January 15, 2026

#### Manual Test (`test_logger.py`)
```
✅ Test logging basique
✅ Test de tous les ActionTypes
✅ Test validation (doit echouer)
✅ Statistiques
✅ Verification du fichier JSON
```

#### End-to-End Tests (`test_logger_e2e.py`)
```
✅ Complete Refactoring Workflow
✅ Iterative Refinement Process
✅ Error Handling Workflow
✅ Multi-Agent Collaboration
```

**All tests passed successfully!**

---

## Known Issues

### Pytest Colorama Buffer Issue
There is a known issue with pytest and colorama on Windows causing buffer detachment errors. This affects `test_logger_pytest.py` when run with pytest. The issue doesn't affect functionality and can be avoided by:
1. Running tests directly: `python tests/logger/test_logger_pytest.py`
2. Using the manual and E2E test scripts instead

---

## Adding New Tests

### To add a new unit test:
Edit `tests/logger/test_logger_pytest.py` and add a new test function:
```python
def test_your_new_test():
    """Test description"""
    log_id = log_experiment(
        agent_name="YourAgent",
        model_used="test-model",
        action=ActionType.ANALYSIS,
        details={"input_prompt": "test", "output_response": "result"}
    )
    assert log_id is not None
```

### To add a new E2E scenario:
Edit `tests/logger/test_logger_e2e.py` and add a new test function:
```python
def test_your_workflow():
    """Test your workflow description"""
    print("\n[E2E Test] Your Workflow")
    # Your workflow steps here
    print("  ✓ Workflow completed")
```

---

## Quick Reference

### ActionType Enum Values
```python
ActionType.ANALYSIS     # Audit, analysis, bug detection
ActionType.GENERATION   # Code generation, creation
ActionType.DEBUG        # Error analysis, debugging
ActionType.FIX          # Applying fixes, corrections
```

### Required Fields in Details
```python
details = {
    "input_prompt": "...",      # REQUIRED
    "output_response": "...",   # REQUIRED
    # ... any other custom fields
}
```

### Log File Location
```
logs/experiment_data.json
```

---

## Maintenance

- Test files should be run before each commit to Day 7+ branches
- All tests must pass before merging to main
- Add new tests when adding new logger functionality
- Update this README when test structure changes

---

**Last Updated**: January 15, 2026  
**Maintained by**: Data Manager (Day 7 - Testing Day)
