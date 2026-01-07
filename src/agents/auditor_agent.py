"""
Auditor Agent - Analyzes code, runs static analysis, produces refactoring plan.
"""

import os
import json
from src.agents.base_agent import BaseAgent
from src.tools.file_tools import read_file, list_python_files
from src.tools.pylint_tool import run_pylint
from src.utils.logger import ActionType
from src.prompts.auditor_prompt import AUDITOR_SYSTEM_PROMPT


class AuditorAgent(BaseAgent):
    """
    The Auditor Agent reads code, runs static analysis (pylint),
    and produces a structured refactoring plan.
    """
    
    def __init__(self):
        super().__init__(agent_name="Auditor_Agent")
    
    def get_system_prompt(self) -> str:
        return AUDITOR_SYSTEM_PROMPT

    def analyze(self, target_dir: str) -> dict:
        """
        Analyze all Python files in the target directory.
        
        Args:
            target_dir: Path to directory containing Python files
        
        Returns:
            Dictionary with analysis results and refactoring plan
        """
        results = {
            "files_analyzed": [],
            "total_issues": 0,
            "all_issues": [],
            "refactoring_plans": [],
            "pylint_scores": {}
        }
        
        # Get all Python files
        try:
            python_files = list_python_files(target_dir)
        except Exception as e:
            return {"error": f"Failed to list files: {str(e)}", "issues": []}
        
        if not python_files:
            return {"error": "No Python files found", "issues": []}
        
        for filepath in python_files:
            file_result = self._analyze_file(str(filepath))
            results["files_analyzed"].append(str(filepath))
            
            if "issues" in file_result:
                results["all_issues"].extend(file_result["issues"])
                results["total_issues"] += len(file_result["issues"])
            
            if "current_pylint_score" in file_result:
                results["pylint_scores"][str(filepath)] = file_result["current_pylint_score"]
            
            if "refactoring_plan" in file_result:
                results["refactoring_plans"].append({
                    "file": str(filepath),
                    "plan": file_result["refactoring_plan"]
                })
        
        return results
    
    def _analyze_file(self, filepath: str) -> dict:
        """
        Analyze a single Python file.
        
        Args:
            filepath: Path to Python file
        
        Returns:
            Dictionary with analysis results for this file
        """
        try:
            # Read the file
            code_content = read_file(filepath)
            
            # Run pylint
            pylint_result = run_pylint(filepath)
            
            # Prepare prompt for LLM
            prompt = f"""{self.get_system_prompt()}

FILE TO ANALYZE: {os.path.basename(filepath)}

CODE:
```python
{code_content}
```

PYLINT RESULTS:
Score: {pylint_result.get('score', 0)}/10
Issues Found: {len(pylint_result.get('issues', []))}

PYLINT ISSUES:
{json.dumps(pylint_result.get('issues', []), indent=2)}

Please provide your complete analysis in the specified JSON format."""
            
            # Call LLM
            response = self.call_llm(
                prompt=prompt,
                action_type=ActionType.ANALYSIS,
                extra_details={
                    "file": filepath,
                    "pylint_score": pylint_result.get('score', 0)
                }
            )
            
            # Parse JSON response
            try:
                # Try to extract JSON from markdown code blocks if present
                if "```json" in response:
                    json_start = response.find("```json") + 7
                    json_end = response.find("```", json_start)
                    response = response[json_start:json_end].strip()
                elif "```" in response:
                    json_start = response.find("```") + 3
                    json_end = response.find("```", json_start)
                    response = response[json_start:json_end].strip()
                
                analysis = json.loads(response)
                analysis["file"] = filepath
                return analysis
            except json.JSONDecodeError:
                # If JSON parsing fails, return raw response
                return {
                    "file": filepath,
                    "current_pylint_score": pylint_result.get('score', 0),
                    "issues": [],
                    "refactoring_plan": ["LLM response was not valid JSON"],
                    "raw_response": response
                }
                
        except Exception as e:
            return {
                "file": filepath,
                "error": str(e),
                "issues": []
            }
