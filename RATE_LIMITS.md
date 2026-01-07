# ⚡ Rate Limits & API Usage Guide

## 📊 Google Gemini API Rate Limits

The system has been **updated with proper rate limiting** to respect Google's API quotas:

| Model | RPM | TPM | RPD | Default Interval |
|-------|-----|-----|-----|------------------|
| **Gemini 1.5 Flash** ✅ | 15 | 1,000,000 | 1,500 | ~4.5s |
| Gemini 2.0 Flash | 10 | 250,000 | 500 | ~6.5s |
| Gemini 1.5 Pro | 2 | 32,000 | 50 | ~31s |

**Legend:**
- RPM = Requests Per Minute
- TPM = Tokens Per Minute (Input + Output)
- RPD = Requests Per Day

---

## ✅ What's Been Fixed

### 1. **Automatic Rate Limiting**
The system now **automatically waits** between API calls to respect rate limits.

```python
# In src/agents/base_agent.py
# Waits 4.5 seconds between calls for Gemini 1.5 Flash
# Waits 6.5 seconds for Gemini 2.0 Flash
# Shared across all agents to prevent parallel violations
```

### 2. **Smart Retry Logic**
If a rate limit error occurs (429), the system:
- ✅ Automatically retries (up to 3 times)
- ✅ Uses exponential backoff (waits longer each retry)
- ✅ Shows progress messages to the user

### 3. **Model Configuration**
Default model is now **Gemini 1.5 Flash** (best for free tier):
- ✅ 15 requests/minute (fastest)
- ✅ 1M tokens/minute (largest)
- ✅ 1,500 requests/day (highest daily limit)

---

## 🔧 Configuration

### Current Settings (in `src/config.py`)

```python
DEFAULT_MODEL = "gemini-1.5-flash"  # Recommended for free tier
MAX_ITERATIONS = 10  # Self-healing loop limit
```

### Changing the Model

Edit `src/config.py`:

```python
# Option 1: Fastest (recommended for free tier)
DEFAULT_MODEL = "gemini-1.5-flash"

# Option 2: Medium speed
DEFAULT_MODEL = "gemini-2.0-flash-exp"

# Option 3: Most capable but slowest
DEFAULT_MODEL = "gemini-1.5-pro"
```

---

## 📈 Estimated Execution Time

### With Gemini 1.5 Flash (Default)

For **3 test files**, **1 iteration**:
- Auditor: 3 files × 4.5s = ~13.5s
- Fixer: 3 files × 4.5s = ~13.5s
- Judge: 1 call × 4.5s = ~4.5s
- **Total per iteration: ~31.5 seconds**

Full run (if max iterations needed):
- **~5-6 minutes** for complete refactoring

### With Gemini 2.0 Flash

Same scenario:
- **Total per iteration: ~45 seconds**
- Full run: **~7-8 minutes**

### With Gemini 1.5 Pro

Same scenario:
- **Total per iteration: ~120 seconds (2 minutes)**
- Full run: **~20 minutes**

---

## 🚨 Avoiding Rate Limit Issues

### ✅ DO:
1. **Use default model** (Gemini 1.5 Flash)
2. **Keep test datasets small** during development
3. **Monitor the console** - watch for rate limit warnings
4. **Check daily quota** - free tier has 1,500 requests/day

### ❌ DON'T:
1. **Run multiple instances** simultaneously
2. **Disable rate limiting** (it's there for a reason)
3. **Use Pro model** unless you need maximum quality
4. **Process large directories** on first run

---

## 🔍 Monitoring Usage

### During Execution

Watch for these messages:
```bash
⚠️  Rate limit hit, waiting 9s...  # Automatic retry
⏱️  Rate Limit: 15 requests/min   # Initial setup info
```

### Checking Logs

View all API calls in `logs/experiment_data.json`:
```bash
type logs\experiment_data.json
```

Count requests made:
```powershell
(Get-Content logs\experiment_data.json | ConvertFrom-Json).Count
```

---

## 📦 Rate Limit Details

### How It Works

1. **Shared Timer**: All agents share a single timer (class variable)
2. **Minimum Interval**: System waits `interval` seconds between ANY API calls
3. **Retry on Error**: If 429 error occurs, doubles wait time and retries
4. **Configurable**: Change model in `src/config.py` to adjust speed

### Example Timeline

```
Time  | Action
------|-------------------------------------------
00:00 | Auditor calls API (file 1)
00:04 | [wait 4.5s]
00:04 | Auditor calls API (file 2)
00:09 | [wait 4.5s]
00:09 | Auditor calls API (file 3)
00:13 | [wait 4.5s]
00:13 | Fixer calls API (file 1)
...
```

---

## 💰 Cost Considerations

### Free Tier Limits (per day)
- Gemini 1.5 Flash: **1,500 requests** ✅
- Gemini 2.0 Flash: **500 requests**
- Gemini 1.5 Pro: **50 requests**

### Example Usage
Processing 10 files with 3 iterations:
- Auditor: 10 calls
- Fixer: 10 calls
- Judge: 3 calls
- **Total: ~23 requests**

You can process **~65 sets of 10 files/day** on free tier (1.5 Flash)!

---

## 🛠️ Troubleshooting

### "Rate limit exceeded"
✅ **Solution**: System auto-retries. Just wait.

### "Quota exceeded for today"
✅ **Solution**: Wait until tomorrow or upgrade to paid tier

### "Too slow!"
✅ **Solutions**:
1. Keep using 1.5 Flash (fastest allowed)
2. Process fewer files at once
3. Reduce MAX_ITERATIONS in config
4. Consider upgrading to paid tier

### Want to go faster?
⚠️ **Not recommended** - Could get your API key temporarily blocked

---

## 📚 References

- [Google Gemini API Docs](https://ai.google.dev/gemini-api/docs)
- [Rate Limits Documentation](https://ai.google.dev/gemini-api/docs/quota)
- Our config: `src/config.py`
- Implementation: `src/agents/base_agent.py`

---

## ✨ Summary

✅ **Rate limiting is NOW IMPLEMENTED**  
✅ **Default model: Gemini 1.5 Flash (best for free tier)**  
✅ **Automatic retries with exponential backoff**  
✅ **Shared timer prevents parallel violations**  
✅ **~30-45 seconds per iteration** (reasonable speed)  
✅ **Safe to use without exceeding quotas**  

**You're good to go!** 🚀
