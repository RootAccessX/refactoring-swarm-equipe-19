"""
Comprehensive Logger Tests - Pytest Suite

Tests for src/utils/logger.py functionality including:
- Basic logging
- Action type validation
- Field validation
- JSON structure compliance
"""

import json
import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.logger import log_experiment, ActionType, get_experiment_stats


def test_basic_logging():
    """Test basic logging functionality"""
    log_id = log_experiment(
        agent_name="TestAgent",
        model_used="test-model",
        action=ActionType.ANALYSIS,
        details={"input_prompt": "test", "output_response": "result"}
    )
    assert log_id is not None
    assert isinstance(log_id, str)
    assert len(log_id) > 0


def test_all_action_types():
    """Test all ActionType enum values"""
    for action in ActionType:
        log_id = log_experiment(
            agent_name="ActionTypeTest",
            model_used="test",
            action=action,
            details={"input_prompt": f"test {action.value}", "output_response": "ok"}
        )
        assert log_id is not None


def test_missing_input_prompt():
    """Test validation of mandatory input_prompt field"""
    with pytest.raises(ValueError):
        log_experiment(
            agent_name="Test",
            model_used="test",
            action=ActionType.ANALYSIS,
            details={"output_response": "response"}
        )


def test_missing_output_response():
    """Test validation of mandatory output_response field"""
    with pytest.raises(ValueError):
        log_experiment(
            agent_name="Test",
            model_used="test",
            action=ActionType.ANALYSIS,
            details={"input_prompt": "prompt"}
        )


def test_extra_fields_preserved():
    """Test that extra fields in details are preserved"""
    log_id = log_experiment(
        agent_name="ExtraFieldTest",
        model_used="test",
        action=ActionType.DEBUG,
        details={
            "input_prompt": "debug",
            "output_response": "fixed",
            "severity": "HIGH",
            "line_number": 42
        }
    )
    
    with open("logs/experiment_data.json", "r") as f:
        data = json.load(f)
    
    for exp in data["experiments"]:
        if exp["id"] == log_id:
            assert exp["details"]["severity"] == "HIGH"
            assert exp["details"]["line_number"] == 42


def test_json_file_structure():
    """Test JSON file structure compliance"""
    log_experiment(
        agent_name="StructureTest",
        model_used="test",
        action=ActionType.ANALYSIS,
        details={"input_prompt": "test", "output_response": "result"}
    )
    
    with open("logs/experiment_data.json", "r") as f:
        data = json.load(f)
    
    assert isinstance(data, dict)
    assert "experiments" in data
    assert isinstance(data["experiments"], list)
    
    if len(data["experiments"]) > 0:
        exp = data["experiments"][-1]
        assert "id" in exp
        assert "timestamp" in exp
        assert "agent_name" in exp
        assert "model_used" in exp
        assert "action" in exp
        assert "details" in exp
        assert "status" in exp


def test_unique_ids():
    """Test that logged entries have unique IDs"""
    ids = []
    for i in range(5):
        log_id = log_experiment(
            agent_name=f"UniqueTest{i}",
            model_used="test",
            action=ActionType.ANALYSIS,
            details={"input_prompt": f"test{i}", "output_response": f"result{i}"}
        )
        ids.append(log_id)
    
    assert len(ids) == len(set(ids))


def test_get_experiment_stats():
    """Test statistics collection"""
    log_experiment(
        agent_name="StatsTest",
        model_used="test",
        action=ActionType.ANALYSIS,
        details={"input_prompt": "test", "output_response": "result"}
    )
    
    stats = get_experiment_stats()
    assert stats is not None
    assert isinstance(stats, dict)
    assert "total_experiments" in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
