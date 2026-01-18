import argparse
import sys
import os
from dotenv import load_dotenv
from src.utils.logger import log_experiment, ActionType  # Import ActionType
from src.orchestrator import RefactoringOrchestrator

load_dotenv()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target_dir", type=str, required=True)
    args = parser.parse_args()

    if not os.path.exists(args.target_dir):
        print(f"❌ Dossier {args.target_dir} introuvable.")
        sys.exit(1)

    print(f"🚀 DEMARRAGE SUR : {args.target_dir}", flush=True)

    # Correct log_experiment call with ActionType and required details dict
    log_experiment(
        agent_name="System",
        model_used="N/A",
        action=ActionType.ANALYSIS,
        details={
            "input_prompt": f"Starting system on target directory {args.target_dir}",
            "output_response": "Initialization completed"
        }
    )

    # Initialize and run the orchestrator
    orchestrator = RefactoringOrchestrator(args.target_dir)
    results = orchestrator.run()

    print("✅ MISSION_COMPLETE", flush=True)

if __name__ == "__main__":
    main()
