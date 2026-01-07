# Manual Testing Guide - Legalize AI Music

This guide will walk you through manually testing all features of the application.

## Prerequisites

Before testing, verify these are installed and running:

### 1. Check Python Environment
```bash
cd /mnt/d/AI_Projects/ralph_app
./venv/bin/python --version
```
**Expected:** Python 3.12.x

### 2. Check Ollama is Running
```bash
curl http://localhost:11434/api/version
```
**Expected:** `{"version":"0.11.4"}` or similar

### 3. Check llama3.1:8b Model is Installed
```bash
ollama list | grep llama3.1
```
**Expected:** You should see `llama3.1:8b` in the list

If not installed:
```bash
ollama pull llama3.1:8b
```

---

## Test 1: Verify Installation

### Navigate to Project Directory
```bash
cd /mnt/d/AI_Projects/ralph_app
```

### Check Virtual Environment
```bash
ls -la venv/
```
**Expected:** You should see `bin/`, `lib/`, `pyvenv.cfg`

### Verify CLI Module
```bash
cd src
../venv/bin/python -m workflow.cli --help
```

**Expected Output:**
```
Usage: python -m workflow.cli [OPTIONS] COMMAND [ARGS]...

  Suno AI to MIDI FL Studio Automation CLI.

Options:
  --help  Show this message and exit.

Commands:
  convert      Convert audio files to MIDI.
  start        Start the workflow with a prompt.
  status       Check workflow status.
  stop         Stop the running workflow.
  test-ollama  Test Ollama connection.
```

✅ **Pass Criteria:** Help menu displays all 5 commands

---

## Test 2: Ollama Connection Test

### Run Ollama Test Command
```bash
../venv/bin/python -m workflow.cli test-ollama --model llama3.1:8b
```

**Expected Output:**
```
Testing Ollama connection with model: llama3.1:8b
✓ Ollama connection successful!
Response: Connection successful!
```

✅ **Pass Criteria:**
- Green checkmark appears
- "Connection successful!" message received
- No error messages (warnings are OK)

❌ **If it fails:**
- Check if Ollama is running: `ollama serve`
- Verify model is installed: `ollama list`
- Check port 11434 is not blocked

---

## Test 3: Status Check

### Check Current Status
```bash
../venv/bin/python -m workflow.cli status
```

**Expected Output:**
```
                       Workflow Status
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Property         ┃ Value                                   ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Status           │ Idle                                    │
│ Output Directory │ /mnt/d/AI_Projects/ralph_app/src/output │
│ Model            │ Not set                                 │
└──────────────────┴─────────────────────────────────────────┘
```

✅ **Pass Criteria:**
- Table displays correctly
- Status shows "Idle"
- Output directory path is shown

---

## Test 4: Simple Workflow Task (Sync Mode)

### Run a Basic Task
```bash
../venv/bin/python -m workflow.cli start --prompt "Explain audio to MIDI conversion in one sentence" --model llama3.1:8b
```

**What You Should See:**

1. **Startup Panel:**
```
╭────────────────────────── Suno AI to MIDI Workflow ──────────────────────────╮
│ Starting Workflow                                                            │
│                                                                              │
│ Prompt: Explain audio to MIDI conversion in one sentence                     │
│ Model: llama3.1:8b                                                           │
│ Ollama URL: http://localhost:11434                                           │
╰──────────────────────────────────────────────────────────────────────────────╯
```

2. **Processing Spinner:**
```
⠙ Processing workflow...
```

3. **Success Message:**
```
✓ Workflow completed successfully!

Agent Output:
[AI-generated response about audio to MIDI conversion]
```

✅ **Pass Criteria:**
- Workflow starts without errors
- Processing spinner appears
- Completion message shows
- AI response is relevant and coherent
- Process takes 5-30 seconds

❌ **If it fails:**
- Check Ollama is running
- Verify llama3.1:8b model is available
- Check for error messages

---

## Test 5: Complex Workflow Task

### Test with More Complex Prompt
```bash
../venv/bin/python -m workflow.cli start --prompt "Create a step-by-step plan for converting a guitar recording to MIDI and importing it into FL Studio with proper instrument mapping" --model llama3.1:8b
```

**What to Verify:**

1. **Processing Time:** Should take 10-45 seconds (longer prompt = longer processing)

2. **Response Quality:**
   - Check if response has multiple steps
   - Look for technical details
   - Verify it mentions FL Studio
   - Ensure it's relevant to the prompt

3. **Structure:**
   - Should be well-formatted
   - May include numbered steps
   - Should mention specific actions

✅ **Pass Criteria:**
- Response is detailed (multiple paragraphs)
- Steps are logically ordered
- Technical terms are used correctly
- References audio-to-MIDI and FL Studio

---

## Test 6: Async Mode

### Test Asynchronous Workflow
```bash
../venv/bin/python -m workflow.cli start --prompt "What are the best practices for MIDI velocity mapping?" --model llama3.1:8b --async-mode
```

**Expected Behavior:**
- Same output format as sync mode
- Should process successfully
- Response should be relevant

✅ **Pass Criteria:**
- No "async" related errors
- Completes successfully
- Output is coherent

---

## Test 7: Run Full Test Suite

### Execute Automated Tests
```bash
cd /mnt/d/AI_Projects/ralph_app
./venv/bin/pytest tests/ -v
```

**What to Monitor:**

1. **Test Discovery:**
```
collecting ... collected 29 items
```

2. **Test Execution:**
```
tests/test_e2e_cli.py::test_cli_module_import PASSED                     [  3%]
tests/test_e2e_cli.py::test_cli_has_click PASSED                         [  6%]
...
```

3. **Final Results:**
```
======================= 29 passed, 6 warnings in X.XXs =======================
```

✅ **Pass Criteria:**
- All 29 tests pass
- No failures or errors
- Warnings are acceptable (deprecation warnings are OK)

❌ **If tests fail:**
- Note which test failed
- Read the error message
- Common issues:
  - Ollama not running (integration tests fail)
  - Import errors (check dependencies)
  - Async test fails (check pytest-asyncio installed)

---

## Test 8: Component Import Test

### Verify All Components Load
```bash
cd /mnt/d/AI_Projects/ralph_app
./venv/bin/python -c "
import sys
sys.path.insert(0, 'src')

print('Testing imports...')
from audio_to_midi.converter import AudioToMIDIConverter
print('✓ AudioToMIDIConverter')

from audio_to_midi.processor import AudioProcessor
print('✓ AudioProcessor')

from agent_framework.ollama_agent import OllamaAgent
print('✓ OllamaAgent')

from workflow.orchestrator import WorkflowOrchestrator
print('✓ WorkflowOrchestrator')

print('\nTesting instantiation...')
converter = AudioToMIDIConverter()
print('✓ AudioToMIDIConverter instance created')

processor = AudioProcessor()
print('✓ AudioProcessor instance created')

agent = OllamaAgent(model_name='llama3.1:8b')
print('✓ OllamaAgent instance created')

print('\n✓ All components working!')
"
```

**Expected Output:**
```
Testing imports...
✓ AudioToMIDIConverter
✓ AudioProcessor
✓ OllamaAgent
✓ WorkflowOrchestrator

Testing instantiation...
✓ AudioToMIDIConverter instance created
✓ AudioProcessor instance created
✓ OllamaAgent instance created

✓ All components working!
```

✅ **Pass Criteria:**
- All imports succeed
- All instantiations succeed
- No ImportError or AttributeError

---

## Test 9: Error Handling Test

### Test Invalid Model
```bash
cd src
../venv/bin/python -m workflow.cli test-ollama --model nonexistent-model
```

**Expected Behavior:**
- Should fail gracefully
- Error message should be informative
- Should suggest model installation

### Test Without Ollama Running

1. **Stop Ollama (if you want to test failure case):**
```bash
# In another terminal, stop Ollama
pkill ollama
```

2. **Try to run command:**
```bash
../venv/bin/python -m workflow.cli test-ollama --model llama3.1:8b
```

**Expected:** Error message indicating Ollama is not accessible

3. **Restart Ollama:**
```bash
ollama serve
```

✅ **Pass Criteria:**
- Errors are caught gracefully
- No Python tracebacks (just user-friendly messages)
- Clear instructions on how to fix

---

## Test 10: Performance Test

### Measure Response Time
```bash
cd src
time ../venv/bin/python -m workflow.cli start --prompt "List 3 benefits of MIDI" --model llama3.1:8b
```

**Typical Times:**
- Simple prompt: 5-15 seconds
- Medium prompt: 15-30 seconds
- Complex prompt: 30-60 seconds

✅ **Pass Criteria:**
- Response time is reasonable for your prompt
- No timeouts
- No hanging processes

---

## Common Issues & Troubleshooting

### Issue 1: "ModuleNotFoundError: No module named 'workflow'"

**Solution:**
```bash
cd /mnt/d/AI_Projects/ralph_app/src
# Run commands from src directory
../venv/bin/python -m workflow.cli [command]
```

### Issue 2: "Ollama connection failed"

**Solution:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# If not running, start it
ollama serve

# In another terminal, verify model
ollama list
```

### Issue 3: "LangChainDeprecationWarning"

**Status:** This is just a warning, not an error
**Impact:** None - functionality works perfectly
**Action:** Can be ignored safely

### Issue 4: Tests taking too long

**Cause:** Ollama model inference can be slow
**Solution:**
- Use faster model (e.g., `mistral` instead of `llama3.1:8b`)
- Ensure Ollama has GPU access if available
- Check system resources

---

## Success Checklist

Use this checklist to verify everything works:

- [ ] Python environment active
- [ ] Ollama running and accessible
- [ ] llama3.1:8b model available
- [ ] CLI help menu displays
- [ ] test-ollama command succeeds
- [ ] status command displays table
- [ ] Simple workflow task completes
- [ ] Complex workflow task completes
- [ ] Async mode works
- [ ] All 29 automated tests pass
- [ ] Components import successfully
- [ ] Error handling works gracefully
- [ ] Performance is acceptable

---

## Next Steps After Testing

If all tests pass, you can:

1. **Use the app for real workflows:**
   ```bash
   cd src
   ../venv/bin/python -m workflow.cli start --prompt "Your task" --model llama3.1:8b
   ```

2. **Convert audio files (when you have audio files):**
   ```bash
   ../venv/bin/python -m workflow.cli convert path/to/audio.mp3 --output-dir ../output/midi
   ```

3. **Integrate with FL Studio** (requires FL Studio running and MCP server setup)

4. **Customize prompts** for your specific music production needs

---

## Getting Help

If you encounter issues:

1. Check the error message carefully
2. Verify prerequisites (Ollama, Python, model)
3. Review the troubleshooting section
4. Check logs in `output/` directory
5. Re-run specific tests to isolate the issue

## Test Report Template

After testing, document your results:

```
MANUAL TEST REPORT
==================
Date: [DATE]
Tester: [YOUR NAME]
Environment: [Windows/Linux/Mac]

Test 1 - Installation: [PASS/FAIL]
Test 2 - Ollama Connection: [PASS/FAIL]
Test 3 - Status Check: [PASS/FAIL]
Test 4 - Simple Workflow: [PASS/FAIL]
Test 5 - Complex Workflow: [PASS/FAIL]
Test 6 - Async Mode: [PASS/FAIL]
Test 7 - Automated Tests: [PASS/FAIL]
Test 8 - Component Imports: [PASS/FAIL]
Test 9 - Error Handling: [PASS/FAIL]
Test 10 - Performance: [PASS/FAIL]

Overall Status: [ALL PASS / ISSUES FOUND]

Notes:
- [Any observations]
- [Issues encountered]
- [Performance notes]
```

---

**Good luck with your testing!** 🚀
