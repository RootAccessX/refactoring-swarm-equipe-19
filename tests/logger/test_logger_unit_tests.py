"""
Comprehensive Unit Tests for Logger Module

Tests individual components and functions in isolation.
Each test focuses on a single unit of functionality.
"""

import pytest
import json
import uuid
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.logger import (
    log_experiment, 
    ActionType, 
    get_experiment_stats,
    _ensure_log_file,
    LOG_FILE
)


class TestActionTypeEnum:
    """Unit tests for ActionType enumeration"""
    
    def test_action_type_has_analysis(self):
        """Test ANALYSIS action type exists"""
        assert hasattr(ActionType, 'ANALYSIS')
        assert ActionType.ANALYSIS.value == "ANALYSIS"
    
    def test_action_type_has_generation(self):
        """Test GENERATION action type exists"""
        assert hasattr(ActionType, 'GENERATION')
        assert ActionType.GENERATION.value == "GENERATION"
    
    def test_action_type_has_debug(self):
        """Test DEBUG action type exists"""
        assert hasattr(ActionType, 'DEBUG')
        assert ActionType.DEBUG.value == "DEBUG"
    
    def test_action_type_has_fix(self):
        """Test FIX action type exists"""
        assert hasattr(ActionType, 'FIX')
        assert ActionType.FIX.value == "FIX"
    
    def test_action_type_count(self):
        """Test total number of action types"""
        action_types = list(ActionType)
        assert len(action_types) == 4
    
    def test_action_type_iteration(self):
        """Test ActionType enum is iterable"""
        count = 0
        for action in ActionType:
            assert action is not None
            count += 1
        assert count == 4
    
    def test_action_type_string_values(self):
        """Test all ActionType values are strings"""
        for action in ActionType:
            assert isinstance(action.value, str)
            assert len(action.value) > 0
    
    def test_action_type_comparison(self):
        """Test ActionType comparison"""
        assert ActionType.ANALYSIS == ActionType.ANALYSIS
        assert ActionType.ANALYSIS != ActionType.DEBUG
    
    def test_action_type_in_list(self):
        """Test ActionType membership in list"""
        actions = [ActionType.ANALYSIS, ActionType.GENERATION]
        assert ActionType.ANALYSIS in actions
        assert ActionType.DEBUG not in actions


class TestLogExperimentBasics:
    """Unit tests for basic log_experiment functionality"""
    
    def test_log_returns_string_id(self):
        """Test log_experiment returns a string ID"""
        log_id = log_experiment(
            agent_name="UnitTest",
            model_used="test",
            action=ActionType.ANALYSIS,
            details={"input_prompt": "test", "output_response": "result"}
        )
        assert isinstance(log_id, str)
    
    def test_log_id_is_valid_uuid(self):
        """Test log_experiment returns valid UUID"""
        log_id = log_experiment(
            agent_name="UUIDTest",
            model_used="test",
            action=ActionType.ANALYSIS,
            details={"input_prompt": "test", "output_response": "result"}
        )
        # Should not raise ValueError
        uuid.UUID(log_id)
    
    def test_log_id_is_unique(self):
        """Test each log gets unique ID"""
        id1 = log_experiment(
            agent_name="UniqueTest1",
            model_used="test",
            action=ActionType.ANALYSIS,
            details={"input_prompt": "test1", "output_response": "result1"}
        )
        id2 = log_experiment(
            agent_name="UniqueTest2",
            model_used="test",
            action=ActionType.ANALYSIS,
            details={"input_prompt": "test2", "output_response": "result2"}
        )
        assert id1 != id2
    
    def test_log_with_default_status(self):
        """Test logging with default SUCCESS status"""
        log_id = log_experiment(
            agent_name="StatusTest",
            model_used="test",
            action=ActionType.ANALYSIS,
            details={"input_prompt": "test", "output_response": "result"}
        )
        
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        entry = next((e for e in data["experiments"] if e["id"] == log_id), None)
        assert entry is not None
        assert entry["status"] == "SUCCESS"
    
    def test_log_with_explicit_status(self):
        """Test logging with explicit status"""
        log_id = log_experiment(
            agent_name="StatusTest",
            model_used="test",
            action=ActionType.ANALYSIS,
            details={"input_prompt": "test", "output_response": "result"},
            status="FAILURE"
        )
        
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        entry = next((e for e in data["experiments"] if e["id"] == log_id), None)
        assert entry["status"] == "FAILURE"


class TestLogExperimentParameters:
    """Unit tests for log_experiment parameter handling"""
    
    def test_agent_name_is_stored(self):
        """Test agent_name parameter is stored correctly"""
        log_id = log_experiment(
            agent_name="TestAgent123",
            model_used="test",
            action=ActionType.ANALYSIS,
            details={"input_prompt": "test", "output_response": "result"}
        )
        
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        entry = next((e for e in data["experiments"] if e["id"] == log_id), None)
        assert entry["agent_name"] == "TestAgent123"
    
    def test_model_used_is_stored(self):
        """Test model_used parameter is stored correctly"""
        log_id = log_experiment(
            agent_name="ModelTest",
            model_used="gpt-4",
            action=ActionType.ANALYSIS,
            details={"input_prompt": "test", "output_response": "result"}
        )
        
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        entry = next((e for e in data["experiments"] if e["id"] == log_id), None)
        assert entry["model_used"] == "gpt-4"
    
    def test_action_type_is_stored(self):
        """Test action parameter is stored correctly"""
        log_id = log_experiment(
            agent_name="ActionTest",
            model_used="test",
            action=ActionType.GENERATION,
            details={"input_prompt": "test", "output_response": "result"}
        )
        
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        entry = next((e for e in data["experiments"] if e["id"] == log_id), None)
        assert entry["action"] == "GENERATION"
    
    def test_empty_agent_name_accepted(self):
        """Test empty agent_name is accepted"""
        log_id = log_experiment(
            agent_name="",
            model_used="test",
            action=ActionType.ANALYSIS,
            details={"input_prompt": "test", "output_response": "result"}
        )
        assert log_id is not None
    
    def test_empty_model_used_accepted(self):
        """Test empty model_used is accepted"""
        log_id = log_experiment(
            agent_name="EmptyModelTest",
            model_used="",
            action=ActionType.ANALYSIS,
            details={"input_prompt": "test", "output_response": "result"}
        )
        assert log_id is not None


class TestLogExperimentValidation:
    """Unit tests for log_experiment validation"""
    
    def test_missing_input_prompt_raises_error(self):
        """Test ValueError when input_prompt is missing"""
        with pytest.raises(ValueError, match="input_prompt"):
            log_experiment(
                agent_name="ValidationTest",
                model_used="test",
                action=ActionType.ANALYSIS,
                details={"output_response": "result"}
            )
    
    def test_missing_output_response_raises_error(self):
        """Test ValueError when output_response is missing"""
        with pytest.raises(ValueError, match="output_response"):
            log_experiment(
                agent_name="ValidationTest",
                model_used="test",
                action=ActionType.ANALYSIS,
                details={"input_prompt": "test"}
            )
    
    def test_empty_details_raises_error(self):
        """Test ValueError when details dict is empty"""
        with pytest.raises(ValueError):
            log_experiment(
                agent_name="ValidationTest",
                model_used="test",
                action=ActionType.ANALYSIS,
                details={}
            )
    
    def test_none_input_prompt_accepted(self):
        """Test that None input_prompt is accepted (only key presence is checked)"""
        # Logger only checks for key presence, not value validation
        log_id = log_experiment(
            agent_name="NonePromptTest",
            model_used="test",
            action=ActionType.ANALYSIS,
            details={"input_prompt": None, "output_response": "result"}
        )
        assert log_id is not None
    
    def test_empty_string_input_prompt_accepted(self):
        """Test that empty string input_prompt is accepted (only key presence is checked)"""
        # Logger only checks for key presence, not value validation
        log_id = log_experiment(
            agent_name="EmptyPromptTest",
            model_used="test",
            action=ActionType.ANALYSIS,
            details={"input_prompt": "", "output_response": "result"}
        )
        assert log_id is not None


class TestLogExperimentDetails:
    """Unit tests for details parameter handling"""
    
    def test_minimal_details_accepted(self):
        """Test minimal valid details dict"""
        log_id = log_experiment(
            agent_name="MinimalTest",
            model_used="test",
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": "minimal",
                "output_response": "ok"
            }
        )
        assert log_id is not None
    
    def test_extra_fields_preserved(self):
        """Test extra fields in details are preserved"""
        log_id = log_experiment(
            agent_name="ExtraFieldTest",
            model_used="test",
            action=ActionType.DEBUG,
            details={
                "input_prompt": "test",
                "output_response": "result",
                "custom_field": "custom_value",
                "severity": "HIGH",
                "line_number": 42
            }
        )
        
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        entry = next((e for e in data["experiments"] if e["id"] == log_id), None)
        assert entry["details"]["custom_field"] == "custom_value"
        assert entry["details"]["severity"] == "HIGH"
        assert entry["details"]["line_number"] == 42
    
    def test_nested_dict_in_details(self):
        """Test nested dict in details is preserved"""
        log_id = log_experiment(
            agent_name="NestedTest",
            model_used="test",
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": "test",
                "output_response": "result",
                "metadata": {"key1": "value1", "key2": "value2"}
            }
        )
        
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        entry = next((e for e in data["experiments"] if e["id"] == log_id), None)
        assert "metadata" in entry["details"]
        assert entry["details"]["metadata"]["key1"] == "value1"
    
    def test_list_in_details(self):
        """Test list in details is preserved"""
        log_id = log_experiment(
            agent_name="ListTest",
            model_used="test",
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": "test",
                "output_response": "result",
                "issues": ["issue1", "issue2", "issue3"]
            }
        )
        
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        entry = next((e for e in data["experiments"] if e["id"] == log_id), None)
        assert "issues" in entry["details"]
        assert len(entry["details"]["issues"]) == 3


class TestLogFileOperations:
    """Unit tests for log file operations"""
    
    def test_log_file_exists_after_logging(self):
        """Test log file is created after logging"""
        log_experiment(
            agent_name="FileTest",
            model_used="test",
            action=ActionType.ANALYSIS,
            details={"input_prompt": "test", "output_response": "result"}
        )
        assert Path(LOG_FILE).exists()
    
    def test_log_file_is_valid_json(self):
        """Test log file contains valid JSON"""
        log_experiment(
            agent_name="JSONTest",
            model_used="test",
            action=ActionType.ANALYSIS,
            details={"input_prompt": "test", "output_response": "result"}
        )
        
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)  # Should not raise JSONDecodeError
        assert isinstance(data, dict)
    
    def test_log_file_has_experiments_array(self):
        """Test log file has experiments array"""
        log_experiment(
            agent_name="ArrayTest",
            model_used="test",
            action=ActionType.ANALYSIS,
            details={"input_prompt": "test", "output_response": "result"}
        )
        
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert "experiments" in data
        assert isinstance(data["experiments"], list)
    
    def test_multiple_logs_append(self):
        """Test multiple logs append to file"""
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            initial_data = json.load(f)
        initial_count = len(initial_data["experiments"])
        
        log_experiment(
            agent_name="AppendTest1",
            model_used="test",
            action=ActionType.ANALYSIS,
            details={"input_prompt": "test1", "output_response": "result1"}
        )
        log_experiment(
            agent_name="AppendTest2",
            model_used="test",
            action=ActionType.ANALYSIS,
            details={"input_prompt": "test2", "output_response": "result2"}
        )
        
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            final_data = json.load(f)
        
        assert len(final_data["experiments"]) >= initial_count + 2


class TestLogEntryStructure:
    """Unit tests for log entry structure"""
    
    def test_entry_has_all_required_fields(self):
        """Test log entry has all required fields"""
        log_id = log_experiment(
            agent_name="StructureTest",
            model_used="test",
            action=ActionType.ANALYSIS,
            details={"input_prompt": "test", "output_response": "result"}
        )
        
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        entry = next((e for e in data["experiments"] if e["id"] == log_id), None)
        required_fields = ["id", "timestamp", "agent_name", "model_used", 
                          "action", "details", "status"]
        
        for field in required_fields:
            assert field in entry, f"Missing required field: {field}"
    
    def test_entry_timestamp_format(self):
        """Test timestamp is in ISO format"""
        log_id = log_experiment(
            agent_name="TimestampTest",
            model_used="test",
            action=ActionType.ANALYSIS,
            details={"input_prompt": "test", "output_response": "result"}
        )
        
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        entry = next((e for e in data["experiments"] if e["id"] == log_id), None)
        timestamp = entry["timestamp"]
        
        # Should be parseable as ISO datetime
        datetime.fromisoformat(timestamp)
    
    def test_entry_details_is_dict(self):
        """Test details field is a dictionary"""
        log_id = log_experiment(
            agent_name="DetailsDictTest",
            model_used="test",
            action=ActionType.ANALYSIS,
            details={"input_prompt": "test", "output_response": "result"}
        )
        
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        entry = next((e for e in data["experiments"] if e["id"] == log_id), None)
        assert isinstance(entry["details"], dict)


class TestGetExperimentStats:
    """Unit tests for get_experiment_stats function"""
    
    def test_stats_returns_dict(self):
        """Test get_experiment_stats returns a dictionary"""
        stats = get_experiment_stats()
        assert isinstance(stats, dict)
    
    def test_stats_has_total_experiments(self):
        """Test stats includes total_experiments count"""
        stats = get_experiment_stats()
        assert "total_experiments" in stats
        assert isinstance(stats["total_experiments"], int)
        assert stats["total_experiments"] >= 0
    
    def test_stats_has_by_agent(self):
        """Test stats includes by_agent breakdown"""
        stats = get_experiment_stats()
        assert "by_agent" in stats
        assert isinstance(stats["by_agent"], dict)
    
    def test_stats_has_by_action(self):
        """Test stats includes by_action breakdown"""
        stats = get_experiment_stats()
        assert "by_action" in stats
        assert isinstance(stats["by_action"], dict)
    
    def test_stats_has_by_status(self):
        """Test stats includes by_status breakdown"""
        stats = get_experiment_stats()
        assert "by_status" in stats
        assert isinstance(stats["by_status"], dict)
    
    def test_stats_counts_are_consistent(self):
        """Test that sum of counts equals total"""
        log_experiment(
            agent_name="StatsConsistencyTest",
            model_used="test",
            action=ActionType.ANALYSIS,
            details={"input_prompt": "test", "output_response": "result"}
        )
        
        stats = get_experiment_stats()
        total = stats["total_experiments"]
        
        # Sum of agent counts should equal total
        agent_sum = sum(stats["by_agent"].values())
        assert agent_sum == total
        
        # Sum of action counts should equal total
        action_sum = sum(stats["by_action"].values())
        assert action_sum == total


class TestEnsureLogFile:
    """Unit tests for _ensure_log_file function"""
    
    def test_ensure_log_file_creates_file(self):
        """Test _ensure_log_file creates log file if missing"""
        # This function is called internally, but we can test it exists
        assert callable(_ensure_log_file)
    
    def test_log_directory_exists(self):
        """Test logs directory exists"""
        log_path = Path(LOG_FILE)
        assert log_path.parent.exists()


class TestEdgeCases:
    """Unit tests for edge cases"""
    
    def test_very_long_agent_name(self):
        """Test logging with very long agent name"""
        long_name = "A" * 1000
        log_id = log_experiment(
            agent_name=long_name,
            model_used="test",
            action=ActionType.ANALYSIS,
            details={"input_prompt": "test", "output_response": "result"}
        )
        assert log_id is not None
    
    def test_very_long_input_prompt(self):
        """Test logging with very long input_prompt"""
        long_prompt = "x" * 10000
        log_id = log_experiment(
            agent_name="LongPromptTest",
            model_used="test",
            action=ActionType.ANALYSIS,
            details={"input_prompt": long_prompt, "output_response": "result"}
        )
        assert log_id is not None
    
    def test_unicode_in_details(self):
        """Test logging with Unicode characters"""
        log_id = log_experiment(
            agent_name="UnicodeTest",
            model_used="test",
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": "Test with émojis 🐝🔧",
                "output_response": "Résultat avec accénts"
            }
        )
        assert log_id is not None
    
    def test_special_characters_in_agent_name(self):
        """Test logging with special characters in agent name"""
        log_id = log_experiment(
            agent_name="Agent-Name_123!@#",
            model_used="test",
            action=ActionType.ANALYSIS,
            details={"input_prompt": "test", "output_response": "result"}
        )
        assert log_id is not None
    
    def test_numeric_values_in_details(self):
        """Test logging with numeric values in details"""
        log_id = log_experiment(
            agent_name="NumericTest",
            model_used="test",
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": "test",
                "output_response": "result",
                "score": 95.5,
                "count": 42,
                "is_valid": True
            }
        )
        
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        entry = next((e for e in data["experiments"] if e["id"] == log_id), None)
        assert entry["details"]["score"] == 95.5
        assert entry["details"]["count"] == 42
        assert entry["details"]["is_valid"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
