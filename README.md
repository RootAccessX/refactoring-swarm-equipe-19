# The Refactoring Swarm 🐝

A multi-agent system that autonomously refactors buggy Python code using AI agents.

## 🏗️ Architecture

The system uses 3 specialized AI agents orchestrated in a self-healing loop:

1. **Auditor Agent 🔍** - Analyzes code and creates refactoring plan
2. **Fixer Agent 🔧** - Applies fixes based on the plan
3. **Judge Agent ⚖️** - Validates fixes and decides if retry is needed

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd refactoring-swarm-equipe-19
```

### 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Key

Create a `.env` file and add your Google API key:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

**Get your free API key**: https://makersuite.google.com/app/apikey

### 5. Run

```bash
python main.py --target_dir ./sandbox/test_cases
```

⚡ **Note**: The system uses **Gemini 1.5 Flash** by default with automatic rate limiting (15 requests/min). See [RATE_LIMITS.md](RATE_LIMITS.md) for details.

## 📁 Project Structure

```
refactoring-swarm-equipe-19/
├── main.py                     # Entry point
├── requirements.txt            # Dependencies
├── .env                       # API keys (create this)
├── .env.example              # Template
│
├── src/
│   ├── orchestrator.py       # Main workflow controller
│   ├── sandbox_manager.py    # Security layer
│   │
│   ├── agents/              # AI Agents
│   │   ├── base_agent.py
│   │   ├── auditor_agent.py
│   │   ├── fixer_agent.py
│   │   └── judge_agent.py
│   │
│   ├── prompts/             # Agent prompts
│   │   ├── auditor_prompt.py
│   │   ├── fixer_prompt.py
│   │   └── judge_prompt.py
│   │
│   ├── tools/               # Utility tools
│   │   ├── file_tools.py
│   │   ├── pylint_tool.py
│   │   └── pytest_tool.py
│   │
│   └── utils/
│       └── logger.py        # Experiment logging
│
├── logs/
│   └── experiment_data.json  # Execution logs
│
└── sandbox/
    └── test_cases/          # Test files
        ├── buggy_code_1.py
        ├── buggy_code_2.py
        └── buggy_code_3.py
```

## 🔄 How It Works

1. **Audit Phase**: Auditor analyzes code and identifies issues
2. **Self-Healing Loop** (max 10 iterations):
   - Fixer applies fixes
   - Judge evaluates the result
   - If not perfect, retry with feedback
3. **Success**: All issues fixed and tests pass

## 🛠️ Usage Examples

```bash
# Refactor test cases
python main.py --target_dir ./sandbox/test_cases

# Refactor your own code
python main.py --target_dir /path/to/your/code
```

## 📊 Logging

All agent interactions are logged to `logs/experiment_data.json`:
- Input prompts
- Model responses
- Actions performed
- Success/failure status

## 🔒 Security

The sandbox manager ensures all operations stay within the target directory.

## 🧪 Testing

Run the setup check:

```bash
python check_setup.py
```

## 📝 Requirements

- Python 3.8+
- Google Gemini API key
- Dependencies in requirements.txt

## 🤝 Team Structure

| Role | Responsibilities |
|------|-----------------|
| Orchestrator | Main workflow, integration |
| Toolsmith | Tools, sandbox security |
| Prompt Engineer | Agent prompts and logic |
| Data Manager | Logging, test datasets |

## 📞 Support

For issues or questions, refer to the project documentation in `project_plan.md` and `solution.md`.

---

**Created by**: Team 19 - Refactoring Swarm
**Date**: January 2026
