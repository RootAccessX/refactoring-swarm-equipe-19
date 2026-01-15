"""
Final pre-submission validation checks.
"""

import json
import sys
from src.utils.log_validator import validate_log_file

def run_final_checks() -> bool:
    """
    Run all final validation checks.
    
    Returns:
        True if all checks pass, False otherwise
    """
    print("=" * 60)
    print("🔍 RUNNING FINAL VALIDATION CHECKS")
    print("=" * 60)
    
    all_passed = True
    
    # Check 1: Log file exists and is valid
    print("\n1️⃣ Validating log file structure...")
    valid, error = validate_log_file()
    if valid:
        print("   ✅ Log file is valid")
    else:
        print(f"   ❌ FAILED: {error}")
        all_passed = False
    
    # Check 2: All experiments have required fields
    print("\n2️⃣ Checking experiment completeness...")
    try:
        with open("logs/experiment_data.json", 'r') as f:
            data = json.load(f)
        
        experiments = data.get("experiments", [])
        if len(experiments) == 0:
            print("   ❌ FAILED: No experiments logged!")
            all_passed = False
        else:
            print(f"   ✅ Found {len(experiments)} experiments")
            
            # Check each has input_prompt and output_response
            missing_prompts = 0
            missing_responses = 0
            for exp in experiments:
                if "input_prompt" not in exp.get("details", {}):
                    missing_prompts += 1
                if "output_response" not in exp.get("details", {}):
                    missing_responses += 1
            
            if missing_prompts > 0:
                print(f"   ❌ FAILED: {missing_prompts} experiments missing input_prompt")
                all_passed = False
            if missing_responses > 0:
                print(f"   ❌ FAILED: {missing_responses} experiments missing output_response")
                all_passed = False
            
            if missing_prompts == 0 and missing_responses == 0:
                print("   ✅ All experiments have required fields")
    
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        all_passed = False
    
    # Check 3: Agents are represented
    print("\n3️⃣ Checking agent participation...")
    try:
        agents = set()
        for exp in experiments:
            agents.add(exp.get("agent_name", "unknown"))
        
        expected_agents = ["Auditor_Agent", "Fixer_Agent", "Judge_Agent"]
        for agent in expected_agents:
            if agent in agents:
                print(f"   ✅ {agent} present")
            else:
                print(f"   ⚠️  WARNING: {agent} not found in logs")
    
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
    
    # Final verdict
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL CHECKS PASSED! Ready for submission.")
        print("=" * 60)
        return True
    else:
        print("❌ SOME CHECKS FAILED! Fix issues before submitting.")
        print("=" * 60)
        return False

if __name__ == "__main__":
    passed = run_final_checks()
    sys.exit(0 if passed else 1)

