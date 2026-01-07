"""
Judge Agent - Validates fixes by running tests and checking quality.
"""

import os
import json
from src.agents.base_agent import BaseAgent
from src.tools.pylint_tool import run_pylint
from src.tools.pytest_tool import run_pytest, has_tests
from src.utils.logger import ActionType
from src.prompts.judge_prompt import JUDGE_SYSTEM_PROMPT


class JudgeAgent(BaseAgent):
    """
    The Judge Agent validates the Fixer's work by running tests
    and checking code quality improvements.
    """
    
    def __init__(self):
        super().__init__(agent_name="Judge_Agent")
    
    def get_system_prompt(self) -> str:
        return JUDGE_SYSTEM_PROMPT

    def evaluate(self, filepath: str, original_score: float, test_dir: str = None) -> dict:
        """
        Evaluate the fixed code.
        
        Args:
            filepath: Path to the fixed file
            original_score: Original pylint score before fixing
            test_dir: Directory containing tests (optional)
        
        Returns:
            Dictionary with evaluation results and decision
        """
        evaluation = {
            "decision": "RETRY",
            "tests_passed": None,
            "tests_details": "No tests found",
            "pylint_before": original_score,
            "pylint_after": 0.0,
            "improved": False,
            "score_delta": 0.0,
            "retry_reason": None,
            "feedback": None
        }
        
        try:
            # Run pylint on fixed code
            pylint_result = run_pylint(filepath)
            new_score = pylint_result.get("score", 0.0)
            evaluation["pylint_after"] = new_score
            evaluation["score_delta"] = new_score - original_score
            evaluation["improved"] = new_score >= original_score
            
            # Run tests if test directory provided
            tests_exist = False
            tests_passed = True  # Default to true if no tests
            
            if test_dir and os.path.exists(test_dir):
                tests_exist = has_tests(test_dir)
                
                if tests_exist:
                    test_result = run_pytest(test_dir)
                    tests_passed = test_result.get("success", False)
                    evaluation["tests_passed"] = tests_passed
                    evaluation["tests_details"] = f"Passed: {test_result.get('passed', 0)}, Failed: {test_result.get('failed', 0)}"
                else:
                    evaluation["tests_details"] = "No tests found in test directory"
            
            # Build evaluation prompt for LLM
            prompt = self._build_evaluation_prompt(
                filepath=filepath,
                evaluation=evaluation,
                pylint_result=pylint_result,
                tests_exist=tests_exist
            )
            
            # Get LLM decision
            response = self.call_llm(
                prompt=prompt,
                action_type=ActionType.DEBUG,
                extra_details={
                    "file": filepath,
                    "score_before": original_score,
                    "score_after": new_score,
                    "tests_passed": tests_passed
                }
            )
            
            # Parse LLM decision
            decision_data = self._parse_decision(response)
            evaluation.update(decision_data)
            
        except Exception as e:
            evaluation["retry_reason"] = f"Evaluation error: {str(e)}"
            evaluation["feedback"] = f"Failed to evaluate: {str(e)}"
        
        return evaluation
    
    def _build_evaluation_prompt(self, filepath: str, evaluation: dict, 
                                  pylint_result: dict, tests_exist: bool) -> str:
        """
        Build the evaluation prompt for the LLM.
        
        Args:
            filepath: Path to file being evaluated
            evaluation: Current evaluation data
            pylint_result: Full pylint results
            tests_exist: Whether tests were found
        
        Returns:
            Complete prompt string
        """
        prompt = f"""{self.get_system_prompt()}

FILE EVALUATED: {os.path.basename(filepath)}

QUALITY METRICS:
- Pylint Score BEFORE: {evaluation['pylint_before']:.2f}/10
- Pylint Score AFTER: {evaluation['pylint_after']:.2f}/10
- Score Change: {evaluation['score_delta']:+.2f}
- Improvement: {evaluation['improved']}

TEST RESULTS:
- Tests Exist: {tests_exist}
- Tests Passed: {evaluation.get('tests_passed', 'N/A')}
- Details: {evaluation['tests_details']}

PYLINT ISSUES IN FIXED CODE:
{json.dumps(pylint_result.get('issues', [])[:10], indent=2)}

Based on this data, make your decision following the rules in your system prompt.
Output your decision in the specified JSON format."""
        
        return prompt
    
    def _parse_decision(self, response: str) -> dict:
        """
        Parse the LLM's decision response.
        
        Args:
            response: Raw LLM response
        
        Returns:
            Parsed decision dictionary
        """
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
            
            decision = json.loads(response)
            return decision
        except json.JSONDecodeError:
            # If parsing fails, default to RETRY with the raw response
            return {
                "decision": "RETRY",
                "retry_reason": "Failed to parse judge decision",
                "feedback": "Judge response was not valid JSON",
                "raw_response": response
            }
    
    def evaluate_multiple_files(self, file_data: list) -> dict:
        """
        Evaluate multiple files.
        
        Args:
            file_data: List of dicts with 'filepath', 'original_score', 'test_dir'
        
        Returns:
            Overall evaluation results
        """
        results = {
            "all_success": True,
            "files_evaluated": [],
            "total_files": len(file_data),
            "passed": 0,
            "failed": 0
        }
        
        for file_info in file_data:
            filepath = file_info.get("filepath")
            original_score = file_info.get("original_score", 0.0)
            test_dir = file_info.get("test_dir")
            
            evaluation = self.evaluate(filepath, original_score, test_dir)
            
            file_result = {
                "file": filepath,
                "decision": evaluation["decision"],
                "evaluation": evaluation
            }
            
            results["files_evaluated"].append(file_result)
            
            if evaluation["decision"] == "SUCCESS":
                results["passed"] += 1
            else:
                results["failed"] += 1
                results["all_success"] = False
        
        return results
