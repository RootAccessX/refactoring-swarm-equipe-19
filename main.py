"""
Main entry point for the Refactoring Swarm.
Usage: python main.py --target_dir <path_to_code>
"""

import argparse
import sys
import os
from dotenv import load_dotenv
from src.orchestrator import RefactoringOrchestrator
from colorama import Fore, Style, init

# Load environment variables
load_dotenv()

# Initialize colorama
init(autoreset=True)


def main():
    """Main function to run the Refactoring Swarm."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="🐝 The Refactoring Swarm - Autonomous Code Refactoring System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --target_dir ./sandbox/test_cases
  python main.py --target_dir /path/to/buggy/code
        """
    )
    parser.add_argument(
        "--target_dir",
        type=str,
        required=True,
        help="Directory containing Python files to refactor"
    )
    
    args = parser.parse_args()
    
    # Validate target directory
    if not os.path.exists(args.target_dir):
        print(f"{Fore.RED}❌ Error: Directory '{args.target_dir}' not found.")
        sys.exit(1)
    
    if not os.path.isdir(args.target_dir):
        print(f"{Fore.RED}❌ Error: '{args.target_dir}' is not a directory.")
        sys.exit(1)
    
    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print(f"{Fore.RED}❌ Error: GOOGLE_API_KEY not found in environment variables.")
        print(f"{Fore.YELLOW}💡 Please set your API key in the .env file:")
        print(f"   GOOGLE_API_KEY=your_api_key_here")
        sys.exit(1)
    
    try:
        # Initialize and run the orchestrator
        orchestrator = RefactoringOrchestrator(args.target_dir)
        results = orchestrator.run()
        
        # Exit with appropriate status code
        if results.get("status") == "SUCCESS":
            print(f"\n{Fore.GREEN}✅ MISSION COMPLETE")
            sys.exit(0)
        else:
            print(f"\n{Fore.YELLOW}⚠️  MISSION INCOMPLETE")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}⚠️  Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Fore.RED}❌ Fatal Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()