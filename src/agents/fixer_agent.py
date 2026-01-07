"""
Fixer Agent - Applies fixes to code based on the Auditor's plan.
"""

import os
import json
from src.agents.base_agent import BaseAgent
from src.tools.file_tools import read_file, write_file, backup_file
from src.utils.logger import ActionType
from src.prompts.fixer_prompt import FIXER_SYSTEM_PROMPT


class FixerAgent(BaseAgent):
    """
    The Fixer Agent takes the refactoring plan from the Auditor
    and applies fixes to the code.
    """
    
    def __init__(self):
        super().__init__(agent_name="Fixer_Agent")
    
    def get_system_prompt(self) -> str:
        return FIXER_SYSTEM_PROMPT

    def fix_file(self, filepath: str, refactoring_plan: dict, previous_errors: str = None) -> dict:
        """
        Fix a single file based on the refactoring plan.
        
        Args:
            filepath: Path to the file to fix
            refactoring_plan: Dictionary containing issues and refactoring steps
            previous_errors: Optional error messages from previous attempts
        
        Returns:
            Dictionary with results:
            - success: Whether the fix was applied
            - fixed_code: The fixed code
            - backup_path: Path to backup file
            - error: Error message if failed
        """
        result = {
            "success": False,
            "fixed_code": None,
            "backup_path": None,
            "error": None
        }
        
        try:
            # Read original code
            original_code = read_file(filepath)
            
            # Create backup
            backup_path = backup_file(filepath)
            result["backup_path"] = backup_path
            
            # Build the fix prompt
            prompt = self._build_fix_prompt(
                filepath=filepath,
                original_code=original_code,
                refactoring_plan=refactoring_plan,
                previous_errors=previous_errors
            )
            
            # Call LLM to get fixed code
            fixed_code = self.call_llm(
                prompt=prompt,
                action_type=ActionType.FIX,
                extra_details={
                    "file": filepath,
                    "issues_count": len(refactoring_plan.get("issues", [])),
                    "has_previous_errors": previous_errors is not None
                }
            )
            
            # Clean up the response (remove markdown if present)
            fixed_code = self._clean_code_response(fixed_code)
            
            # Write the fixed code
            write_file(filepath, fixed_code)
            
            result["success"] = True
            result["fixed_code"] = fixed_code
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _build_fix_prompt(self, filepath: str, original_code: str, 
                          refactoring_plan: dict, previous_errors: str = None) -> str:
        """
        Build the prompt for the LLM to fix the code.
        
        Args:
            filepath: Path to file being fixed
            original_code: Original buggy code
            refactoring_plan: Plan with issues and steps
            previous_errors: Previous error messages if this is a retry
        
        Returns:
            Complete prompt string
        """
        prompt = f"""{self.get_system_prompt()}

FILE: {os.path.basename(filepath)}

ORIGINAL CODE:
```python
{original_code}
```

ISSUES TO FIX:
{json.dumps(refactoring_plan.get('issues', []), indent=2)}

REFACTORING PLAN:
{chr(10).join(refactoring_plan.get('refactoring_plan', []))}
"""
        
        if previous_errors:
            prompt += f"""

PREVIOUS ATTEMPT FAILED WITH THESE ERRORS:
{previous_errors}

Please fix these errors while applying the refactoring plan.
"""
        
        prompt += """

Now output the COMPLETE fixed Python file. 
Output ONLY the Python code, no markdown, no explanations."""
        
        return prompt
    
    def _clean_code_response(self, response: str) -> str:
        """
        Clean the LLM response to extract just the Python code.
        
        Args:
            response: Raw LLM response
        
        Returns:
            Cleaned Python code
        """
        # Remove markdown code blocks if present
        if "```python" in response:
            start = response.find("```python") + 9
            end = response.find("```", start)
            response = response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            response = response[start:end].strip()
        
        return response.strip()
    
    def fix_multiple_files(self, file_plans: list) -> dict:
        """
        Fix multiple files based on their refactoring plans.
        
        Args:
            file_plans: List of dicts with 'filepath' and 'plan'
        
        Returns:
            Dictionary with results for each file
        """
        results = {
            "fixed_files": [],
            "failed_files": [],
            "total_files": len(file_plans)
        }
        
        for file_plan in file_plans:
            filepath = file_plan.get("filepath")
            plan = file_plan.get("plan", {})
            
            fix_result = self.fix_file(filepath, plan)
            
            if fix_result["success"]:
                results["fixed_files"].append({
                    "file": filepath,
                    "backup": fix_result["backup_path"]
                })
            else:
                results["failed_files"].append({
                    "file": filepath,
                    "error": fix_result["error"]
                })
        
        return results
