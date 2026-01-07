# 🐝 Solution Architecture - The Refactoring Swarm

## 📋 Executive Summary

This document outlines the technical solution for implementing a multi-agent system that autonomously refactors buggy Python code. The system uses 3 specialized AI agents orchestrated in a self-healing loop.

---

## 🏗️ System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MAIN.PY (Entry Point)                             │
│                         python main.py --target_dir                         │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            ORCHESTRATOR                                      │
│                    (LangGraph / CrewAI / AutoGen)                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     EXECUTION GRAPH                                  │   │
│  │                                                                      │   │
│  │    ┌──────────┐      ┌──────────┐      ┌──────────┐                │   │
│  │    │ AUDITOR  │ ───► │  FIXER   │ ───► │  JUDGE   │                │   │
│  │    │  Agent   │      │  Agent   │      │  Agent   │                │   │
│  │    └──────────┘      └──────────┘      └────┬─────┘                │   │
│  │         ▲                                   │                       │   │
│  │         │            SELF-HEALING           │                       │   │
│  │         │              LOOP                 │                       │   │
│  │         │         (max 10 iterations)       │                       │   │
│  │         │                                   │                       │   │
│  │         │         ┌─────────────┐           │                       │   │
│  │         └─────────┤  FAIL?      │◄──────────┘                       │   │
│  │                   │  retry...   │                                   │   │
│  │                   └──────┬──────┘                                   │   │
│  │                          │ SUCCESS                                  │   │
│  │                          ▼                                          │   │
│  │                   ┌─────────────┐                                   │   │
│  │                   │    EXIT     │                                   │   │
│  │                   │   CLEAN     │                                   │   │
│  │                   └─────────────┘                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              TOOLS LAYER                                     │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────────────┐   │
│  │ File I/O   │  │  Pylint    │  │  Pytest    │  │  Sandbox Manager   │   │
│  │   Tools    │  │  Wrapper   │  │  Wrapper   │  │  (Security)        │   │
│  └────────────┘  └────────────┘  └────────────┘  └────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              LOGGING LAYER                                   │
│                        experiment_data.json                                  │
│  { agent_name, model_used, action, input_prompt, output_response, ... }    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🤖 Agent Specifications

### Agent 1: The Auditor 🔍

**Purpose:** Analyze code, identify issues, create refactoring plan

**Input:**
- Path to Python file(s) to analyze
- Pylint output (quality score + issues)

**Output:**
- Structured refactoring plan (JSON)
- List of issues found (bugs, missing docs, style issues)
- Priority ranking of fixes

**Tools Used:**
- `read_file(filepath)` - Read source code
- `run_pylint(filepath)` - Get static analysis results

**Prompt Strategy:**
```python
AUDITOR_SYSTEM_PROMPT = """
You are a senior Python code reviewer. Your job is to:
1. Analyze the provided Python code
2. Identify ALL issues: bugs, missing docstrings, PEP8 violations, logic errors
3. Create a prioritized refactoring plan

Output Format (JSON):
{
    "file": "filename.py",
    "current_pylint_score": X.XX,
    "issues": [
        {
            "line": N,
            "type": "bug|style|documentation|logic",
            "severity": "critical|high|medium|low",
            "description": "...",
            "suggested_fix": "..."
        }
    ],
    "refactoring_plan": [
        "Step 1: ...",
        "Step 2: ..."
    ]
}

Be exhaustive but precise. Do not hallucinate issues that don't exist.
"""
```

---

### Agent 2: The Fixer 🔧

**Purpose:** Apply fixes to code based on the Auditor's plan

**Input:**
- Original code
- Refactoring plan from Auditor
- (Optional) Previous error logs from Judge

**Output:**
- Modified code files
- Summary of changes made

**Tools Used:**
- `read_file(filepath)` - Read current code
- `write_file(filepath, content)` - Write fixed code
- `apply_patch(filepath, old_code, new_code)` - Apply targeted fixes

**Prompt Strategy:**
```python
FIXER_SYSTEM_PROMPT = """
You are an expert Python developer tasked with fixing code.

Given:
1. The original buggy code
2. A refactoring plan
3. (If retry) Previous error messages

Your job:
1. Apply fixes ONE BY ONE from the plan
2. Ensure the code remains syntactically valid
3. Preserve the original functionality while fixing issues
4. Add proper docstrings and type hints

Rules:
- NEVER delete functionality unless it's clearly a bug
- ALWAYS ensure imports are correct
- Test your mental model of the code before outputting

Output the COMPLETE fixed file, not just snippets.
"""
```

---

### Agent 3: The Judge ⚖️

**Purpose:** Validate fixes by running tests and checking quality

**Input:**
- Path to fixed code
- Original Pylint score (to compare improvement)

**Output:**
- Test results (pass/fail)
- New Pylint score
- Decision: SUCCESS or RETRY with error details

**Tools Used:**
- `run_pytest(filepath)` - Execute unit tests
- `run_pylint(filepath)` - Check quality score
- `compare_scores(before, after)` - Verify improvement

**Prompt Strategy:**
```python
JUDGE_SYSTEM_PROMPT = """
You are a quality assurance judge for Python code.

Given:
1. Test execution results (pytest output)
2. Quality scores (before and after)

Your job:
1. Analyze if ALL tests pass
2. Verify the Pylint score improved (or stayed same)
3. Make a final decision

Decision Output (JSON):
{
    "decision": "SUCCESS" | "RETRY",
    "tests_passed": true/false,
    "tests_details": "...",
    "pylint_before": X.XX,
    "pylint_after": Y.YY,
    "improved": true/false,
    "retry_reason": "..." (if RETRY)
}

Be strict: If ANY test fails, decision = RETRY
"""
```

---

## 🤖 Agent Class Implementations

### Base Agent Class (`src/agents/base_agent.py`)

```python
"""
Base Agent class that all specialized agents inherit from.
Handles common functionality: LLM calls, logging, error handling.
"""

import os
import google.generativeai as genai
from abc import ABC, abstractmethod
from src.utils.logger import log_experiment, ActionType

class BaseAgent(ABC):
    """Abstract base class for all agents in the Refactoring Swarm."""
    
    def __init__(self, agent_name: str, model_name: str = "gemini-2.0-flash"):
        """
        Initialize the base agent.
        
        Args:
            agent_name: Name identifier for this agent
            model_name: Gemini model to use
        """
        self.agent_name = agent_name
        self.model_name = model_name
        
        # Configure Gemini API
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
    
    def call_llm(self, prompt: str, action_type: ActionType, extra_details: dict = None) -> str:
        """
        Call the LLM and log the interaction.
        
        Args:
            prompt: The prompt to send to the LLM
            action_type: Type of action being performed
            extra_details: Additional details to log
        
        Returns:
            LLM response text
        """
        try:
            # Call Gemini
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Prepare log details
            details = {
                "input_prompt": prompt,
                "output_response": response_text,
            }
            if extra_details:
                details.update(extra_details)
            
            # Log the interaction
            log_experiment(
                agent_name=self.agent_name,
                model_used=self.model_name,
                action=action_type,
                details=details,
                status="SUCCESS"
            )
            
            return response_text
            
        except Exception as e:
            # Log failure
            log_experiment(
                agent_name=self.agent_name,
                model_used=self.model_name,
                action=action_type,
                details={
                    "input_prompt": prompt,
                    "output_response": f"ERROR: {str(e)}",
                    "error_type": type(e).__name__
                },
                status="FAILURE"
            )
            raise
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent. Must be implemented by subclasses."""
        pass
```

---

### Auditor Agent (`src/agents/auditor_agent.py`)

```python
"""
Auditor Agent - Analyzes code, runs static analysis, produces refactoring plan.
"""

import os
import json
from src.agents.base_agent import BaseAgent
from src.tools.file_tools import read_file, list_python_files
from src.tools.pylint_tool import run_pylint
from src.utils.logger import ActionType

class AuditorAgent(BaseAgent):
    """
    The Auditor Agent reads code, runs static analysis (pylint),
    and produces a structured refactoring plan.
    """
    
    def __init__(self):
        super().__init__(agent_name="Auditor_Agent")
    
    def get_system_prompt(self) -> str:
        return """You are a senior Python code auditor and reviewer.

YOUR ROLE:
- Analyze Python code for bugs, style issues, missing documentation, and logic errors
- Use pylint results to identify specific problems
- Create a prioritized, actionable refactoring plan

OUTPUT FORMAT (STRICT JSON):
{
    "file": "filename.py",
    "current_pylint_score": 0.0,
    "issues": [
        {
            "line": 1,
            "type": "bug|style|documentation|logic|security",
            "severity": "critical|high|medium|low",
            "description": "Clear description of the issue",
            "suggested_fix": "Specific suggestion to fix it"
        }
    ],
    "refactoring_plan": [
        "Step 1: Fix critical bugs first...",
        "Step 2: Add missing docstrings...",
        "Step 3: Improve code style..."
    ]
}

RULES:
1. Be thorough - find ALL issues
2. Be precise - give exact line numbers
3. Be actionable - every issue must have a suggested fix
4. Prioritize: critical bugs > high severity > medium > low
5. DO NOT hallucinate issues that don't exist in the code
6. Output ONLY valid JSON, no markdown or explanations"""

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
            "issues": [],
            "refactoring_plan": [],
            "pylint_scores": {}
        }
        
        # Get all Python files
        python_files = list_python_files(target_dir)
        
        if not python_files:
            return {"error": "No Python files found", "issues": []}
        
        for filepath in python_files:
            file_result = self._analyze_file(str(filepath), target_dir)
            results["files_analyzed"].append(str(filepath))
            results["issues"].extend(file_result.get("issues", []))
            results["total_issues"] += len(file_result.get("issues", []))
            results["pylint_scores"][str(filepath)] = file_result.get("current_pylint_score", 0)
            results["refactoring_plan"].extend(file_result.get("refactoring_plan", []))
        
        return results
    
    def _analyze_file(self, filepath: str, sandbox_root: str) -> dict:
        """
        Analyze a single Python file.
        
        Args:
            filepath: Path to the Python file
            sandbox_root: Root directory for sandbox security
        
        Returns:
            Analysis results for this file
        """
        # Read the file content
        try:
            code_content = read_file(filepath, sandbox_root)
        except Exception as e:
            return {"error": f"Could not read file: {e}", "issues": []}
        
        # Run pylint
        pylint_result = run_pylint(filepath)
        
        # Build the prompt
        prompt = f"""{self.get_system_prompt()}

---
FILE TO ANALYZE: {os.path.basename(filepath)}
---

PYLINT OUTPUT (Score: {pylint_result.get('score', 0)}/10):
{json.dumps(pylint_result.get('issues', [])[:20], indent=2)}

---
SOURCE CODE:
---
python
{code_content}


Analyze this code and provide your assessment in the JSON format specified above."""

        # Call LLM
        response = self.call_llm(
            prompt=prompt,
            action_type=ActionType.ANALYSIS,
            extra_details={
                "file_analyzed": filepath,
                "pylint_score": pylint_result.get('score', 0)
            }
        )
        
        # Parse JSON response
        try:
            # Clean response (remove markdown code blocks if present)
            clean_response = response.strip()
            if clean_response.startswith("```"):
                clean_response = clean_response.split("```")[1]
                if clean_response.startswith("json"):
                    clean_response = clean_response[4:]
            clean_response = clean_response.strip()
            
            result = json.loads(clean_response)
            result["current_pylint_score"] = pylint_result.get('score', 0)
            return result
        except json.JSONDecodeError:
            # If JSON parsing fails, return raw response
            return {
                "file": filepath,
                "current_pylint_score": pylint_result.get('score', 0),
                "issues": [],
                "refactoring_plan": [],
                "raw_response": response,
                "parse_error": "Could not parse LLM response as JSON"
            }
```

---

### Fixer Agent (`src/agents/fixer_agent.py`)

```python
"""
Fixer Agent - Reads the refactoring plan and modifies code to fix issues.
"""

import os
import json
from src.agents.base_agent import BaseAgent
from src.tools.file_tools import read_file, write_file, list_python_files
from src.utils.logger import ActionType

class FixerAgent(BaseAgent):
    """
    The Fixer Agent reads the refactoring plan from the Auditor
    and applies fixes to the code files.
    """
    
    def __init__(self):
        super().__init__(agent_name="Fixer_Agent")
    
    def get_system_prompt(self) -> str:
        return """You are an expert Python developer specialized in code refactoring and bug fixing.

YOUR ROLE:
- Take buggy Python code and a refactoring plan
- Apply fixes systematically, one by one
- Ensure the fixed code is syntactically correct and functional

OUTPUT FORMAT:
You must output ONLY the complete fixed Python code, nothing else.
- No explanations before or after
- No markdown code blocks (no ```)
- Just the raw Python code that should replace the original file

RULES:
1. Fix ALL issues mentioned in the refactoring plan
2. Add proper docstrings to all functions and classes
3. Add type hints where appropriate
4. Handle edge cases (empty lists, None values, division by zero, etc.)
5. Follow PEP 8 style guidelines
6. Preserve the original functionality - only fix bugs, don't change behavior
7. Ensure all imports are correct and present
8. If there are unit tests, make sure the code passes them

IMPORTANT: Output ONLY the fixed Python code, ready to be saved to a file."""

    def fix(self, target_dir: str, refactoring_plan: list, error_context: str = None) -> dict:
        """
        Apply fixes to all Python files based on the refactoring plan.
        
        Args:
            target_dir: Path to directory containing Python files
            refactoring_plan: List of refactoring steps from Auditor
            error_context: Optional error message from previous failed attempt
        
        Returns:
            Dictionary with fix results
        """
        results = {
            "files_fixed": [],
            "success": True,
            "errors": []
        }
        
        python_files = list_python_files(target_dir)
        
        for filepath in python_files:
            try:
                fix_result = self._fix_file(
                    str(filepath), 
                    target_dir, 
                    refactoring_plan,
                    error_context
                )
                results["files_fixed"].append({
                    "file": str(filepath),
                    "status": "fixed" if fix_result["success"] else "failed",
                    "details": fix_result
                })
            except Exception as e:
                results["errors"].append({
                    "file": str(filepath),
                    "error": str(e)
                })
                results["success"] = False
        
        return results
    
    def _fix_file(self, filepath: str, sandbox_root: str, 
                  refactoring_plan: list, error_context: str = None) -> dict:
        """
        Fix a single Python file.
        
        Args:
            filepath: Path to the Python file
            sandbox_root: Root directory for sandbox security
            refactoring_plan: List of refactoring steps
            error_context: Optional error from previous attempt
        
        Returns:
            Fix result for this file
        """
        # Read current code
        try:
            original_code = read_file(filepath, sandbox_root)
        except Exception as e:
            return {"success": False, "error": f"Could not read file: {e}"}
        
        # Build the prompt
        error_section = ""
        if error_context:
            error_section = f"""
---
⚠️ PREVIOUS ATTEMPT FAILED WITH THIS ERROR:
{error_context}

Please fix this error in addition to the refactoring plan.
---
"""
        
        prompt = f"""{self.get_system_prompt()}

---
FILE TO FIX: {os.path.basename(filepath)}
---

REFACTORING PLAN:
{json.dumps(refactoring_plan, indent=2)}
{error_section}
---
ORIGINAL CODE:
---
{original_code}

Now output the COMPLETE fixed Python code:"""

        # Call LLM
        response = self.call_llm(
            prompt=prompt,
            action_type=ActionType.FIX,
            extra_details={
                "file_fixed": filepath,
                "had_error_context": error_context is not None
            }
        )
        
        # Clean the response
        fixed_code = self._clean_code_response(response)
        
        # Validate syntax before writing
        try:
            compile(fixed_code, filepath, 'exec')
        except SyntaxError as e:
            return {
                "success": False,
                "error": f"Generated code has syntax error: {e}",
                "line": e.lineno
            }
        
        # Write the fixed code
        try:
            write_file(filepath, fixed_code, sandbox_root)
            return {
                "success": True,
                "original_length": len(original_code),
                "fixed_length": len(fixed_code)
            }
        except Exception as e:
            return {"success": False, "error": f"Could not write file: {e}"}
    
    def _clean_code_response(self, response: str) -> str:
        """
        Clean the LLM response to extract only the Python code.
        
        Args:
            response: Raw LLM response
        
        Returns:
            Clean Python code
        """
        code = response.strip()
        
        # Remove markdown code blocks if present
        if code.startswith("```python"):
            code = code[9:]
        elif code.startswith("```"):
            code = code[3:]
        
        if code.endswith("```"):
            code = code[:-3]
        
        return code.strip()
```

---

### Judge Agent (`src/agents/judge_agent.py`)

```python
"""
Judge Agent - Executes tests and validates the refactored code.
Implements the self-healing loop decision logic.
"""

import os
import json
from src.agents.base_agent import BaseAgent
from src.tools.pylint_tool import run_pylint
from src.tools.pytest_tool import run_pytest
from src.tools.file_tools import list_python_files
from src.utils.logger import ActionType

class JudgeAgent(BaseAgent):
    """
    The Judge Agent evaluates the fixed code by:
    1. Running unit tests (pytest)
    2. Checking quality score (pylint)
    3. Deciding: SUCCESS (end) or RETRY (back to Fixer)
    """
    
    def __init__(self):
        super().__init__(agent_name="Judge_Agent")
        self.initial_scores = {}  # Store initial scores for comparison
    
    def get_system_prompt(self) -> str:
        return """You are a strict quality assurance judge for Python code.

YOUR ROLE:
- Analyze test results and quality metrics
- Make a binary decision: SUCCESS or RETRY
- If RETRY, provide clear feedback for the Fixer

OUTPUT FORMAT (STRICT JSON):
{
    "decision": "SUCCESS" or "RETRY",
    "tests_passed": true or false,
    "tests_summary": "X passed, Y failed",
    "pylint_before": 0.0,
    "pylint_after": 0.0,
    "quality_improved": true or false,
    "retry_reason": "Detailed explanation if RETRY, empty string if SUCCESS",
    "specific_failures": ["List of specific test failures or issues"]
}

DECISION CRITERIA:
1. If ANY test fails → RETRY
2. If pylint score decreased significantly (>1 point) → RETRY  
3. If code has syntax errors → RETRY
4. Otherwise → SUCCESS

Be strict but fair. Output ONLY valid JSON."""

    def set_initial_scores(self, scores: dict):
        """
        Store initial pylint scores for comparison.
        
        Args:
            scores: Dictionary mapping filepath to initial pylint score
        """
        self.initial_scores = scores
    
    def evaluate(self, target_dir: str) -> dict:
        """
        Evaluate the fixed code in the target directory.
        
        Args:
            target_dir: Path to directory containing fixed Python files
        
        Returns:
            Evaluation result with decision (SUCCESS/RETRY)
        """
        # Gather metrics
        test_results = self._run_all_tests(target_dir)
        quality_results = self._check_all_quality(target_dir)
        
        # Build evaluation prompt
        prompt = f"""{self.get_system_prompt()}

---
TEST RESULTS:
---
{json.dumps(test_results, indent=2)}

---
QUALITY METRICS:
---
Initial scores: {json.dumps(self.initial_scores, indent=2)}
Current scores: {json.dumps(quality_results, indent=2)}

Based on these results, make your judgment:"""

        # Call LLM for decision
        response = self.call_llm(
            prompt=prompt,
            action_type=ActionType.DEBUG,
            extra_details={
                "test_results": test_results,
                "quality_results": quality_results
            }
        )
        
        # Parse response
        try:
            clean_response = response.strip()
            if clean_response.startswith("```"):
                clean_response = clean_response.split("```")[1]
                if clean_response.startswith("json"):
                    clean_response = clean_response[4:]
            clean_response = clean_response.strip()
            
            result = json.loads(clean_response)
            
            # Add raw metrics to result
            result["raw_test_results"] = test_results
            result["raw_quality_results"] = quality_results
            
            return result
            
        except json.JSONDecodeError:
            # Fallback: make decision based on raw metrics
            return self._fallback_decision(test_results, quality_results)
    
    def _run_all_tests(self, target_dir: str) -> dict:
        """
        Run pytest on the target directory.
        
        Args:
            target_dir: Directory to test
        
        Returns:
            Test results dictionary
        """
        # Look for test files
        test_files = []
        for f in os.listdir(target_dir):
            if f.startswith("test_") and f.endswith(".py"):
                test_files.append(os.path.join(target_dir, f))
        
        if not test_files:
            # No test files, try running pytest on the whole directory
            return run_pytest(target_dir)
        
        # Run tests
        all_results = {
            "total_passed": 0,
            "total_failed": 0,
            "total_errors": 0,
            "all_passed": True,
            "details": []
        }
        
        for test_file in test_files:
            result = run_pytest(test_file)
            all_results["total_passed"] += result.get("passed", 0)
            all_results["total_failed"] += result.get("failed", 0)
            all_results["total_errors"] += result.get("errors", 0)
            all_results["details"].append({
                "file": test_file,
                "result": result
            })
            if not result.get("success", False):
                all_results["all_passed"] = False
        
        return all_results
    
    def _check_all_quality(self, target_dir: str) -> dict:
        """
        Run pylint on all Python files.
        
        Args:
            target_dir: Directory to check
        
        Returns:
            Quality scores dictionary
        """
        scores = {}
        python_files = list_python_files(target_dir)
        
        for filepath in python_files:
            result = run_pylint(str(filepath))
            scores[str(filepath)] = {
                "score": result.get("score", 0),
                "issues_count": len(result.get("issues", []))
            }
        
        # Calculate average
        if scores:
            avg_score = sum(s["score"] for s in scores.values()) / len(scores)
            scores["_average"] = avg_score
        
        return scores
    
    def _fallback_decision(self, test_results: dict, quality_results: dict) -> dict:
        """
        Make a decision based on raw metrics if LLM parsing fails.
        
        Args:
            test_results: Raw test results
            quality_results: Raw quality metrics
        
        Returns:
            Decision dictionary
        """
        tests_passed = test_results.get("all_passed", False)
        
        # Check if quality improved
        current_avg = quality_results.get("_average", 0)
        initial_avg = sum(self.initial_scores.values()) / len(self.initial_scores) if self.initial_scores else 0
        quality_improved = current_avg >= initial_avg - 1  # Allow 1 point tolerance
        
        if tests_passed and quality_improved:
            decision = "SUCCESS"
            retry_reason = ""
        else:
            decision = "RETRY"
            reasons = []
            if not tests_passed:
                reasons.append(f"Tests failed: {test_results.get('total_failed', 0)} failures")
            if not quality_improved:
                reasons.append(f"Quality decreased: {initial_avg:.1f} -> {current_avg:.1f}")
            retry_reason = "; ".join(reasons)
        
        return {
            "decision": decision,
            "tests_passed": tests_passed,
            "tests_summary": f"{test_results.get('total_passed', 0)} passed, {test_results.get('total_failed', 0)} failed",
            "pylint_before": initial_avg,
            "pylint_after": current_avg,
            "quality_improved": quality_improved,
            "retry_reason": retry_reason,
            "specific_failures": []
        }
```

---

### Agent Registry (`src/agents/__init__.py`)

```python
"""
Agent Registry - Central place to import and instantiate all agents.
"""

from src.agents.base_agent import BaseAgent
from src.agents.auditor_agent import AuditorAgent
from src.agents.fixer_agent import FixerAgent
from src.agents.judge_agent import JudgeAgent

__all__ = [
    "BaseAgent",
    "AuditorAgent", 
    "FixerAgent",
    "JudgeAgent"
]

def create_agent(agent_type: str) -> BaseAgent:
    """
    Factory function to create agents by type.
    
    Args:
        agent_type: One of "auditor", "fixer", "judge"
    
    Returns:
        Instantiated agent
    
    Raises:
        ValueError: If agent_type is unknown
    """
    agents = {
        "auditor": AuditorAgent,
        "fixer": FixerAgent,
        "judge": JudgeAgent
    }
    
    if agent_type.lower() not in agents:
        raise ValueError(f"Unknown agent type: {agent_type}. Choose from: {list(agents.keys())}")
    
    return agents[agent_type.lower()]()
```

---

## 🛠️ Tools Implementation

### File Tools (`src/tools/file_tools.py`)

```python
import os
from pathlib import Path

def read_file(filepath: str, sandbox_root: str) -> str:
    """
    Safely read a file from the sandbox.
    
    Args:
        filepath: Path to the file to read
        sandbox_root: Root directory of sandbox (security boundary)
    
    Returns:
        File content as string
    
    Raises:
        SecurityError: If filepath is outside sandbox
        FileNotFoundError: If file doesn't exist
    """
    # Security check
    abs_path = os.path.abspath(filepath)
    abs_sandbox = os.path.abspath(sandbox_root)
    
    if not abs_path.startswith(abs_sandbox):
        raise SecurityError(f"Access denied: {filepath} is outside sandbox")
    
    with open(abs_path, 'r', encoding='utf-8') as f:
        return f.read()


def write_file(filepath: str, content: str, sandbox_root: str) -> bool:
    """
    Safely write content to a file in the sandbox.
    
    Args:
        filepath: Path to the file to write
        content: Content to write
        sandbox_root: Root directory of sandbox (security boundary)
    
    Returns:
        True if successful
    
    Raises:
        SecurityError: If filepath is outside sandbox
    """
    # Security check
    abs_path = os.path.abspath(filepath)
    abs_sandbox = os.path.abspath(sandbox_root)
    
    if not abs_path.startswith(abs_sandbox):
        raise SecurityError(f"Access denied: {filepath} is outside sandbox")
    
    # Create directory if needed
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    
    with open(abs_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True


def list_python_files(directory: str) -> list[str]:
    """List all Python files in a directory recursively."""
    return list(Path(directory).rglob("*.py"))
```

---

### Pylint Tool (`src/tools/pylint_tool.py`)

```python
import subprocess
import json
import re

def run_pylint(filepath: str) -> dict:
    """
    Run Pylint on a Python file and return structured results.
    
    Args:
        filepath: Path to Python file to analyze
    
    Returns:
        dict with 'score', 'issues', 'raw_output'
    """
    try:
        # Run pylint with JSON output
        result = subprocess.run(
            ['pylint', filepath, '--output-format=json', '--reports=y'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Parse JSON output
        issues = []
        if result.stdout:
            try:
                issues = json.loads(result.stdout)
            except json.JSONDecodeError:
                pass
        
        # Extract score from stderr (pylint prints score there)
        score = 0.0
        score_match = re.search(r'Your code has been rated at ([\d.]+)/10', result.stderr)
        if score_match:
            score = float(score_match.group(1))
        
        return {
            'score': score,
            'issues': issues,
            'raw_output': result.stderr
        }
    
    except subprocess.TimeoutExpired:
        return {
            'score': 0.0,
            'issues': [],
            'error': 'Pylint timeout'
        }
    except Exception as e:
        return {
            'score': 0.0,
            'issues': [],
            'error': str(e)
        }
```

---

### Pytest Tool (`src/tools/pytest_tool.py`)

```python
import subprocess
import json

def run_pytest(test_path: str) -> dict:
    """
    Run pytest on a test file or directory.
    
    Args:
        test_path: Path to test file or directory
    
    Returns:
        dict with 'passed', 'failed', 'errors', 'output'
    """
    try:
        result = subprocess.run(
            ['pytest', test_path, '-v', '--tb=short', '--json-report'],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        # Parse results
        passed = result.stdout.count(' PASSED')
        failed = result.stdout.count(' FAILED')
        errors = result.stdout.count(' ERROR')
        
        return {
            'success': failed == 0 and errors == 0,
            'passed': passed,
            'failed': failed,
            'errors': errors,
            'output': result.stdout,
            'return_code': result.returncode
        }
    
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Pytest timeout (>120s)'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
```

---

## 📊 Logger Implementation (`src/utils/logger.py`)

```python
import json
import os
from datetime import datetime
from enum import Enum
from typing import Any
import uuid

class ActionType(Enum):
    ANALYSIS = "ANALYSIS"
    GENERATION = "GENERATION"
    DEBUG = "DEBUG"
    FIX = "FIX"

LOG_FILE = "logs/experiment_data.json"

def _ensure_log_file():
    """Ensure log file exists with valid JSON structure."""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w') as f:
            json.dump({"experiments": []}, f)

def log_experiment(
    agent_name: str,
    model_used: str,
    action: ActionType,
    details: dict[str, Any],
    status: str = "SUCCESS"
) -> str:
    """
    Log an experiment/interaction to the JSON log file.
    
    Args:
        agent_name: Name of the agent (e.g., "Auditor_Agent")
        model_used: LLM model name (e.g., "gemini-2.5-flash")
        action: ActionType enum value
        details: Dictionary with interaction details
                 MUST contain 'input_prompt' and 'output_response'
        status: "SUCCESS" or "FAILURE"
    
    Returns:
        Unique experiment ID
    
    Raises:
        ValueError: If required fields are missing from details
    """
    # Validate required fields
    if 'input_prompt' not in details:
        raise ValueError("details must contain 'input_prompt'")
    if 'output_response' not in details:
        raise ValueError("details must contain 'output_response'")
    
    _ensure_log_file()
    
    # Create experiment entry
    experiment_id = str(uuid.uuid4())
    entry = {
        "id": experiment_id,
        "timestamp": datetime.now().isoformat(),
        "agent_name": agent_name,
        "model_used": model_used,
        "action": action.value,
        "details": details,
        "status": status
    }
    
    # Append to log file
    with open(LOG_FILE, 'r+') as f:
        data = json.load(f)
        data["experiments"].append(entry)
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()
    
    return experiment_id
```

---

## 🔄 Orchestrator Implementation (`src/orchestrator.py`)

```python
from typing import Literal
from src.agents.auditor_agent import AuditorAgent
from src.agents.fixer_agent import FixerAgent
from src.agents.judge_agent import JudgeAgent
from src.utils.logger import log_experiment, ActionType

MAX_ITERATIONS = 10

class RefactoringOrchestrator:
    """
    Orchestrates the refactoring workflow between agents.
    Implements self-healing loop with max iteration limit.
    """
    
    def __init__(self, target_dir: str):
        self.target_dir = target_dir
        self.auditor = AuditorAgent()
        self.fixer = FixerAgent()
        self.judge = JudgeAgent()
        self.iteration = 0
        self.history = []
    
    def run(self) -> dict:
        """
        Execute the refactoring pipeline.
        
        Returns:
            Final status dict with results
        """
        print(f"🐝 Starting Refactoring Swarm on: {self.target_dir}")
        
        # Phase 1: Audit
        print("\n📋 Phase 1: Auditing code...")
        audit_result = self.auditor.analyze(self.target_dir)
        self.history.append({"phase": "audit", "result": audit_result})
        
        if not audit_result.get("issues"):
            print("✅ No issues found! Code is already clean.")
            return {"status": "SUCCESS", "iterations": 0}
        
        # Phase 2: Fix Loop
        while self.iteration < MAX_ITERATIONS:
            self.iteration += 1
            print(f"\n🔧 Iteration {self.iteration}: Fixing code...")
            
            # Get error context from previous iteration (if any)
            error_context = None
            if len(self.history) > 1 and self.history[-1].get("error"):
                error_context = self.history[-1]["error"]
            
            # Fixer applies changes
            fix_result = self.fixer.fix(
                self.target_dir,
                audit_result["refactoring_plan"],
                error_context
            )
            self.history.append({"phase": "fix", "result": fix_result})
            
            # Judge evaluates
            print("⚖️ Judging results...")
            judge_result = self.judge.evaluate(self.target_dir)
            self.history.append({"phase": "judge", "result": judge_result})
            
            if judge_result["decision"] == "SUCCESS":
                print(f"\n🎉 SUCCESS after {self.iteration} iteration(s)!")
                return {
                    "status": "SUCCESS",
                    "iterations": self.iteration,
                    "final_score": judge_result.get("pylint_after"),
                    "history": self.history
                }
            
            # Prepare for retry
            print(f"⚠️ Tests failed. Retry reason: {judge_result.get('retry_reason')}")
            self.history[-1]["error"] = judge_result.get("retry_reason")
        
        # Max iterations reached
        print(f"\n❌ FAILED: Max iterations ({MAX_ITERATIONS}) reached")
        return {
            "status": "FAILURE",
            "reason": "Max iterations reached",
            "iterations": self.iteration,
            "history": self.history
        }
```

---

## 🚀 Main Entry Point (`main.py`)

```python
#!/usr/bin/env python3
"""
The Refactoring Swarm - Main Entry Point
Usage: python main.py --target_dir "./sandbox/buggy_code"
"""

import argparse
import sys
import os
from src.orchestrator import RefactoringOrchestrator
from src.utils.logger import log_experiment, ActionType

def main():
    # Parse CLI arguments
    parser = argparse.ArgumentParser(
        description="The Refactoring Swarm - Autonomous Code Refactoring System"
    )
    parser.add_argument(
        "--target_dir",
        type=str,
        required=True,
        help="Path to directory containing Python code to refactor"
    )
    args = parser.parse_args()
    
    # Validate target directory
    if not os.path.isdir(args.target_dir):
        print(f"❌ Error: Directory not found: {args.target_dir}")
        sys.exit(1)
    
    # Check for Python files
    py_files = [f for f in os.listdir(args.target_dir) if f.endswith('.py')]
    if not py_files:
        print(f"❌ Error: No Python files found in {args.target_dir}")
        sys.exit(1)
    
    print("=" * 60)
    print("🐝 THE REFACTORING SWARM 🐝")
    print("=" * 60)
    print(f"Target: {args.target_dir}")
    print(f"Files found: {len(py_files)}")
    print("=" * 60)
    
    # Run orchestrator
    try:
        orchestrator = RefactoringOrchestrator(args.target_dir)
        result = orchestrator.run()
        
        # Print final summary
        print("\n" + "=" * 60)
        print("📊 FINAL RESULTS")
        print("=" * 60)
        print(f"Status: {result['status']}")
        print(f"Iterations: {result['iterations']}")
        if result.get('final_score'):
            print(f"Final Pylint Score: {result['final_score']}/10")
        
        # Exit code based on result
        sys.exit(0 if result['status'] == 'SUCCESS' else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        log_experiment(
            agent_name="Orchestrator",
            model_used="system",
            action=ActionType.DEBUG,
            details={
                "input_prompt": "System error",
                "output_response": str(e),
                "error_type": type(e).__name__
            },
            status="FAILURE"
        )
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## 🧪 Sample Test Case (`sandbox/test_cases/buggy_example.py`)

```python
# A deliberately buggy file for testing

def calculate_average(numbers):
    # Bug 1: No docstring
    # Bug 2: No type hints
    # Bug 3: Division by zero possible
    total = 0
    for n in numbers:
        total = total + n
    return total / len(numbers)  # Crashes on empty list!

def find_maximum(lst):
    # Bug: Returns None for empty list instead of raising error
    max_val = lst[0]  # IndexError on empty list!
    for item in lst:
        if item > max_val:
            max_val = item
    return max_val

class Calculator:
    # Bug: No __init__ docstring
    def __init__(self):
        self.result = 0
    
    def add(self, x, y):
        # Bug: Unused self.result
        return x + y
    
    def divide(self, x, y):
        # Bug: No zero division handling
        return x / y
```

---

## ✅ Checklist Before Submission

- [ ] All 4 team members have made commits throughout the 10 days
- [ ] `python main.py --target_dir "./sandbox/test"` runs without errors
- [ ] Self-healing loop stops within 10 iterations
- [ ] `logs/experiment_data.json` is populated with all interactions
- [ ] All log entries have `input_prompt` and `output_response`
- [ ] `.env` file is in `.gitignore` (API key not exposed)
- [ ] Git history shows descriptive commit messages
- [ ] README.md explains how to run the project

---

## 🎯 Expected Output Format (`logs/experiment_data.json`)

```json
{
  "experiments": [
    {
      "id": "uuid-1234-5678",
      "timestamp": "2026-01-07T10:30:00",
      "agent_name": "Auditor_Agent",
      "model_used": "gemini-2.5-flash",
      "action": "ANALYSIS",
      "details": {
        "file_analyzed": "buggy_example.py",
        "input_prompt": "You are a Python expert. Analyze this code...",
        "output_response": "I found 5 issues: ...",
        "issues_found": 5
      },
      "status": "SUCCESS"
    },
    {
      "id": "uuid-2345-6789",
      "timestamp": "2026-01-07T10:31:00",
      "agent_name": "Fixer_Agent",
      "model_used": "gemini-2.5-flash",
      "action": "FIX",
      "details": {
        "input_prompt": "Fix the following issues in this code...",
        "output_response": "Here is the corrected code: ...",
        "files_modified": ["buggy_example.py"]
      },
      "status": "SUCCESS"
    }
  ]
}
```

---

*Document Version: 1.0 | Last Updated: January 6, 2026*
