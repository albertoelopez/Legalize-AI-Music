# FL Studio Automation - Setup & Configuration Guide

## Quick Start

This guide covers setup for all FL Studio automation methods provided.

---

## 1. Environment Setup

### 1.1 Python Installation

Ensure Python 3.9+ is installed:

```bash
python --version
# Output: Python 3.9.x or higher
```

### 1.2 Virtual Environment

Create and activate a virtual environment:

```bash
# Create virtual environment
python -m venv fl_automation_env

# Activate (Windows)
fl_automation_env\Scripts\activate

# Activate (macOS/Linux)
source fl_automation_env/bin/activate
```

### 1.3 Install Dependencies

```bash
# Core dependencies
pip install pyautogui pillow keyboard psutil pygetwindow

# MCP Server
pip install mcp

# FL Studio API stubs (for development/intellisense)
pip install fl-studio-api-stubs

# Optional: for advanced automation
pip install opencv-python selenium
```

---

## 2. Method 1: FL Studio MIDI Scripting API

### 2.1 Setup FL Studio Python Scripts

**Location:** `C:\Users\[YourUsername]\AppData\Roaming\Image-Line\FL Studio\Settings\Hardware\`

**Steps:**

1. Create the Hardware folder if it doesn't exist
2. Copy `fl_studio_midi_controller.py` to this directory and rename to `device_automation.py`
3. Restart FL Studio
4. Check if script loaded in FL Studio menu: `Tools > MIDI > [Your device name]`

### 2.2 Script File Naming

Files must follow the naming convention:

```
device_[name].py    # Lowercase 'device_' prefix is required
```

Valid examples:
- `device_automation.py`
- `device_mycontroller.py`
- `device_generic.py`

### 2.3 Verify Installation

1. Open FL Studio
2. Go to `Tools > MIDI > My Devices > [Script Name]`
3. If script loaded, you'll see options or messages in the console

### 2.4 Debugging

Enable FL Studio's Python console:

```
Tools > MIDI > [Device] > Show Event Monitor
```

This shows:
- MIDI events received
- Script debug output
- Error messages

### 2.5 Example: Using the Script

The script responds to MIDI messages:

```
MIDI Note-On (60 = C3, velocity=any) → Start playback
MIDI Note-On (61 = C#3, velocity=any) → Stop playback
MIDI Control Change (CC 1) → Master volume
MIDI Control Change (CC 2) → Selected track volume
MIDI Control Change (CC 3) → Pan
```

Send MIDI from any controller:
- Hardware MIDI keyboard/controller
- DAW MIDI output
- Other MIDI software

---

## 3. Method 2: PyAutoGUI Automation

### 3.1 Installation

```bash
pip install pyautogui pillow pygetwindow
```

### 3.2 Basic Configuration

Edit `fl_studio_pyautogui_automation.py`:

```python
# Line 29
FL_EXE_PATH = r"C:\Program Files\Image-Line\FL Studio 21\FL.exe"

# Line 33
IMAGE_CONFIDENCE = 0.8  # 0.7 = lenient, 0.9 = strict
```

### 3.3 Running Simple Script

```bash
python fl_studio_pyautogui_automation.py
```

This will:
1. Launch FL Studio
2. Create a test project
3. Adjust mixer volumes
4. Take a screenshot

### 3.4 Creating Button Images

For image recognition, capture button screenshots:

```python
import pyautogui

# Take full screenshot
screenshot = pyautogui.screenshot()
screenshot.save("button.png")

# Or use:
pyautogui.locateCenterOnScreen('button.png')
```

### 3.5 Safe Development

Always keep failsafe enabled:

```python
pyautogui.FAILSAFE = True  # Move mouse to corner to stop
```

### 3.6 Troubleshooting

**Issue: "No module named 'PIL'"**
```bash
pip install pillow
```

**Issue: "FL Studio window not found"**
```python
import pygetwindow as gw
# Check available windows
print(gw.getAllWindows())
```

**Issue: Image recognition not working**
- Increase timeout: `automation.find_image(image_path, timeout=10)`
- Decrease confidence: `automation.find_image(image_path, confidence=0.7)`
- Take fresh screenshot of button

---

## 4. Method 3: MCP Server

### 4.1 Installation

```bash
pip install mcp pyautogui pillow psutil
```

### 4.2 Running the Server

Start the server:

```bash
python fl_studio_mcp_server.py
```

Expected output:

```
============================================================
FL Studio MCP Server Started
============================================================

Available Tools:
  - launch_fl_studio
  - close_fl_studio
  - focus_window
  - click_position
  - drag_position
  - press_key
  - hotkey
  - type_text
  - take_screenshot
  - create_project
  - save_project
  - adjust_mixer_volume
  - start_playback
  - stop_playback
  - undo_action
  - redo_action

Server ready for connections...
============================================================
```

### 4.3 Configure Claude Code Integration

Create/edit `.claude/claude.json` or config:

```json
{
  "mcpServers": {
    "fl-studio": {
      "command": "python",
      "args": ["/absolute/path/to/fl_studio_mcp_server.py"]
    }
  }
}
```

### 4.4 Using with Claude Code

Once configured, Claude can use the tools:

```
Human: "Create a new FL Studio project called 'Electronic Dance'"

Claude will:
1. Call launch_fl_studio tool
2. Call create_project tool with project_name="Electronic Dance"
3. Report success
```

### 4.5 Troubleshooting

**Issue: "No module named 'mcp'"**
```bash
pip install mcp
```

**Issue: Server won't start**
- Check Python path: `which python`
- Verify MCP installation: `pip show mcp`
- Check logs: `python fl_studio_mcp_server.py 2>&1 | tee server.log`

---

## 5. Advanced Configuration

### 5.1 Custom MIDI Mapping

Edit `fl_studio_midi_controller.py`:

```python
# Custom CC mappings
MIDI_CC_CUSTOM = {
    10: "pan",          # Standard MIDI pan
    7:  "volume",       # Standard MIDI volume
    11: "expression",   # Expression pedal
    64: "sustain",      # Sustain pedal
}
```

### 5.2 Automation Delays & Timing

Adjust pause between actions:

```python
# PyAutoGUI
automation.pauses_between_actions = 0.3  # 300ms delay

# Direct PyAutoGUI
pyautogui.PAUSE = 0.1  # 100ms global pause
```

### 5.3 Error Handling & Logging

Enable debug logging:

```bash
# Run with debug output
python fl_studio_pyautogui_automation.py --debug

# Check log file
cat fl_studio_automation.log
```

Configure logging level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 5.4 Performance Optimization

For faster automation:

```python
# Lower image recognition confidence (faster, less reliable)
IMAGE_CONFIDENCE = 0.7

# Reduce pause between actions (faster, more fragile)
pyautogui.PAUSE = 0.05

# Use shorter timeouts
automation.find_image(path, timeout=5)
```

---

## 6. Best Practices

### 6.1 Reliability Checklist

- [ ] Always use explicit waits, not fixed delays
- [ ] Implement retry logic for flaky operations
- [ ] Log all actions to file
- [ ] Take screenshots on errors
- [ ] Test with screen at 100% zoom
- [ ] Use window focus verification
- [ ] Handle exceptions gracefully

### 6.2 Testing Workflow

```bash
# 1. Test individual functions
python -c "from fl_studio_pyautogui_automation import *; automation = FLStudioWorkflows(); automation.launch()"

# 2. Test with verbose logging
python fl_studio_pyautogui_automation.py 2>&1 | tee test.log

# 3. Verify with screenshots
python -c "from fl_studio_pyautogui_automation import *; automation = FLStudioWorkflows(); automation.take_screenshot()"
```

### 6.3 Monitor Resource Usage

```bash
# Check Python memory usage
import psutil
process = psutil.Process()
print(process.memory_info())

# Monitor FL Studio process
for proc in psutil.process_iter(['name', 'memory_percent']):
    if 'FL.exe' in proc.name():
        print(f"FL Studio: {proc.memory_percent():.1f}% RAM")
```

---

## 7. Troubleshooting Common Issues

### Issue: "Module not found" errors

**Solution:**
```bash
# Verify installation
pip list | grep pyautogui
pip list | grep mcp

# Reinstall if needed
pip install --upgrade --force-reinstall pyautogui mcp
```

### Issue: Automation runs too fast/slow

**Solution:**
```python
# Increase delays
pyautogui.PAUSE = 0.3  # 300ms pause

# Or per-action:
time.sleep(1)  # 1 second wait
```

### Issue: Mouse clicks not registering

**Solution:**
```python
# Ensure window is focused
automation.focus_window()
time.sleep(0.5)

# Verify coordinates are correct
print(pyautogui.position())  # Print current position

# Add click verification
pyautogui.click(x, y)
time.sleep(0.3)  # Wait for click to register
```

### Issue: FL Studio not launching

**Solution:**
```python
# Verify path exists
from pathlib import Path
fl_path = r"C:\Program Files\Image-Line\FL Studio 21\FL.exe"
assert Path(fl_path).exists(), f"FL Studio not found at {fl_path}"

# Check for process
import psutil
for proc in psutil.process_iter(['name']):
    print(proc.name())
```

### Issue: Image recognition failing

**Solution:**
```python
# Take fresh screenshot
automation.take_screenshot()

# Try with lower confidence
location = pyautogui.locateOnScreen('button.png', confidence=0.7)

# Check image size matches screen area
from PIL import Image
img = Image.open('button.png')
print(f"Image size: {img.size}")

# Verify button is visible
automation.take_screenshot('debug.png')
```

---

## 8. Uninstallation

To remove all automation files:

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf fl_automation_env

# Remove MIDI script
del "C:\Users\[YourUsername]\AppData\Roaming\Image-Line\FL Studio\Settings\Hardware\device_automation.py"

# Remove automation scripts
rm fl_studio_*.py
```

---

## 9. Support & Resources

### Documentation Links
- [FL Studio Manual - MIDI Scripting](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/midi_scripting.htm)
- [FL Studio API Documentation](https://il-group.github.io/FL-Studio-API-Stubs/)
- [PyAutoGUI Documentation](https://pyautogui.readthedocs.io/)
- [MCP Protocol Documentation](https://modelcontextprotocol.github.io/python-sdk/)

### Debugging Tools
- FL Studio Python Console: `Tools > MIDI > [Device] > Show Event Monitor`
- PyAutoGUI Debug: `pyautogui.position()` to check coordinates
- Log Files: Check `fl_studio_automation.log` for detailed logs

### Example Projects

See included files:
- `fl_studio_midi_controller.py` - MIDI controller script
- `fl_studio_pyautogui_automation.py` - UI automation
- `fl_studio_mcp_server.py` - MCP server for AI integration

---

## 10. Next Steps

1. **Choose your method:**
   - MIDI scripting: Direct, reliable, event-based
   - PyAutoGUI: Quick, flexible, visual
   - MCP Server: AI-integrated, orchestration

2. **Test with examples:**
   - Run provided example scripts
   - Verify tools work correctly
   - Check logs for issues

3. **Customize for your needs:**
   - Modify MIDI mappings
   - Create project templates
   - Build complex workflows

4. **Integrate with your workflow:**
   - Use MCP with Claude Code
   - Automate repetitive tasks
   - Build production tools

---

## Quick Command Reference

```bash
# Virtual environment
python -m venv fl_automation_env
fl_automation_env\Scripts\activate
deactivate

# Installation
pip install pyautogui pillow psutil mcp

# Running scripts
python fl_studio_pyautogui_automation.py
python fl_studio_mcp_server.py

# Testing
python -c "import pyautogui; print(pyautogui.position())"
python -c "import mcp; print('MCP installed')"

# Logging
tail -f fl_studio_automation.log
python script.py 2>&1 | tee output.log
```

---

## Success Checklist

- [ ] Python 3.9+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed: `pip list` shows required packages
- [ ] MIDI script installed in correct location
- [ ] PyAutoGUI can find FL Studio: `pyautogui.locateOnScreen()`
- [ ] MCP server starts without errors
- [ ] Example scripts run successfully
- [ ] Logs are being generated
- [ ] Screenshots captured correctly
- [ ] FL Studio responds to automation commands

Once all items are checked, you're ready to automate FL Studio!
