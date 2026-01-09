# 🚀 Quick Start Guide

## Installation (3 steps)

### 1. Activate Virtual Environment
```bas
venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Add API Key
Edit `.env` file and add your Google API key:
```env
GOOGLE_API_KEY=your_actual_google_api_key_here
```

Get API key from: https://makersuite.google.com/app/apikey

---

## Running the System

### Basic Usage
```bash
python main.py --target_dir ./sandbox/test_cases
```

### On Your Own Code
```bash
python main.py --target_dir C:\path\to\your\python\code
```

---

## What to Expect

1. **Colored Output**: The system uses colors to show progress
   - 🔵 Blue = Info
   - 🟢 Green = Success
   - 🔴 Red = Error/Retry
   - 🟡 Yellow = Working

2. **Phases**:
   - Phase 1: Audit (analyzes code)
   - Phase 2: Self-Healing Loop (fix and validate)

3. **Duration**: Depends on code complexity and API response time
   - Simple files: 1-2 minutes
   - Complex files: 5-10 minutes

4. **Output**:
   - Fixed code (overwrites originals)
   - Backup files (.backup suffix)
   - Logs in `logs/experiment_data.json`

---

## Troubleshooting

### "GOOGLE_API_KEY not found"
→ Edit `.env` and add your API key

### "Pylint not installed"
→ Run: `pip install -r requirements.txt`

### "Directory not found"
→ Check the path you provided is correct

### Import errors
→ Make sure you're in the project root directory when running

---

## File Structure Quick Reference

```
📁 Your Project
├── 📄 main.py              ← RUN THIS
├── 📄 .env                 ← ADD API KEY HERE
├── 📁 src/
│   ├── orchestrator.py     ← Main logic
│   ├── agents/             ← AI agents
│   ├── tools/              ← Utilities
│   └── utils/              ← Logger
├── 📁 sandbox/
│   └── test_cases/         ← Test files
└── 📁 logs/
    └── experiment_data.json ← All logs
```

---

## Example Session

```bash
C:\...\refactoring-swarm-equipe-19> python main.py --target_dir ./sandbox/test_cases

🤖 Initializing agents...

============================================================
🐝 REFACTORING SWARM INITIATED
============================================================

📁 Target Directory: ./sandbox/test_cases
🔄 Max Iterations: 10

────────────────────────────────────────────────────────────
PHASE 1: CODE AUDIT 🔍
────────────────────────────────────────────────────────────
✅ Audit complete!
   📊 Files analyzed: 3
   🐛 Total issues found: 15

────────────────────────────────────────────────────────────
PHASE 2: SELF-HEALING LOOP 🔄
────────────────────────────────────────────────────────────

╔══════════════════════════════════════════════════════════╗
║ ITERATION 1/10                                          ║
╚══════════════════════════════════════════════════════════╝

  🔧 Fixer Agent working...
  ✅ Fixes applied

  ⚖️  Judge Agent evaluating...
  ✅ Judge decision: SUCCESS!

============================================================
🎉 REFACTORING COMPLETE!
============================================================
📊 Final Statistics:
   ├─ Iterations used: 1/10
   ├─ Files processed: 3
   └─ Issues fixed: 15

✅ MISSION COMPLETE
```

---

## Advanced Usage

### Check Logs
View all agent interactions:
```bash
type logs\experiment_data.json
```

### Restore Backup
If you need to restore original files:
```bash
# Backup files have .backup extension
copy file.py.backup file.py
```

### Run on Specific File
```bash
# Create a directory with just that file
mkdir temp_target
copy myfile.py temp_target\
python main.py --target_dir temp_target
```

---

## Tips

1. **Start Small**: Test on a few files first
2. **Check Backups**: Original files are saved with `.backup` extension
3. **Review Logs**: Check `logs/experiment_data.json` for detailed info
4. **API Limits**: Free tier has rate limits, might need to wait between runs
5. **Internet Required**: System needs internet to call Gemini API

---

## Need Help?

1. Check [README.md](README.md) for full documentation
2. Check [SETUP_COMPLETE.md](SETUP_COMPLETE.md) for architecture details
3. Check [project_plan.md](project_plan.md) for project structure
4. Check [solution.md](solution.md) for implementation details

---

**Ready?** Run: `python main.py --target_dir ./sandbox/test_cases`

**Good luck!** 🐝✨
