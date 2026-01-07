# Quick Test Commands Reference

Copy and paste these commands to quickly test the application.

## Setup
```bash
cd /mnt/d/AI_Projects/ralph_app/src
```

---

## 1. Check Ollama is Running
```bash
curl http://localhost:11434/api/version
```
✅ Should return: `{"version":"0.11.4"}`

---

## 2. Test Ollama Connection
```bash
../venv/bin/python -m workflow.cli test-ollama --model llama3.1:8b
```
✅ Should show: `✓ Ollama connection successful!`

---

## 3. Check Status
```bash
../venv/bin/python -m workflow.cli status
```
✅ Should show: Status table with "Idle"

---

## 4. Simple Test Task
```bash
../venv/bin/python -m workflow.cli start --prompt "Explain MIDI in one sentence" --model llama3.1:8b
```
✅ Should complete with AI response

---

## 5. Complex Test Task
```bash
../venv/bin/python -m workflow.cli start --prompt "Create a workflow for converting vocals to MIDI and importing into FL Studio" --model llama3.1:8b
```
✅ Should provide detailed step-by-step plan

---

## 6. Test Async Mode
```bash
../venv/bin/python -m workflow.cli start --prompt "What are MIDI velocity ranges?" --model llama3.1:8b --async-mode
```
✅ Should complete successfully

---

## 7. Run All Automated Tests
```bash
cd /mnt/d/AI_Projects/ralph_app
./venv/bin/pytest tests/ -v
```
✅ Should show: `29 passed`

---

## 8. Quick Component Test
```bash
cd /mnt/d/AI_Projects/ralph_app
./venv/bin/python -c "
import sys; sys.path.insert(0, 'src')
from audio_to_midi.converter import AudioToMIDIConverter
from agent_framework.ollama_agent import OllamaAgent
from workflow.orchestrator import WorkflowOrchestrator
print('✓ All components imported successfully')
"
```
✅ Should show: `✓ All components imported successfully`

---

## 9. View Help Menu
```bash
cd /mnt/d/AI_Projects/ralph_app/src
../venv/bin/python -m workflow.cli --help
```
✅ Should show: 5 commands (convert, start, status, stop, test-ollama)

---

## Quick Test Sequence (Run All)

```bash
# Navigate to project
cd /mnt/d/AI_Projects/ralph_app/src

# Test 1: Ollama connection
echo "=== Test 1: Ollama Connection ==="
../venv/bin/python -m workflow.cli test-ollama --model llama3.1:8b

# Test 2: Status check
echo -e "\n=== Test 2: Status ==="
../venv/bin/python -m workflow.cli status

# Test 3: Simple workflow
echo -e "\n=== Test 3: Simple Workflow ==="
../venv/bin/python -m workflow.cli start --prompt "What is MIDI?" --model llama3.1:8b

# Test 4: Run automated tests
echo -e "\n=== Test 4: Automated Tests ==="
cd /mnt/d/AI_Projects/ralph_app
./venv/bin/pytest tests/ -v --tb=short

echo -e "\n✓ All tests complete!"
```

---

## Expected Results Summary

| Test | Expected Output | Time |
|------|----------------|------|
| Ollama connection | `✓ Ollama connection successful!` | 1-3s |
| Status check | Status table showing "Idle" | <1s |
| Simple workflow | AI response (1-2 paragraphs) | 5-15s |
| Complex workflow | Detailed plan (multiple steps) | 15-45s |
| Async mode | Same as sync, completes successfully | 5-30s |
| Automated tests | `29 passed` | 20-30s |
| Component import | `✓ All components imported` | <1s |

---

## If Something Fails

### Ollama not accessible
```bash
# Start Ollama
ollama serve

# Check it's running
curl http://localhost:11434/api/version
```

### Model not found
```bash
# List models
ollama list

# Pull llama3.1 if missing
ollama pull llama3.1:8b
```

### Virtual environment issues
```bash
cd /mnt/d/AI_Projects/ralph_app
ls -la venv/  # Verify venv exists
./venv/bin/python --version  # Should be Python 3.12.x
```

### Import errors
```bash
# Always run from src directory
cd /mnt/d/AI_Projects/ralph_app/src
# Then use: ../venv/bin/python -m workflow.cli [command]
```

---

## Pass/Fail Criteria

✅ **ALL TESTS PASS:**
- Ollama connects successfully
- Status displays correctly
- Simple workflow completes with relevant response
- Complex workflow provides detailed plan
- Async mode works
- 29 automated tests pass
- Components import without errors

❌ **TESTS FAIL:**
- Error messages appear
- Timeouts occur
- Automated tests show failures
- Import errors
- No AI response generated

---

## Post-Testing

Once all tests pass, you can use the app for:

1. **AI-assisted music production planning**
2. **Audio to MIDI conversion workflows**
3. **FL Studio automation**
4. **Music production task orchestration**

Example real-world usage:
```bash
cd /mnt/d/AI_Projects/ralph_app/src
../venv/bin/python -m workflow.cli start \
  --prompt "Help me create a sampling workflow: I have a 30-second guitar loop and want to extract the melody as MIDI, map it to a synth in FL Studio, and add harmonies" \
  --model llama3.1:8b
```

The AI will provide detailed, actionable steps for your specific workflow!
