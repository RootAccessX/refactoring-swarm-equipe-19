"""
Orchestrator - Manages the execution flow of the Refactoring Swarm.
Implements the self-healing loop: Auditor -> Fixer -> Judge -> Retry (max 10 iterations).
"""

import os
from pathlib import Path
from src.agents.auditor_agent import AuditorAgent
from src.agents.fixer_agent import FixerAgent
from src.agents.judge_agent import JudgeAgent
from src.sandbox_manager import SandboxManager
from src.utils.logger import log_experiment, ActionType
from src.config import MAX_ITERATIONS, DEFAULT_MODEL, RATE_LIMITS
from colorama import Fore, Style, init

# Initialize colorama for colored terminal output
init(autoreset=True)


class RefactoringOrchestrator:
    """
    Orchestrates the multi-agent refactoring workflow.
    """
    
    def __init__(self, target_dir: str):
        """
        Initialize the orchestrator.
        
        Args:
            target_dir: Directory containing Python files to refactor
        """
        self.target_dir = target_dir
        self.sandbox = SandboxManager(target_dir)
        
        # Initialize agents
        print(f"{Fore.CYAN}🤖 Initializing agents...")
        print(f"{Fore.CYAN}📡 Model: {DEFAULT_MODEL}")
        
        # Show rate limit info
        if DEFAULT_MODEL in RATE_LIMITS:
            limits = RATE_LIMITS[DEFAULT_MODEL]
            print(f"{Fore.CYAN}⏱️  Rate Limit: {limits['rpm']} requests/min ({limits['interval']:.1f}s between calls)")
        
        self.auditor = AuditorAgent()
        self.fixer = FixerAgent()
        self.judge = JudgeAgent()
        
        # Track execution state
        self.iteration = 0
        self.execution_log = []
    
    def run(self) -> dict:
        """
        Execute the refactoring workflow.
        
        Returns:
            Dictionary with final results
        """
        print(f"\n{Fore.GREEN}{'='*60}")
        print(f"{Fore.GREEN}🐝 REFACTORING SWARM INITIATED")
        print(f"{Fore.GREEN}{'='*60}\n")
        print(f"{Fore.YELLOW}📁 Target Directory: {self.target_dir}")
        print(f"{Fore.YELLOW}🔄 Max Iterations: {MAX_ITERATIONS}")
        print(f"{Fore.YELLOW}🤖 AI Model: {DEFAULT_MODEL}\n")
        
        # Log system startup
        log_experiment(
            agent_name="Orchestrator",
            model_used="System",
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": f"Starting refactoring on {self.target_dir}",
                "output_response": f"Initialized with max {MAX_ITERATIONS} iterations",
                "target_directory": self.target_dir
            },
            status="SUCCESS"
        )
        
        # PHASE 1: Audit
        print(f"{Fore.CYAN}{'─'*60}")
        print(f"{Fore.CYAN}PHASE 1: CODE AUDIT 🔍")
        print(f"{Fore.CYAN}{'─'*60}")
        
        audit_results = self.auditor.analyze(self.target_dir)
        
        if "error" in audit_results:
            print(f"{Fore.RED}❌ Audit failed: {audit_results['error']}")
            return {"status": "FAILED", "error": audit_results['error']}
        
        print(f"{Fore.GREEN}✅ Audit complete!")
        print(f"   📊 Files analyzed: {len(audit_results['files_analyzed'])}")
        print(f"   🐛 Total issues found: {audit_results['total_issues']}")
        
        if audit_results['total_issues'] == 0:
            print(f"\n{Fore.GREEN}🎉 No issues found! Code is already clean.")
            return {"status": "SUCCESS", "iterations": 0, "message": "No fixes needed"}
        
        # PHASE 2: Self-Healing Loop
        print(f"\n{Fore.CYAN}{'─'*60}")
        print(f"{Fore.CYAN}PHASE 2: SELF-HEALING LOOP 🔄")
        print(f"{Fore.CYAN}{'─'*60}\n")
        
        previous_feedback = None
        
        for iteration in range(1, MAX_ITERATIONS + 1):
            self.iteration = iteration
            
            print(f"{Fore.MAGENTA}╔{'═'*58}╗")
            print(f"{Fore.MAGENTA}║ ITERATION {iteration}/{MAX_ITERATIONS}{' '*(47-len(str(iteration)))}║")
            print(f"{Fore.MAGENTA}╚{'═'*58}╝")
            
            # Step 1: Fix
            print(f"\n{Fore.YELLOW}  🔧 Fixer Agent working...")
            fix_success = self._run_fixer(audit_results, previous_feedback)
            
            if not fix_success:
                print(f"{Fore.RED}  ❌ Fixer failed!")
                break
            
            print(f"{Fore.GREEN}  ✅ Fixes applied")
            
            # Step 2: Judge
            print(f"\n{Fore.YELLOW}  ⚖️  Judge Agent evaluating...")
            judge_decision = self._run_judge(audit_results)
            
            decision = judge_decision.get("decision", "RETRY")
            
            if decision == "SUCCESS":
                print(f"{Fore.GREEN}  ✅ Judge decision: SUCCESS!")
                print(f"\n{Fore.GREEN}{'='*60}")
                print(f"{Fore.GREEN}🎉 REFACTORING COMPLETE!")
                print(f"{Fore.GREEN}{'='*60}")
                print(f"{Fore.CYAN}📊 Final Statistics:")
                print(f"   ├─ Iterations used: {iteration}/{MAX_ITERATIONS}")
                print(f"   ├─ Files processed: {len(audit_results['files_analyzed'])}")
                print(f"   └─ Issues fixed: {audit_results['total_issues']}")
                
                return {
                    "status": "SUCCESS",
                    "iterations": iteration,
                    "files_processed": len(audit_results['files_analyzed']),
                    "issues_fixed": audit_results['total_issues']
                }
            else:
                print(f"{Fore.RED}  ❌ Judge decision: RETRY")
                print(f"{Fore.YELLOW}  📝 Reason: {judge_decision.get('retry_reason', 'Unknown')}")
                previous_feedback = judge_decision.get('feedback', '')
        
        # Max iterations reached
        print(f"\n{Fore.RED}{'='*60}")
        print(f"{Fore.RED}⚠️  MAX ITERATIONS REACHED")
        print(f"{Fore.RED}{'='*60}")
        print(f"{Fore.YELLOW}The system was unable to complete refactoring within {MAX_ITERATIONS} iterations.")
        
        return {
            "status": "MAX_ITERATIONS",
            "iterations": MAX_ITERATIONS,
            "message": "Max iterations reached without complete success"
        }
    
    def _run_fixer(self, audit_results: dict, previous_feedback: str = None) -> bool:
        """
        Run the Fixer agent on all files.
        
        Args:
            audit_results: Results from the Auditor
            previous_feedback: Feedback from previous Judge evaluation
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare file plans
            file_plans = []
            for file_path in audit_results['files_analyzed']:
                # Find issues for this file
                file_issues = [
                    issue for issue in audit_results.get('all_issues', [])
                    if issue.get('file') == file_path or os.path.basename(file_path) in str(issue)
                ]
                
                # Find refactoring plan for this file
                file_plan = None
                for plan_data in audit_results.get('refactoring_plans', []):
                    if plan_data['file'] == file_path:
                        file_plan = plan_data['plan']
                        break
                
                if not file_plan:
                    file_plan = ["Apply fixes based on issues found"]
                
                plan_dict = {
                    "issues": file_issues,
                    "refactoring_plan": file_plan if isinstance(file_plan, list) else [file_plan]
                }
                
                # Add previous feedback if exists
                if previous_feedback:
                    fix_result = self.fixer.fix_file(file_path, plan_dict, previous_feedback)
                else:
                    fix_result = self.fixer.fix_file(file_path, plan_dict)
                
                if not fix_result.get('success'):
                    print(f"{Fore.RED}    Failed to fix: {file_path}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}    Error in fixer: {str(e)}")
            return False
    
    def _run_judge(self, audit_results: dict) -> dict:
        """
        Run the Judge agent to evaluate fixes.
        
        Args:
            audit_results: Original audit results
        
        Returns:
            Judge's decision dictionary
        """
        try:
            # Evaluate the first file (for simplicity, can be extended for multiple files)
            if not audit_results['files_analyzed']:
                return {"decision": "RETRY", "retry_reason": "No files to evaluate"}
            
            file_path = audit_results['files_analyzed'][0]
            original_score = audit_results['pylint_scores'].get(file_path, 0.0)
            
            # Look for test directory
            test_dir = None
            base_dir = Path(self.target_dir)
            if (base_dir / "tests").exists():
                test_dir = str(base_dir / "tests")
            
            evaluation = self.judge.evaluate(file_path, original_score, test_dir)
            
            return evaluation
            
        except Exception as e:
            return {
                "decision": "RETRY",
                "retry_reason": f"Judge evaluation error: {str(e)}"
            }
