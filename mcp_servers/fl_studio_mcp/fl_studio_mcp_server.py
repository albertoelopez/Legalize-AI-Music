"""
FL Studio MCP (Model Context Protocol) Server
Exposes FL Studio automation tools to Claude and other AI models

Installation:
    pip install mcp pyautogui pillow psutil

Usage:
    python fl_studio_mcp_server.py

Configuration in Claude:
    Add to your config:
    {
      "mcpServers": {
        "fl-studio": {
          "command": "python",
          "args": ["fl_studio_mcp_server.py"]
        }
      }
    }
"""

import asyncio
import json
import logging
import subprocess
import time
from pathlib import Path
from typing import Any

import pyautogui
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.types as types


# ============================================================================
# CONFIGURATION
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

FL_EXE_PATH = r"C:\Program Files\Image-Line\FL Studio 21\FL.exe"
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

# Initialize MCP Server
server = Server("fl-studio-automation")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def log_action(message: str):
    """Log action and return as text content."""
    logger.info(message)
    return [types.TextContent(type="text", text=message)]


def log_error(message: str):
    """Log error and return as error content."""
    logger.error(message)
    return [types.TextContent(type="text", text=f"ERROR: {message}")]


# ============================================================================
# TOOL IMPLEMENTATIONS
# ============================================================================

@server.call_tool()
async def launch_fl_studio(arguments: dict) -> list[types.TextContent]:
    """
    Launch FL Studio if not already running.

    Returns:
        Status message
    """
    try:
        import psutil

        # Check if already running
        for proc in psutil.process_iter(['name']):
            try:
                if 'FL.exe' in proc.name():
                    return log_action("FL Studio is already running")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        logger.info(f"Launching FL Studio from {FL_EXE_PATH}")
        process = subprocess.Popen(FL_EXE_PATH)
        time.sleep(5)

        return log_action(f"FL Studio launched successfully (PID: {process.pid})")

    except Exception as e:
        return log_error(f"Failed to launch FL Studio: {str(e)}")


@server.call_tool()
async def close_fl_studio(arguments: dict) -> list[types.TextContent]:
    """Close FL Studio."""
    try:
        import psutil

        for proc in psutil.process_iter(['name']):
            try:
                if 'FL.exe' in proc.name():
                    proc.terminate()
                    proc.wait(timeout=5)
                    return log_action("FL Studio closed successfully")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return log_action("FL Studio was not running")

    except Exception as e:
        return log_error(f"Error closing FL Studio: {str(e)}")


@server.call_tool()
async def focus_window(arguments: dict) -> list[types.TextContent]:
    """Focus FL Studio window."""
    try:
        import pygetwindow as gw

        windows = gw.getWindowsWithTitle("FL Studio")
        if windows:
            window = windows[0]
            window.activate()
            time.sleep(0.5)
            return log_action("FL Studio window focused")
        else:
            return log_error("FL Studio window not found")

    except Exception as e:
        return log_error(f"Error focusing window: {str(e)}")


@server.call_tool()
async def click_position(arguments: dict) -> list[types.TextContent]:
    """
    Click at specific coordinates.

    Arguments:
        - x: X coordinate
        - y: Y coordinate
        - button: "left" (default), "right", or "middle"
    """
    x = arguments.get("x", 0)
    y = arguments.get("y", 0)
    button = arguments.get("button", "left")

    try:
        pyautogui.click(x, y, button=button)
        time.sleep(0.2)
        return log_action(f"Clicked at ({x}, {y}) with {button} button")
    except Exception as e:
        return log_error(f"Click failed: {str(e)}")


@server.call_tool()
async def drag_position(arguments: dict) -> list[types.TextContent]:
    """
    Drag from one position to another.

    Arguments:
        - start_x: Starting X coordinate
        - start_y: Starting Y coordinate
        - end_x: Ending X coordinate
        - end_y: Ending Y coordinate
        - duration: Duration of drag (default: 0.5)
    """
    start_x = arguments.get("start_x", 0)
    start_y = arguments.get("start_y", 0)
    end_x = arguments.get("end_x", 0)
    end_y = arguments.get("end_y", 0)
    duration = arguments.get("duration", 0.5)

    try:
        dx = end_x - start_x
        dy = end_y - start_y
        pyautogui.drag(dx, dy, duration=duration)
        time.sleep(0.2)
        return log_action(f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})")
    except Exception as e:
        return log_error(f"Drag failed: {str(e)}")


@server.call_tool()
async def press_key(arguments: dict) -> list[types.TextContent]:
    """
    Press a keyboard key.

    Arguments:
        - key: Key name (e.g., "enter", "escape", "space")
    """
    key = arguments.get("key", "")

    if not key:
        return log_error("Key argument is required")

    try:
        pyautogui.press(key)
        time.sleep(0.2)
        return log_action(f"Pressed key: {key}")
    except Exception as e:
        return log_error(f"Key press failed: {str(e)}")


@server.call_tool()
async def hotkey(arguments: dict) -> list[types.TextContent]:
    """
    Press hotkey combination.

    Arguments:
        - keys: Space-separated keys (e.g., "ctrl s", "alt f4")
    """
    keys_str = arguments.get("keys", "")

    if not keys_str:
        return log_error("Keys argument is required")

    try:
        keys = keys_str.split()
        pyautogui.hotkey(*keys)
        time.sleep(0.2)
        return log_action(f"Hotkey pressed: {'+'.join(keys)}")
    except Exception as e:
        return log_error(f"Hotkey failed: {str(e)}")


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

    if not text:
        return log_error("Text argument is required")

    try:
        delay = 1.0 / speed
        for char in text:
            pyautogui.typewrite(char)
            time.sleep(delay)

        time.sleep(0.2)
        return log_action(f"Typed: {text}")
    except Exception as e:
        return log_error(f"Typing failed: {str(e)}")


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
        return log_action(f"Screenshot saved: {filename}")
    except Exception as e:
        return log_error(f"Screenshot failed: {str(e)}")


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

        # Alt+F for File menu
        pyautogui.hotkey('alt', 'f')
        time.sleep(0.5)

        # N for New
        pyautogui.press('n')
        time.sleep(1)

        # Type project name
        for char in project_name:
            pyautogui.typewrite(char)
            time.sleep(0.05)

        # Enter to confirm
        pyautogui.press('enter')
        time.sleep(2)

        return log_action(f"Project '{project_name}' created successfully")
    except Exception as e:
        return log_error(f"Error creating project: {str(e)}")


@server.call_tool()
async def save_project(arguments: dict) -> list[types.TextContent]:
    """
    Save the current FL Studio project.

    Arguments:
        - filepath: Optional path to save to
    """
    filepath = arguments.get("filepath", None)

    try:
        # Ctrl+S to save
        pyautogui.hotkey('ctrl', 's')
        time.sleep(2)

        if filepath:
            # Type path
            for char in filepath:
                pyautogui.typewrite(char)
                time.sleep(0.05)
            pyautogui.press('enter')
            time.sleep(2)

        return log_action("Project saved successfully")
    except Exception as e:
        return log_error(f"Error saving project: {str(e)}")


@server.call_tool()
async def adjust_mixer_volume(arguments: dict) -> list[types.TextContent]:
    """
    Adjust mixer track volume by dragging fader.

    Arguments:
        - track_index: Mixer track index (0-based)
        - volume: Volume level (0.0 to 1.0)
        - duration: Duration of drag (default: 0.5)
    """
    track_index = arguments.get("track_index", 0)
    volume = arguments.get("volume", 0.5)
    duration = arguments.get("duration", 0.5)

    # Validate volume
    volume = max(0.0, min(1.0, volume))

    try:
        logger.info(f"Setting track {track_index} volume to {volume:.2f}")

        # Calculate mixer position (approximate)
        mixer_x = 50 + (track_index * 60)
        mixer_y = 400

        # Click track
        pyautogui.click(mixer_x, mixer_y)
        time.sleep(0.3)

        # Drag fader
        fader_top = 320
        fader_bottom = 500
        fader_height = fader_bottom - fader_top
        target_y = int(fader_bottom - (volume * fader_height))

        pyautogui.drag(0, target_y - mixer_y, duration=duration)
        time.sleep(0.2)

        return log_action(f"Track {track_index} volume set to {volume:.2f}")
    except Exception as e:
        return log_error(f"Error adjusting volume: {str(e)}")


@server.call_tool()
async def start_playback(arguments: dict) -> list[types.TextContent]:
    """Start FL Studio playback."""
    try:
        pyautogui.press('space')
        time.sleep(0.2)
        return log_action("Playback started")
    except Exception as e:
        return log_error(f"Error starting playback: {str(e)}")


@server.call_tool()
async def stop_playback(arguments: dict) -> list[types.TextContent]:
    """Stop FL Studio playback."""
    try:
        pyautogui.press('space')
        time.sleep(0.2)
        return log_action("Playback stopped")
    except Exception as e:
        return log_error(f"Error stopping playback: {str(e)}")


@server.call_tool()
async def undo_action(arguments: dict) -> list[types.TextContent]:
    """Undo last action."""
    try:
        pyautogui.hotkey('ctrl', 'z')
        time.sleep(0.2)
        return log_action("Action undone")
    except Exception as e:
        return log_error(f"Error undoing action: {str(e)}")


@server.call_tool()
async def redo_action(arguments: dict) -> list[types.TextContent]:
    """Redo last undone action."""
    try:
        pyautogui.hotkey('ctrl', 'y')
        time.sleep(0.2)
        return log_action("Action redone")
    except Exception as e:
        return log_error(f"Error redoing action: {str(e)}")


# ============================================================================
# RESOURCES
# ============================================================================

@server.list_resources()
async def list_resources() -> list[types.Resource]:
    """List available resources."""
    return [
        types.Resource(
            uri="fl-studio://status",
            name="FL Studio Status",
            description="Current status of FL Studio application",
            mimeType="application/json"
        ),
        types.Resource(
            uri="fl-studio://capabilities",
            name="FL Studio Capabilities",
            description="Available automation capabilities",
            mimeType="application/json"
        ),
    ]


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read a resource."""
    try:
        if uri == "fl-studio://status":
            import psutil
            fl_running = False

            for proc in psutil.process_iter(['name']):
                try:
                    if 'FL.exe' in proc.name():
                        fl_running = True
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            return json.dumps({
                "status": "running" if fl_running else "stopped",
                "version": "21",
                "api_version": "1.0"
            })

        elif uri == "fl-studio://capabilities":
            return json.dumps({
                "capabilities": [
                    "launch_fl_studio",
                    "close_fl_studio",
                    "focus_window",
                    "create_project",
                    "save_project",
                    "adjust_mixer_volume",
                    "start_playback",
                    "stop_playback",
                    "undo_action",
                    "redo_action",
                    "take_screenshot"
                ]
            })

    except Exception as e:
        logger.error(f"Error reading resource: {e}")

    return json.dumps({"error": "Unknown resource"})


# ============================================================================
# PROMPTS
# ============================================================================

@server.list_prompts()
async def list_prompts() -> list[types.Prompt]:
    """List available prompt templates."""
    return [
        types.Prompt(
            name="create_and_setup_project",
            description="Create a new project and set up basic tracks",
            arguments=[
                types.PromptArgument(
                    name="project_name",
                    description="Name of the project",
                    required=True
                ),
                types.PromptArgument(
                    name="tempo",
                    description="Project tempo in BPM",
                    required=False
                ),
            ]
        ),
        types.Prompt(
            name="setup_mixer",
            description="Configure mixer tracks and levels",
            arguments=[
                types.PromptArgument(
                    name="track_count",
                    description="Number of tracks to set up",
                    required=False
                ),
            ]
        ),
    ]


@server.get_prompt()
async def get_prompt(name: str, arguments: dict) -> types.GetPromptResult:
    """Get a prompt template."""
    if name == "create_and_setup_project":
        project_name = arguments.get("project_name", "My Project")
        tempo = arguments.get("tempo", "120")

        instructions = f"""
Create and setup a new FL Studio project:
1. Launch FL Studio
2. Create a new project named '{project_name}'
3. Set project tempo to {tempo} BPM
4. Save the project
"""

        return types.GetPromptResult(
            description=f"Setup project: {project_name}",
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
        messages=[]
    )


# ============================================================================
# SERVER INITIALIZATION
# ============================================================================

async def main():
    """Start the MCP server."""
    async with server:
        logger.info("=" * 60)
        logger.info("FL Studio MCP Server Started")
        logger.info("=" * 60)
        logger.info("\nAvailable Tools:")
        logger.info("  - launch_fl_studio")
        logger.info("  - close_fl_studio")
        logger.info("  - focus_window")
        logger.info("  - click_position")
        logger.info("  - drag_position")
        logger.info("  - press_key")
        logger.info("  - hotkey")
        logger.info("  - type_text")
        logger.info("  - take_screenshot")
        logger.info("  - create_project")
        logger.info("  - save_project")
        logger.info("  - adjust_mixer_volume")
        logger.info("  - start_playback")
        logger.info("  - stop_playback")
        logger.info("  - undo_action")
        logger.info("  - redo_action")
        logger.info("\nServer ready for connections...")
        logger.info("=" * 60)

        await server.wait_for_shutdown()


if __name__ == "__main__":
    asyncio.run(main())
