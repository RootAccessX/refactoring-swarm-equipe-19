"""
JSON Schema validation for experiment logs.
"""

import json
from typing import Optional

LOG_SCHEMA = {
    "type": "object",
    "required": ["experiments"],
    "properties": {
        "experiments": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "id", "timestamp", "agent_name",
                    "model_used", "action", "details", "status"
                ],
                "properties": {
                    "id": {"type": "string"},
                    "timestamp": {"type": "string"},
                    "agent_name": {"type": "string"},
                    "model_used": {"type": "string"},
                    "action": {"type": "string"},
                    "status": {"type": "string"},
                    "details": {
                        "type": "object",
                        "required": ["input_prompt", "output_response"],
                        "properties": {
                            "input_prompt": {"type": "string"},
                            "output_response": {"type": "string"}
                        }
                    }
                }
            }
        }
    }
}


def validate_log_file(filepath: str = "logs/experiment_data.json") -> tuple[bool, Optional[str]]:
    """
    Validate the log file against the schema.
    
    Args:
        filepath: Path to log file
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Basic structure check
        if "experiments" not in data:
            return False, "Missing 'experiments' key"
        
        if not isinstance(data["experiments"], list):
            return False, "'experiments' must be a list"
        
        # Validate each experiment
        for idx, exp in enumerate(data["experiments"]):
            # Check required top-level fields
            required = ["id", "timestamp", "agent_name", "model_used", 
                       "action", "details", "status"]
            for field in required:
                if field not in exp:
                    return False, f"Experiment {idx}: missing '{field}'"
            
            # Check details has required fields
            if "input_prompt" not in exp["details"]:
                return False, f"Experiment {idx}: missing 'input_prompt' in details"
            if "output_response" not in exp["details"]:
                return False, f"Experiment {idx}: missing 'output_response' in details"
        
        return True, None
        
    except FileNotFoundError:
        return False, f"File not found: {filepath}"
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"
    except Exception as e:
        return False, f"Validation error: {e}"


if __name__ == "__main__":
    # Run validation
    valid, error = validate_log_file()
    if valid:
        print("OK - Log file is valid!")
    else:
        print(f"ERROR - Validation failed: {error}")