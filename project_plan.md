# 🐝 The Refactoring Swarm - Project Plan & Solution

## 📅 Timeline: January 7, 2026 → January 16, 2026 (10 Working Days)

---

## 👥 Team Roles & Responsibilities

| Role | Member | Main Files | Branch Prefix |
|------|--------|------------|---------------|
| 🧠 **Orchestrateur (Lead Dev)** | Member 1 | `main.py`, `src/orchestrator.py` | `orch/` |
| 🛠️ **Toolsmith** | Member 2 | `src/tools/`, `src/sandbox_manager.py` | `tools/` |
| 💬 **Prompt Engineer** | Member 3 | `src/prompts/`, `src/agents/` | `prompt/` |
| 📊 **Quality & Data Manager** | Member 4 | `src/utils/logger.py`, `logs/`, tests | `data/` |

---

## 🔄 Dependency Graph (Who Waits for Whom?)

```
┌─────────────────────────────────────────────────────────────────┐
│                        DEPENDENCY FLOW                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   [Toolsmith] ──────────────────┐                               │
│       │                         │                               │
│       ▼                         ▼                               │
│   [Data Manager] ────────► [Prompt Engineer]                    │
│       │                         │                               │
│       └──────────┬──────────────┘                               │
│                  ▼                                              │
│            [Orchestrateur]                                      │
│                  │                                              │
│                  ▼                                              │
│           [INTEGRATION]                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Key Dependencies:**
1. **Toolsmith** must commit tools BEFORE Prompt Engineer can use them in agents
2. **Data Manager** must commit logger BEFORE anyone can log actions
3. **Prompt Engineer** must commit agents BEFORE Orchestrateur can orchestrate them
4. **Orchestrateur** integrates AFTER all components are ready

---

## 📆 Day-by-Day Commit Schedule

### **Day 1 - Tuesday, January 7** 🚀 SETUP DAY

| Order | Member | Branch | Commit Message | Description |
|-------|--------|--------|----------------|-------------|
| 1 | **ALL** | `main` | `init: clone template and setup venv` | Everyone clones repo, creates venv, runs `check_setup.py` |
| 2 | **Data Manager** | `data/logger-base` | `feat: implement base logger with ActionType enum` | Create `src/utils/logger.py` with `log_experiment()` function |
| 3 | **Toolsmith** | `tools/file-operations` | `feat: add file read/write tools` | Create `src/tools/file_tools.py` with safe read/write functions |

**🔒 End of Day 1 Merges:** Data Manager → main, Toolsmith → main

---

### **Day 2 - Wednesday, January 8** 🛠️ TOOLS DAY

| Order | Member | Branch | Commit Message | Description |
|-------|--------|--------|----------------|-------------|
| 1 | **Toolsmith** | `tools/analysis-tools` | `feat: add pylint execution wrapper` | Create `src/tools/pylint_tool.py` |
| 2 | **Toolsmith** | `tools/analysis-tools` | `feat: add pytest execution wrapper` | Create `src/tools/pytest_tool.py` |
| 3 | **Toolsmith** | `tools/sandbox` | `feat: implement sandbox security manager` | Create `src/sandbox_manager.py` - prevent writes outside sandbox |
| 4 | **Data Manager** | `data/logger-enhance` | `feat: add validation for mandatory fields` | Add checks for `input_prompt` and `output_response` |

**🔒 End of Day 2 Merges:** Toolsmith → main, Data Manager → main

---

### **Day 3 - Thursday, January 9** 💬 PROMPTS DAY

| Order | Member | Branch | Commit Message | Description |
|-------|--------|--------|----------------|-------------|
| 1 | **Prompt Engineer** | `prompt/auditor-system` | `feat: create auditor agent system prompt` | Create `src/prompts/auditor_prompt.py` |
| 2 | **Prompt Engineer** | `prompt/auditor-agent` | `feat: implement auditor agent class` | Create `src/agents/auditor_agent.py` |
| 3 | **Data Manager** | `data/test-dataset` | `feat: create internal test dataset` | Add buggy Python files in `sandbox/test_cases/` |
| 4 | **Orchestrateur** | `orch/cli-args` | `feat: add CLI argument parsing in main.py` | Implement `--target_dir` argument handling |

**🔒 End of Day 3 Merges:** Prompt Engineer → main, Data Manager → main, Orchestrateur → main

---

### **Day 4 - Friday, January 10** 🔧 FIXER AGENT DAY

| Order | Member | Branch | Commit Message | Description |
|-------|--------|--------|----------------|-------------|
| 1 | **Prompt Engineer** | `prompt/fixer-system` | `feat: create fixer agent system prompt` | Create `src/prompts/fixer_prompt.py` |
| 2 | **Prompt Engineer** | `prompt/fixer-agent` | `feat: implement fixer agent class` | Create `src/agents/fixer_agent.py` |
| 3 | **Toolsmith** | `tools/code-modifier` | `feat: add code modification utilities` | Functions to apply fixes to code files |
| 4 | **Data Manager** | `data/log-validation` | `feat: add JSON schema validation for logs` | Validate `experiment_data.json` format |

**🔒 End of Day 4 Merges:** ALL branches → main

---

### **Day 5 - Saturday, January 11** ⚖️ JUDGE AGENT DAY

| Order | Member | Branch | Commit Message | Description |
|-------|--------|--------|----------------|-------------|
| 1 | **Prompt Engineer** | `prompt/judge-system` | `feat: create judge agent system prompt` | Create `src/prompts/judge_prompt.py` |
| 2 | **Prompt Engineer** | `prompt/judge-agent` | `feat: implement judge agent class` | Create `src/agents/judge_agent.py` |
| 3 | **Orchestrateur** | `orch/agent-registry` | `feat: create agent registry and loader` | Central place to instantiate all agents |

**🔒 End of Day 5 Merges:** Prompt Engineer → main, Orchestrateur → main

---

### **Day 6 - Sunday, January 12** 🔄 LOOP DAY

| Order | Member | Branch | Commit Message | Description |
|-------|--------|--------|----------------|-------------|
| 1 | **Orchestrateur** | `orch/workflow-graph` | `feat: implement execution graph (LangGraph/CrewAI)` | Create `src/orchestrator.py` with agent workflow |
| 2 | **Orchestrateur** | `orch/self-healing` | `feat: add self-healing loop logic` | Implement retry mechanism (max 10 iterations) |
| 3 | **Data Manager** | `data/iteration-tracking` | `feat: add iteration tracking to logs` | Track loop iterations in `experiment_data.json` |

**🔒 End of Day 6 Merges:** Orchestrateur → main, Data Manager → main

---

### **Day 7 - Monday, January 13** 🧪 TESTING DAY

| Order | Member | Branch | Commit Message | Description |
|-------|--------|--------|----------------|-------------|
| 1 | **Data Manager** | `data/trap-files` | `feat: add complex trap test cases` | Create edge cases to stress-test the system |
| 2 | **Toolsmith** | `tools/error-handling` | `feat: add robust error handling to all tools` | Try-catch, timeout handling |
| 3 | **Prompt Engineer** | `prompt/optimize` | `fix: optimize prompts to reduce hallucinations` | Refine prompts based on test results |
| 4 | **ALL** | - | Manual testing on internal dataset | Run full system, check logs |

**🔒 End of Day 7 Merges:** ALL branches → main

---

### **Day 8 - Tuesday, January 14** 🐛 BUGFIX DAY

| Order | Member | Branch | Commit Message | Description |
|-------|--------|--------|----------------|-------------|
| 1 | **ALL** | `fix/[issue-name]` | `fix: [description of bug]` | Fix bugs found during testing |
| 2 | **Orchestrateur** | `orch/graceful-exit` | `feat: add graceful exit and cleanup` | Ensure system stops cleanly |
| 3 | **Data Manager** | `data/final-validation` | `feat: add final log completeness check` | Verify all required fields present |

**🔒 End of Day 8 Merges:** ALL fixes → main

---

### **Day 9 - Wednesday, January 15** 📝 DOCUMENTATION DAY

| Order | Member | Branch | Commit Message | Description |
|-------|--------|--------|----------------|-------------|
| 1 | **Orchestrateur** | `docs/readme` | `docs: update README with usage instructions` | How to run, dependencies, etc. |
| 2 | **Prompt Engineer** | `docs/prompts` | `docs: document prompt engineering decisions` | Explain prompt design choices |
| 3 | **Data Manager** | `data/force-logs` | `chore: force add experiment_data.json` | `git add -f logs/experiment_data.json` |
| 4 | **Toolsmith** | `docs/tools-api` | `docs: document tools API` | Document all tool functions |

**🔒 End of Day 9 Merges:** ALL → main

---

### **Day 10 - Thursday, January 16** 🚀 FINAL DAY

| Order | Member | Branch | Commit Message | Description |
|-------|--------|--------|----------------|-------------|
| 1 | **ALL** | `main` | Final integration testing | Run on fresh clone |
| 2 | **Data Manager** | `main` | `chore: final log verification` | Ensure `experiment_data.json` is complete |
| 3 | **Orchestrateur** | `main` | `release: v1.0.0 ready for submission` | Final tag |

---

## 🗂️ Recommended File Structure

```
/refactoring-swarm-template
│
├── main.py                          # 🧠 Orchestrateur
├── requirements.txt
├── .env
├── check_setup.py
│
├── /src
│   ├── __init__.py
│   ├── orchestrator.py              # 🧠 Orchestrateur
│   │
│   ├── /agents                      # 💬 Prompt Engineer
│   │   ├── __init__.py
│   │   ├── auditor_agent.py
│   │   ├── fixer_agent.py
│   │   └── judge_agent.py
│   │
│   ├── /prompts                     # 💬 Prompt Engineer
│   │   ├── __init__.py
│   │   ├── auditor_prompt.py
│   │   ├── fixer_prompt.py
│   │   └── judge_prompt.py
│   │
│   ├── /tools                       # 🛠️ Toolsmith
│   │   ├── __init__.py
│   │   ├── file_tools.py
│   │   ├── pylint_tool.py
│   │   ├── pytest_tool.py
│   │   └── code_modifier.py
│   │
│   ├── /utils                       # 📊 Data Manager
│   │   ├── __init__.py
│   │   └── logger.py
│   │
│   └── sandbox_manager.py           # 🛠️ Toolsmith
│
├── /logs                            # 📊 Data Manager
│   └── experiment_data.json
│
└── /sandbox
    └── /test_cases                  # 📊 Data Manager
        ├── buggy_code_1.py
        ├── buggy_code_2.py
        └── ...
```

---

## ⚠️ Communication Protocol

### Daily Standup (5 min on Discord/Slack)
1. What did you commit yesterday?
2. What will you commit today?
3. Any blockers? Need someone else's code first?

### Before Modifying Shared Files
```
🚨 ALWAYS ASK IN CHAT FIRST:
"Hey, I need to modify [file]. Is anyone working on it?"
```

### Branch Naming Convention
```
[prefix]/[short-description]

Examples:
- tools/pylint-wrapper
- prompt/auditor-v2
- orch/self-healing-loop
- data/log-validation
- fix/json-parsing-error
- docs/readme-update
```

---

## 🔀 Merge Order Rules

```
⚠️ GOLDEN RULE: Never merge to main if your code depends on 
                someone else's uncommitted work!
```

**Safe Merge Order (per day):**
1. Toolsmith (provides tools)
2. Data Manager (provides logging)
3. Prompt Engineer (uses tools + logging)
4. Orchestrateur (uses everything)

---

## 🆘 Conflict Resolution Checklist

If you get a merge conflict:

1. ✅ **STOP** - Don't force push anything
2. ✅ **COMMUNICATE** - Tell your team on Discord
3. ✅ **PULL** - `git pull origin main`
4. ✅ **RESOLVE** - In VS Code, use the conflict editor
5. ✅ **TEST** - Run `python check_setup.py` after resolving
6. ✅ **COMMIT** - `git commit -m "resolve: merge conflict in [file]"`
7. ✅ **PUSH** - `git push origin [your-branch]`

---

## 📊 Success Metrics Checklist

Before submission, verify:

- [ ] `python main.py --target_dir "./sandbox/test_cases"` runs without crash
- [ ] System stops within 10 iterations (no infinite loop)
- [ ] `logs/experiment_data.json` contains complete history
- [ ] All prompts have `input_prompt` and `output_response` logged
- [ ] Pylint score improves after refactoring
- [ ] Unit tests pass on fixed code
- [ ] Git history shows regular commits (not just 1 final commit)
- [ ] `.env` file is NOT committed (check `.gitignore`)

---

## 📞 Emergency Contacts

| Situation | Who to Contact |
|-----------|----------------|
| Git/Branch issues | Orchestrateur (Lead Dev) |
| Tool functions not working | Toolsmith |
| Agent not responding correctly | Prompt Engineer |
| Logs missing or malformed | Data Manager |

---

*Good luck! Remember: Communication is key! 🐝*
