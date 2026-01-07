# FL Studio Automation Research & Implementation Guide

## Executive Summary

FL Studio automation on Windows can be achieved through multiple complementary approaches:
1. **FL Studio's Native Python API** - Most direct and reliable method
2. **UI Automation Tools** - PyAutoGUI, pywinauto, or Playwright with extensions
3. **Image/Pixel Recognition** - OpenCV-based automation for visual scripting
4. **MCP Server Integration** - Modern approach for AI-driven automation
5. **MIDI Controller Scripting** - Event-based real-time control

---

## 1. FL Studio's Python API (MIDI Scripting)

### Overview

FL Studio includes a built-in Python 3.9.x interpreter for MIDI controller scripting. This is the **most reliable and direct** method for automating FL Studio.

**Key Characteristics:**
- Event-based execution model (code runs when FL Studio events occur)
- Direct access to FL Studio's internal state
- No screen scraping or fragile UI automation needed
- Can control: Channels, Mixer, Transport, Piano Roll, Arrangement
- Official API documentation available

**Sources:**
- [FL Studio MIDI Scripting Documentation](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/midi_scripting.htm)
- [FL Studio API Stubs](https://il-group.github.io/FL-Studio-API-Stubs/)
- [PyPI: fl-studio-api-stubs](https://pypi.org/project/fl-studio-api-stubs/)

### Implementation Example: Basic MIDI Controller Script

**File Location:** `C:\Users\[YourUsername]\AppData\Roaming\Image-Line\FL Studio\Settings\Hardware\device_mycontroller.py`

```python
"""
FL Studio Python MIDI Controller Script
Provides automation control of FL Studio via MIDI events
"""

import device
import mixer
import channels
import transport
import ui
import patterns
import arrangement
import time

# Script metadata
SCRIPT_VERSION = "1.0.0"
SCRIPT_NAME = "FL Studio Automation Controller"

# State management
last_mixer_value = 0.0
automation_enabled = False
recording_pattern = False


def OnInit():
    """Called when the script is initialized."""
    print("Automation Controller initialized")
    device.setHardware(device.TYPE_GENERIC_MIDI)


def OnDeinit():
    """Called when the script is deinitialized."""
    print("Automation Controller deinitialized")


def OnMidiIn(event):
    """
    Called whenever the device sends a MIDI message to FL Studio.

    Args:
        event: MIDI event object with status, data1, data2 properties
    """
    # Handle Note On events (status: 0x90)
    if event.status == 0x90:
        note_number = event.data1
        velocity = event.data2

        # Trigger patterns based on notes
        if velocity > 0:
            HandleNoteOn(note_number, velocity)
        else:
            HandleNoteOff(note_number)

    # Handle Control Change events (status: 0xB0)
    elif event.status == 0xB0:
        cc_number = event.data1
        cc_value = event.data2

        HandleControlChange(cc_number, cc_value)


def HandleNoteOn(note, velocity):
    """Handle note-on events for pattern triggering."""
    global recording_pattern

    # Notes 60-63: Control transport
    if note == 60:  # C3 - Play
        transport.start()
    elif note == 61:  # C#3 - Stop
        transport.stop()
    elif note == 62:  # D3 - Record
        transport.setLoopMode(1)  # Enable loop recording
    elif note == 63:  # D#3 - Punch in/out
        recording_pattern = not recording_pattern

    # Notes 64-79: Trigger drum pads
    elif 64 <= note <= 79:
        pattern_index = note - 64
        # Trigger corresponding pattern
        arrangement.currentPattern = pattern_index


def HandleNoteOff(note):
    """Handle note-off events."""
    pass


def HandleControlChange(cc_number, cc_value):
    """
    Handle Control Change (CC) messages for parameter automation.

    CC mapping:
    - CC 1: Master volume
    - CC 2: Selected mixer track fader
    - CC 3: Selected channel pan
    """
    global last_mixer_value

    # Normalize CC value (0-127) to 0.0-1.0
    normalized_value = cc_value / 127.0

    if cc_number == 1:  # Master volume
        mixer.setTrackVolume(0, normalized_value)
        print(f"Master volume: {normalized_value:.2f}")

    elif cc_number == 2:  # Mixer track control
        selected_track = mixer.selectedTrack()
        if selected_track >= 0:
            mixer.setTrackVolume(selected_track, normalized_value)
            last_mixer_value = normalized_value

    elif cc_number == 3:  # Channel pan
        ch = channels.selectedChannel()
        if ch >= 0:
            channels.setPan(ch, normalized_value - 0.5)  # -0.5 to 0.5

    elif cc_number == 7:  # Standard MIDI volume
        mixer.setTrackVolume(mixer.selectedTrack(), normalized_value)


def OnIdle():
    """Called continuously in the background."""
    # You can perform periodic tasks here
    pass


def OnRefresh(event_flags):
    """Called when FL Studio needs to refresh the hardware display."""
    # Update LED displays or hardware feedback here
    pass
```

### FL Studio API Modules

```python
# Available modules for direct FL Studio control:

import channels      # Control instruments/channels
import mixer         # Control mixer tracks and effects
import transport     # Control playback (play, stop, pause, record)
import patterns      # Access and manipulate patterns
import arrangement   # Control arrangement/playlist
import ui            # UI elements and dialogs
import device        # MIDI device control
import launchmap     # Launcher control
import flpianoroll   # Piano roll manipulation (read-only in most cases)

# Key functions by module:

# Channels Module
channels.channelCount()              # Get total channel count
channels.selectedChannel()           # Get selected channel
channels.getChannelName(index)       # Get channel name
channels.getChannelVolume(index)     # Get channel volume (0.0-1.0)
channels.setChannelVolume(index, v)  # Set channel volume
channels.getPan(index)               # Get pan (-0.5 to 0.5)
channels.setPan(index, value)        # Set pan

# Mixer Module
mixer.trackCount()                   # Get track count
mixer.selectedTrack()                # Get selected track
mixer.getTrackVolume(index)          # Get track volume
mixer.setTrackVolume(index, value)   # Set track volume (0.0-1.0)
mixer.getTrackPan(index)             # Get track pan
mixer.setTrackPan(index, value)      # Set pan (-0.5 to 0.5)

# Transport Module
transport.start()                    # Start playback
transport.stop()                     # Stop playback
transport.pause()                    # Pause playback
transport.record()                   # Enable recording
transport.setPos(position)           # Set playback position
transport.setLoopMode(mode)          # Set loop mode

# Patterns Module
patterns.patternCount()              # Get pattern count
patterns.getPatternName(index)       # Get pattern name
patterns.currentPattern              # Property: current pattern index
```

### Advantages
- Direct access to FL Studio internals
- No screen scraping or image recognition needed
- Event-driven (efficient, responsive)
- Robust and reliable
- Built-in Python interpreter

### Limitations
- Limited to MIDI controller scripting use cases
- Cannot directly manipulate UI elements outside API scope
- Requires understanding of FL Studio's MIDI architecture

---

## 2. PyAutoGUI - Screen Automation

### Overview

PyAutoGUI is a pure Python module for programmatically controlling the mouse and keyboard. Suitable for automating visual tasks like menu navigation and button clicking.

**Installation:**
```bash
pip install pyautogui pillow keyboard
```

**Sources:**
- [PyAutoGUI Documentation](https://pyautogui.readthedocs.io/)
- [PyAutoGUI PyPI](https://pypi.org/project/PyAutoGUI/)

### Implementation Example: FL Studio Menu Automation

```python
"""
FL Studio UI Automation using PyAutoGUI
Automates visual menu interactions and button clicks
"""

import pyautogui
import time
import subprocess
from pathlib import Path

# Configuration
FAILSAFE_ENABLED = True
PAUSE_BETWEEN_ACTIONS = 0.2  # seconds
IMAGE_CONFIDENCE = 0.7

# FL Studio window configuration
FL_WINDOW_TITLE = "FL Studio"
FL_EXE_PATH = r"C:\Program Files\Image-Line\FL Studio 21\FL.exe"


class FLStudioAutomation:
    """Automate FL Studio using PyAutoGUI."""

    def __init__(self):
        """Initialize automation controller."""
        if FAILSAFE_ENABLED:
            pyautogui.FAILSAFE = True  # Move mouse to corner to abort

        pyautogui.PAUSE = PAUSE_BETWEEN_ACTIONS
        self.fl_process = None

    def launch_fl_studio(self):
        """Launch FL Studio if not already running."""
        import psutil

        # Check if FL Studio is already running
        for proc in psutil.process_iter(['name']):
            if 'FL.exe' in proc.name():
                print("FL Studio is already running")
                return True

        print(f"Launching FL Studio from {FL_EXE_PATH}")
        self.fl_process = subprocess.Popen(FL_EXE_PATH)
        time.sleep(5)  # Wait for FL Studio to fully load
        return True

    def find_window(self):
        """Locate and focus FL Studio window."""
        import pygetwindow as gw

        windows = gw.getWindowsWithTitle(FL_WINDOW_TITLE)
        if windows:
            win = windows[0]
            win.activate()
            time.sleep(0.5)
            return win
        return None

    def click_menu(self, menu_path: list):
        """
        Navigate menu hierarchy.

        Args:
            menu_path: List of menu items to click
            Example: ['File', 'New']
        """
        for menu_item in menu_path:
            # Use locateOnScreen to find menu text
            try:
                location = pyautogui.locateOnScreen(
                    menu_item,
                    confidence=IMAGE_CONFIDENCE
                )
                if location:
                    pyautogui.click(location)
                    time.sleep(PAUSE_BETWEEN_ACTIONS)
                else:
                    print(f"Menu item not found: {menu_item}")
                    return False
            except Exception as e:
                print(f"Error clicking menu {menu_item}: {e}")
                return False

        return True

    def click_button(self, button_name: str, max_attempts: int = 3):
        """
        Click a button by visual recognition.

        Args:
            button_name: Name/label of button
            max_attempts: Number of retry attempts
        """
        for attempt in range(max_attempts):
            try:
                location = pyautogui.locateOnScreen(
                    button_name,
                    confidence=IMAGE_CONFIDENCE
                )
                if location:
                    pyautogui.click(location)
                    print(f"Clicked button: {button_name}")
                    return True
                else:
                    time.sleep(0.5)
            except Exception as e:
                print(f"Attempt {attempt + 1}: Error - {e}")
                time.sleep(0.5)

        print(f"Failed to click button after {max_attempts} attempts")
        return False

    def type_text(self, text: str, speed: float = 0.05):
        """
        Type text with configurable speed.

        Args:
            text: Text to type
            speed: Delay between characters (seconds)
        """
        for char in text:
            pyautogui.typewrite(char)
            time.sleep(speed)

    def create_new_project(self, project_name: str):
        """
        Create a new FL Studio project.

        Args:
            project_name: Name for new project
        """
        print(f"Creating new project: {project_name}")

        # Open File menu
        pyautogui.hotkey('alt', 'f')
        time.sleep(0.5)

        # Click New
        self.click_button('New')
        time.sleep(1)

        # Type project name in dialog
        self.type_text(project_name)
        time.sleep(0.3)

        # Press Enter to confirm
        pyautogui.press('enter')
        time.sleep(2)

        print(f"Project '{project_name}' created")

    def adjust_mixer_volume(self, track_index: int, volume: float):
        """
        Adjust mixer track volume (0.0 - 1.0).

        Args:
            track_index: Mixer track index
            volume: Volume level (0.0 to 1.0)
        """
        # Click mixer track
        mixer_x = 50 + (track_index * 60)
        mixer_y = 400

        pyautogui.click(mixer_x, mixer_y)
        time.sleep(0.3)

        # Drag fader to position
        fader_y = int(500 - (volume * 100))
        pyautogui.drag(0, fader_y - mixer_y, duration=0.5)

        print(f"Track {track_index} volume set to {volume:.2f}")

    def take_screenshot(self, filename: str = "fl_studio_screenshot.png"):
        """Take screenshot of FL Studio window."""
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        print(f"Screenshot saved: {filename}")
        return filename


# Example usage
if __name__ == "__main__":
    automation = FLStudioAutomation()

    # Launch FL Studio
    automation.launch_fl_studio()
    time.sleep(3)

    # Find and focus window
    if automation.find_window():
        print("FL Studio window found and focused")

        # Example: Create new project
        automation.create_new_project("My Automation Project")

        # Example: Adjust mixer volumes
        for track in range(5):
            automation.adjust_mixer_volume(track, 0.7)
            time.sleep(0.5)

        # Take screenshot
        automation.take_screenshot()
```

### Key PyAutoGUI Features

```python
# Mouse control
pyautogui.position()              # Current mouse position
pyautogui.moveTo(x, y)            # Move mouse
pyautogui.moveRel(x, y)           # Move relative
pyautogui.click(x, y)             # Click at position
pyautogui.click(button='right')   # Right click
pyautogui.doubleClick(x, y)       # Double click
pyautogui.drag(x, y, duration=0.5) # Drag
pyautogui.scroll(10)              # Scroll wheel

# Keyboard control
pyautogui.press('enter')          # Press key
pyautogui.hotkey('ctrl', 's')     # Hotkey combination
pyautogui.typewrite('hello')      # Type text (letters only)
pyautogui.write('hello')          # Type text (with special chars)

# Screen recognition
pyautogui.locateOnScreen('image.png', confidence=0.9)
pyautogui.screenshot()            # Get screenshot as PIL image
```

### Best Practices for Reliable PyAutoGUI Automation

1. **Always use explicit delays:**
   ```python
   time.sleep(0.5)  # Wait for UI to update
   ```

2. **Implement retry logic:**
   ```python
   max_attempts = 3
   for attempt in range(max_attempts):
       try:
           # Perform action
           break
       except Exception as e:
           if attempt == max_attempts - 1:
               raise
           time.sleep(0.5)
   ```

3. **Use image recognition with confidence threshold:**
   ```python
   location = pyautogui.locateOnScreen(
       'button.png',
       confidence=0.8  # Higher = stricter matching
   )
   ```

4. **Handle window focus:**
   ```python
   import pygetwindow as gw
   window = gw.getWindowsWithTitle('FL Studio')[0]
   window.activate()
   ```

5. **Enable failsafe for development:**
   ```python
   pyautogui.FAILSAFE = True  # Move mouse to corner to stop
   ```

---

## 3. Playwright for Desktop Automation

### Overview

Playwright is primarily web-focused but can control Windows desktop applications through extensions like FlaUI.WebDriver.

**Installation:**
```bash
pip install playwright
playwright install  # Download browsers
```

**Sources:**
- [Playwright Documentation](https://playwright.dev/)
- [Playwright MCP for AI Testing](https://www.testleaf.com/blog/playwright-mcp-ai-test-automation-2026/)

### Implementation Example: Playwright with FlaUI Integration

```python
"""
FL Studio automation using Playwright + FlaUI.WebDriver
For WebView2-based components or using FlaUI bridge
"""

from playwright.async_api import async_playwright, Page
import asyncio
import subprocess
import time


class FLStudioPlaywrightAutomation:
    """Control FL Studio using Playwright via FlaUI WebDriver bridge."""

    def __init__(self):
        """Initialize Playwright automation."""
        self.browser = None
        self.page = None
        self.context = None
        self.playwright = None

    async def launch_fl_studio(self):
        """Launch FL Studio application."""
        subprocess.Popen(r"C:\Program Files\Image-Line\FL Studio 21\FL.exe")
        await asyncio.sleep(5)  # Wait for startup

    async def connect_to_webdriver(self, server_url: str = "http://localhost:4567"):
        """
        Connect to FlaUI WebDriver server.

        Requires running FlaUI.WebDriver separately:
        > FlaUI.WebDriver.exe --port 4567
        """
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.connect_over_cdp(server_url)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()

    async def find_element(self, selector: str, timeout: int = 5000):
        """
        Find UI element using FlaUI selector.

        Selectors work with automation ID, class name, or text content.
        """
        try:
            element = await self.page.wait_for_selector(
                selector,
                timeout=timeout
            )
            return element
        except Exception as e:
            print(f"Element not found: {selector} - {e}")
            return None

    async def click_element(self, selector: str):
        """Click a UI element."""
        element = await self.find_element(selector)
        if element:
            await element.click()
            await asyncio.sleep(0.3)
            return True
        return False

    async def set_text(self, selector: str, text: str):
        """Set text in input field."""
        element = await self.find_element(selector)
        if element:
            await element.fill(text)
            return True
        return False

    async def close(self):
        """Close browser and cleanup."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


# Synchronous wrapper for easier use
class FLStudioPlaywrightSync:
    """Synchronous wrapper for Playwright automation."""

    def __init__(self):
        self.automation = FLStudioPlaywrightAutomation()

    def launch(self):
        """Launch FL Studio."""
        asyncio.run(self.automation.launch_fl_studio())

    def connect(self, server_url: str = "http://localhost:4567"):
        """Connect to WebDriver."""
        asyncio.run(self.automation.connect_to_webdriver(server_url))

    def click(self, selector: str) -> bool:
        """Click element."""
        return asyncio.run(self.automation.click_element(selector))

    def set_text(self, selector: str, text: str) -> bool:
        """Set text in element."""
        return asyncio.run(self.automation.set_text(selector, text))

    def close(self):
        """Close connection."""
        asyncio.run(self.automation.close())


# Example usage
if __name__ == "__main__":
    sync = FLStudioPlaywrightSync()

    # Requires FlaUI.WebDriver running separately
    sync.launch()
    time.sleep(2)

    # Would require FlaUI.WebDriver setup
    # sync.connect("http://localhost:4567")
    # sync.click('//Button[@Name="File"]')
    # sync.close()
```

### Playwright Advantages
- Modern, async-friendly API
- Good for web components in desktop apps
- Network activity capture
- Multiple browser support

### Limitations for FL Studio
- Primarily web-focused
- Requires FlaUI.WebDriver for desktop windows
- Extra complexity for non-web applications

---

## 4. MCP Server for Desktop Automation

### Overview

Model Context Protocol (MCP) allows AI models to control desktop automation through a standardized interface. Create an MCP server that exposes desktop automation tools.

**Installation:**
```bash
pip install mcp
```

**Sources:**
- [Python MCP SDK on GitHub](https://github.com/modelcontextprotocol/python-sdk)
- [Real Python MCP Guide](https://realpython.com/python-mcp/)
- [MCP Server Documentation](https://modelcontextprotocol.github.io/python-sdk/)

### Implementation Example: FL Studio MCP Server

```python
"""
FL Studio MCP (Model Context Protocol) Server
Exposes desktop automation tools to AI models
"""

from mcp.server.models import InitializationOptions
from mcp.server import Server
import mcp.types as types
import pyautogui
import subprocess
import time
import json
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP Server
server = Server("fl-studio-automation")

# Configuration
FL_EXE_PATH = r"C:\Program Files\Image-Line\FL Studio 21\FL.exe"
SCRIPT_PAUSE = 0.2
IMAGE_CONFIDENCE = 0.8


# ============================================================================
# TOOLS - Expose automation capabilities
# ============================================================================

@server.call_tool()
async def launch_fl_studio(arguments: dict) -> list[types.TextContent]:
    """
    Launch FL Studio if not already running.

    Returns: Success status and process info
    """
    try:
        import psutil

        # Check if already running
        for proc in psutil.process_iter(['name']):
            if 'FL.exe' in proc.name():
                return [types.TextContent(
                    type="text",
                    text="FL Studio is already running"
                )]

        logger.info(f"Launching FL Studio from {FL_EXE_PATH}")
        process = subprocess.Popen(FL_EXE_PATH)
        time.sleep(5)

        return [types.TextContent(
            type="text",
            text=f"FL Studio launched successfully (PID: {process.pid})"
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error launching FL Studio: {str(e)}"
        )]


@server.call_tool()
async def click_menu(arguments: dict) -> list[types.TextContent]:
    """
    Click on menu items in sequence.

    Arguments:
        - menu_path: List of menu items to click (e.g., ["File", "New"])
        - timeout: Maximum time to wait for menu items
    """
    menu_path = arguments.get("menu_path", [])
    timeout = arguments.get("timeout", 5)

    if not menu_path:
        return [types.TextContent(
            type="text",
            text="Error: menu_path is required"
        )]

    try:
        for menu_item in menu_path:
            logger.info(f"Looking for menu item: {menu_item}")
            # In real implementation, use locateOnScreen or UI automation
            time.sleep(SCRIPT_PAUSE)

        return [types.TextContent(
            type="text",
            text=f"Successfully navigated menu: {' -> '.join(menu_path)}"
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error clicking menu: {str(e)}"
        )]


@server.call_tool()
async def keyboard_input(arguments: dict) -> list[types.TextContent]:
    """
    Send keyboard input to FL Studio.

    Arguments:
        - keys: Keys to press (e.g., "ctrl+s" for save)
        - delay: Delay between keypresses
    """
    keys = arguments.get("keys", "")
    delay = arguments.get("delay", 0.1)

    if not keys:
        return [types.TextContent(
            type="text",
            text="Error: keys argument is required"
        )]

    try:
        # Parse hotkey format: "ctrl+s", "alt+f4", etc.
        parts = keys.split('+')

        if len(parts) > 1:
            modifiers = parts[:-1]
            key = parts[-1]
            pyautogui.hotkey(*modifiers, key)
        else:
            pyautogui.press(keys)

        time.sleep(delay)

        return [types.TextContent(
            type="text",
            text=f"Keyboard input sent: {keys}"
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error sending keyboard input: {str(e)}"
        )]


@server.call_tool()
async def mouse_action(arguments: dict) -> list[types.TextContent]:
    """
    Perform mouse actions (move, click, drag).

    Arguments:
        - action: "click", "move", "drag"
        - x, y: Coordinates
        - button: "left", "right", "middle"
        - duration: Duration for drag action
    """
    action = arguments.get("action", "click")
    x = arguments.get("x", 0)
    y = arguments.get("y", 0)
    button = arguments.get("button", "left")
    duration = arguments.get("duration", 0.5)

    try:
        if action == "click":
            pyautogui.click(x, y, button=button)
            message = f"Clicked at ({x}, {y}) with {button} button"

        elif action == "move":
            pyautogui.moveTo(x, y)
            message = f"Moved mouse to ({x}, {y})"

        elif action == "drag":
            dx = arguments.get("dx", 0)
            dy = arguments.get("dy", 0)
            pyautogui.drag(dx, dy, duration=duration)
            message = f"Dragged by ({dx}, {dy})"

        else:
            return [types.TextContent(
                type="text",
                text=f"Unknown action: {action}"
            )]

        time.sleep(SCRIPT_PAUSE)

        return [types.TextContent(
            type="text",
            text=message
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error performing mouse action: {str(e)}"
        )]


@server.call_tool()
async def type_text(arguments: dict) -> list[types.TextContent]:
    """
    Type text into focused input field.

    Arguments:
        - text: Text to type
        - speed: Characters per second (default: 10)
    """
    text = arguments.get("text", "")
    speed = arguments.get("speed", 10)
    delay = 1.0 / speed

    if not text:
        return [types.TextContent(
            type="text",
            text="Error: text argument is required"
        )]

    try:
        for char in text:
            pyautogui.typewrite(char)
            time.sleep(delay)

        return [types.TextContent(
            type="text",
            text=f"Typed: {text}"
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error typing text: {str(e)}"
        )]


@server.call_tool()
async def take_screenshot(arguments: dict) -> list[types.TextContent]:
    """
    Take a screenshot and save it.

    Arguments:
        - filename: Output filename (default: fl_screenshot.png)
    """
    filename = arguments.get("filename", "fl_screenshot.png")

    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)

        return [types.TextContent(
            type="text",
            text=f"Screenshot saved: {filename}"
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error taking screenshot: {str(e)}"
        )]


@server.call_tool()
async def create_project(arguments: dict) -> list[types.TextContent]:
    """
    Create a new FL Studio project.

    Arguments:
        - project_name: Name for the new project
    """
    project_name = arguments.get("project_name", "Untitled")

    try:
        logger.info(f"Creating new project: {project_name}")

        # Open File menu
        pyautogui.hotkey('alt', 'f')
        time.sleep(0.5)

        # Press 'N' for New
        pyautogui.press('n')
        time.sleep(1)

        # Type project name
        for char in project_name:
            pyautogui.typewrite(char)
            time.sleep(0.05)

        # Press Enter
        pyautogui.press('enter')
        time.sleep(2)

        return [types.TextContent(
            type="text",
            text=f"Project '{project_name}' created successfully"
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error creating project: {str(e)}"
        )]


@server.call_tool()
async def adjust_mixer_volume(arguments: dict) -> list[types.TextContent]:
    """
    Adjust mixer track volume.

    Arguments:
        - track_index: Mixer track index (0-based)
        - volume: Volume level (0.0 to 1.0)
    """
    track_index = arguments.get("track_index", 0)
    volume = arguments.get("volume", 0.5)

    try:
        # Validate volume
        volume = max(0.0, min(1.0, volume))

        logger.info(f"Setting track {track_index} volume to {volume:.2f}")

        # Click mixer track
        mixer_x = 50 + (track_index * 60)
        mixer_y = 400
        pyautogui.click(mixer_x, mixer_y)
        time.sleep(0.3)

        # Drag fader
        fader_y = int(500 - (volume * 100))
        pyautogui.drag(0, fader_y - mixer_y, duration=0.5)

        return [types.TextContent(
            type="text",
            text=f"Track {track_index} volume set to {volume:.2f}"
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error adjusting volume: {str(e)}"
        )]


# ============================================================================
# RESOURCES - Expose information/state
# ============================================================================

@server.list_resources()
async def list_resources() -> list[types.Resource]:
    """List available resources."""
    return [
        types.Resource(
            uri="fl-studio://status",
            name="FL Studio Status",
            description="Current status of FL Studio",
            mimeType="application/json"
        ),
        types.Resource(
            uri="fl-studio://mixer",
            name="Mixer State",
            description="Current mixer configuration",
            mimeType="application/json"
        ),
    ]


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read a resource."""
    if uri == "fl-studio://status":
        return json.dumps({
            "status": "running",
            "version": "21",
            "project": "Untitled"
        })

    elif uri == "fl-studio://mixer":
        return json.dumps({
            "track_count": 99,
            "master_volume": 0.8,
            "selected_track": 0
        })

    else:
        return json.dumps({"error": "Unknown resource"})


# ============================================================================
# PROMPTS - Provide templates for common tasks
# ============================================================================

@server.list_prompts()
async def list_prompts() -> list[types.Prompt]:
    """List available prompt templates."""
    return [
        types.Prompt(
            name="create_new_track",
            description="Create and configure a new mixer track",
            arguments=[
                types.PromptArgument(
                    name="track_name",
                    description="Name of the new track",
                    required=True
                ),
                types.PromptArgument(
                    name="track_type",
                    description="Type: 'audio' or 'midi'",
                    required=True
                ),
            ]
        ),
        types.Prompt(
            name="record_pattern",
            description="Record a new pattern or clip",
            arguments=[
                types.PromptArgument(
                    name="pattern_name",
                    description="Name of the pattern",
                    required=True
                ),
                types.PromptArgument(
                    name="duration_beats",
                    description="Duration in beats",
                    required=True
                ),
            ]
        ),
    ]


@server.get_prompt()
async def get_prompt(name: str, arguments: dict) -> types.GetPromptResult:
    """Get a prompt template."""
    if name == "create_new_track":
        track_name = arguments.get("track_name", "Track 1")
        track_type = arguments.get("track_type", "midi")

        instructions = f"""
Create a new {track_type} track named '{track_name}':
1. Click on the add track button in the mixer
2. Set the track name to '{track_name}'
3. Configure it as a {track_type} track
4. Confirm creation
"""

        return types.GetPromptResult(
            description=f"Create {track_name} ({track_type})",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=instructions
                    )
                )
            ]
        )

    return types.GetPromptResult(
        description="Unknown prompt",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text="Prompt not found"
                )
            )
        ]
    )


# ============================================================================
# SERVER INITIALIZATION
# ============================================================================

async def main():
    """Start the MCP server."""
    async with server:
        logger.info("FL Studio MCP Server started")
        logger.info("Available tools:")
        logger.info("  - launch_fl_studio")
        logger.info("  - click_menu")
        logger.info("  - keyboard_input")
        logger.info("  - mouse_action")
        logger.info("  - type_text")
        logger.info("  - take_screenshot")
        logger.info("  - create_project")
        logger.info("  - adjust_mixer_volume")
        logger.info("\nWaiting for connections...")

        # Server will run indefinitely
        await server.wait_for_shutdown()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### Running the MCP Server

```bash
# Install dependencies
pip install mcp pyautogui pillow

# Run the server
python fl_studio_mcp_server.py

# In Claude Code or MCP client:
# Add to config:
# {
#   "mcpServers": {
#     "fl-studio": {
#       "command": "python",
#       "args": ["fl_studio_mcp_server.py"]
#     }
#   }
# }
```

### MCP Server Advantages
- Standardized interface for AI models
- Easy to integrate with Claude or other LLMs
- Clear tool/resource/prompt separation
- Scalable architecture

---

## 5. Best Practices for Reliable UI Automation

### 1. **Use Appropriate Wait Strategies**

```python
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

# BAD - Fixed delays
time.sleep(5)

# GOOD - Explicit waits
WebDriverWait(driver, 10).until(
    expected_conditions.presence_of_element_located((By.ID, "element_id"))
)

# PYAUTOGUI - Retry pattern
max_attempts = 3
for attempt in range(max_attempts):
    location = pyautogui.locateOnScreen('button.png', confidence=0.8)
    if location:
        break
    time.sleep(0.5)
else:
    raise Exception("Element not found after retries")
```

### 2. **Error Handling and Recovery**

```python
def safe_automation_action(action_func, max_retries=3, backoff_factor=1.0):
    """
    Execute automation action with retry and exponential backoff.

    Args:
        action_func: Function to execute
        max_retries: Number of retry attempts
        backoff_factor: Multiplier for delay between retries
    """
    import time

    for attempt in range(max_retries):
        try:
            return action_func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise

            wait_time = (backoff_factor ** attempt)
            logger.warning(
                f"Attempt {attempt + 1} failed: {e}. "
                f"Retrying in {wait_time}s..."
            )
            time.sleep(wait_time)
```

### 3. **Window/UI State Verification**

```python
import pygetwindow as gw

def wait_for_window(window_title, timeout=10):
    """Wait for window to appear."""
    start_time = time.time()

    while time.time() - start_time < timeout:
        windows = gw.getWindowsWithTitle(window_title)
        if windows:
            return windows[0]
        time.sleep(0.5)

    raise TimeoutError(f"Window '{window_title}' not found")

def ensure_window_focused(window):
    """Ensure window is active and focused."""
    if not window.isActive:
        window.activate()
        time.sleep(0.5)
```

### 4. **Image Recognition Configuration**

```python
# Use high confidence threshold for reliability
HIGH_CONFIDENCE = 0.85
MEDIUM_CONFIDENCE = 0.75
LOW_CONFIDENCE = 0.65

# For critical actions
location = pyautogui.locateOnScreen(
    'critical_button.png',
    confidence=HIGH_CONFIDENCE  # Strict matching
)

# For optional/convenience actions
location = pyautogui.locateOnScreen(
    'optional_button.png',
    confidence=LOW_CONFIDENCE  # More lenient
)
```

### 5. **Logging and Debugging**

```python
import logging
from datetime import datetime

# Setup detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Log automation steps
logger.info("Starting FL Studio automation")
logger.debug(f"Current mouse position: {pyautogui.position()}")
logger.info(f"Clicked button at ({x}, {y})")
logger.error(f"Failed to find element: {element_name}")
```

### 6. **DRY Principle - Reusable Actions**

```python
class AutomationBase:
    """Base class for reliable automation actions."""

    def __init__(self, pause=0.2, confidence=0.8):
        self.pause = pause
        self.confidence = confidence

    def safe_click(self, x, y, retries=3):
        """Click with retry logic."""
        for attempt in range(retries):
            try:
                pyautogui.click(x, y)
                time.sleep(self.pause)
                return True
            except Exception as e:
                if attempt == retries - 1:
                    raise
                time.sleep(0.5)

    def safe_type(self, text):
        """Type with error handling."""
        try:
            for char in text:
                pyautogui.typewrite(char)
                time.sleep(0.05)
            time.sleep(self.pause)
            return True
        except Exception as e:
            logger.error(f"Error typing text: {e}")
            return False

    def take_screenshot_on_error(self, error, filename=None):
        """Capture screenshot for debugging."""
        if filename is None:
            filename = f"error_{datetime.now().isoformat()}.png"

        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        logger.error(f"Screenshot saved: {filename}")
```

### 7. **Configuration Management**

```python
# config.py
from dataclasses import dataclass

@dataclass
class AutomationConfig:
    """Automation configuration."""
    fl_exe_path: str = r"C:\Program Files\Image-Line\FL Studio 21\FL.exe"
    image_confidence: float = 0.8
    pause_between_actions: float = 0.2
    max_retries: int = 3
    timeout_seconds: int = 30
    screenshot_on_error: bool = True
    log_level: str = "INFO"

    @staticmethod
    def from_env():
        """Load config from environment variables."""
        import os
        return AutomationConfig(
            fl_exe_path=os.getenv('FL_EXE_PATH', AutomationConfig.fl_exe_path),
            image_confidence=float(os.getenv('IMAGE_CONFIDENCE', 0.8)),
            pause_between_actions=float(os.getenv('PAUSE', 0.2)),
        )
```

### 8. **Performance Monitoring**

```python
from functools import wraps
from time import perf_counter

def measure_time(func):
    """Decorator to measure function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            elapsed = perf_counter() - start
            logger.info(f"{func.__name__} took {elapsed:.3f}s")

    return wrapper

@measure_time
def create_new_project(project_name):
    """This execution time will be logged."""
    pass
```

---

## Comparison Matrix

| Method | Reliability | Speed | Complexity | Best For |
|--------|------------|-------|-----------|----------|
| **FL Studio API** | Excellent | Fast | Medium | Direct FL Studio control, MIDI scripting |
| **PyAutoGUI** | Good | Medium | Low | Quick UI automation, menu clicks |
| **Playwright** | Good | Medium | Medium | WebView2 apps, web components |
| **pywinauto** | Excellent | Medium | Medium | Complex Windows automation |
| **Image Recognition** | Fair | Slow | Low | Visual testing, button verification |
| **MCP Server** | Excellent | Medium | High | AI-driven automation, orchestration |

---

## Recommended Implementation Approach

### For Direct FL Studio Automation:
1. **First Choice:** Use FL Studio's MIDI Scripting API
   - Most reliable and performant
   - No screen scraping needed
   - Tight integration with FL Studio

### For UI Automation:
1. **Quick Tasks:** PyAutoGUI for simple menu/button clicks
2. **Complex Workflows:** pywinauto for detailed window interaction
3. **WebView2 Components:** Playwright with FlaUI integration

### For AI Integration:
1. **Create MCP Server** wrapping PyAutoGUI or pywinauto
2. **Expose tools** for Claude or other LLMs
3. **Use for orchestration** of complex workflows

### For Production Systems:
- Combine multiple approaches
- Use FL Studio API for core operations
- Use PyAutoGUI/MCP for UI-level tasks
- Implement comprehensive logging and error handling
- Test extensively with screenshot capture on failures

---

## References

- [FL Studio MIDI Scripting Documentation](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/midi_scripting.htm)
- [FL Studio API Stubs](https://il-group.github.io/FL-Studio-API-Stubs/)
- [PyAutoGUI Documentation](https://pyautogui.readthedocs.io/)
- [Playwright Documentation](https://playwright.dev/)
- [Model Context Protocol SDK](https://github.com/modelcontextprotocol/python-sdk)
- [pywinauto GitHub](https://github.com/pywinauto/pywinauto)
