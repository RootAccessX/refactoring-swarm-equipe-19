"""
End-to-End Logger Tests

Tests complete workflows and system integration scenarios.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.logger import log_experiment, ActionType


def test_complete_refactoring_workflow():
    """Test logging a complete refactoring workflow"""
    print("\n[E2E Test] Complete Refactoring Workflow")
    
    # Phase 1: Analysis
    analysis_id = log_experiment(
        agent_name="AuditorAgent",
        model_used="gemini-2.0-flash",
        action=ActionType.ANALYSIS,
        details={
            "input_prompt": "Analyze Python file for code quality",
            "output_response": "Found 5 issues: duplicate code, unused variables, missing docstrings",
            "file_path": "sample.py",
            "issues_count": 5
        }
    )
    print(f"  ✓ Analysis logged: {analysis_id}")
    
    # Phase 2: Fix generation
    fix_id = log_experiment(
        agent_name="FixerAgent",
        model_used="gemini-2.0-flash",
        action=ActionType.GENERATION,
        details={
            "input_prompt": "Generate refactored code",
            "output_response": "Refactored code with all issues addressed",
            "file_path": "sample.py",
            "fixes_applied": 5
        }
    )
    print(f"  ✓ Fix generation logged: {fix_id}")
    
    # Phase 3: Analysis (validation check)
    validation_id = log_experiment(
        agent_name="JudgeAgent",
        model_used="gemini-2.0-flash",
        action=ActionType.ANALYSIS,
        details={
            "input_prompt": "Validate refactored code",
            "output_response": "All validation checks passed",
            "file_path": "sample.py",
            "tests_passed": True,
            "code_quality_score": 0.95
        }
    )
    print(f"  ✓ Validation logged: {validation_id}")
    
    # Verify all entries logged
    with open("logs/experiment_data.json", "r") as f:
        data = json.load(f)
    
    logged_ids = {exp["id"] for exp in data["experiments"]}
    assert analysis_id in logged_ids
    assert fix_id in logged_ids
    assert validation_id in logged_ids
    print("  ✓ All workflow steps verified in logs")


def test_iterative_refinement():
    """Test logging iterative refinement process"""
    print("\n[E2E Test] Iterative Refinement Process")
    
    iteration_ids = []
    for iteration in range(1, 4):
        log_id = log_experiment(
            agent_name="RefinementAgent",
            model_used="gemini-2.0-flash",
            action=ActionType.GENERATION,
            details={
                "input_prompt": f"Refine code - iteration {iteration}",
                "output_response": f"Refinement complete - quality improved by {iteration * 10}%",
                "iteration": iteration,
                "quality_improvement": iteration * 10
            }
        )
        iteration_ids.append(log_id)
        print(f"  ✓ Iteration {iteration} logged: {log_id}")
    
    # Verify all iterations
    with open("logs/experiment_data.json", "r") as f:
        data = json.load(f)
    
    for log_id in iteration_ids:
        assert any(exp["id"] == log_id for exp in data["experiments"])
    
    print("  ✓ All iteration steps verified in logs")


def test_error_handling_workflow():
    """Test logging error detection and handling"""
    print("\n[E2E Test] Error Handling Workflow")
    
    # Detect error
    debug_id = log_experiment(
        agent_name="AuditorAgent",
        model_used="gemini-2.0-flash",
        action=ActionType.DEBUG,
        details={
            "input_prompt": "Analyze test failures",
            "output_response": "Found 3 bugs: null pointer exception, off-by-one error, logic error",
            "bug_count": 3
        }
    )
    print(f"  ✓ Error detection logged: {debug_id}")
    
    # Fix errors
    fix_ids = []
    for bug_num in range(1, 4):
        fix_id = log_experiment(
            agent_name="FixerAgent",
            model_used="gemini-2.0-flash",
            action=ActionType.FIX,
            details={
                "input_prompt": f"Fix bug {bug_num}",
                "output_response": f"Bug {bug_num} fixed and tested successfully",
                "bug_number": bug_num
            }
        )
        fix_ids.append(fix_id)
        print(f"  ✓ Bug fix {bug_num} logged: {fix_id}")
    
    # Verify all logged
    with open("logs/experiment_data.json", "r") as f:
        data = json.load(f)
    
    logged_ids = {exp["id"] for exp in data["experiments"]}
    assert debug_id in logged_ids
    for fix_id in fix_ids:
        assert fix_id in logged_ids
    
    print("  ✓ Error handling workflow verified in logs")


def test_multi_agent_collaboration():
    """Test logging multi-agent collaboration"""
    print("\n[E2E Test] Multi-Agent Collaboration")
    
    agents = [
        ("AuditorAgent", ActionType.ANALYSIS, "Analyze code for issues"),
        ("FixerAgent", ActionType.GENERATION, "Generate fixes"),
        ("JudgeAgent", ActionType.ANALYSIS, "Judge and validate solutions")
    ]
    
    collaboration_logs = []
    for agent_name, action, prompt in agents:
        log_id = log_experiment(
            agent_name=agent_name,
            model_used="gemini-2.0-flash",
            action=action,
            details={
                "input_prompt": prompt,
                "output_response": f"Completed by {agent_name}",
                "agent_role": agent_name
            }
        )
        collaboration_logs.append(log_id)
        print(f"  ✓ {agent_name} logged: {log_id}")
    
    # Verify collaboration logged
    with open("logs/experiment_data.json", "r") as f:
        data = json.load(f)
    
    for log_id in collaboration_logs:
        assert any(exp["id"] == log_id for exp in data["experiments"])
    
    print("  ✓ Multi-agent collaboration verified in logs")


if __name__ == "__main__":
    print("=" * 70)
    print("END-TO-END LOGGER TESTS")
    print("=" * 70)
    
    try:
        test_complete_refactoring_workflow()
        test_iterative_refinement()
        test_error_handling_workflow()
        test_multi_agent_collaboration()
        
        print("\n" + "=" * 70)
        print("✅ ALL END-TO-END TESTS PASSED")
        print("=" * 70)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
