"""
FL Studio UI Automation using PyAutoGUI
Production-ready automation for FL Studio menu/button interactions
"""

import pyautogui
import time
import subprocess
import logging
from pathlib import Path
from typing import Optional, Tuple, List, Dict
from dataclasses import dataclass
from enum import Enum


# ============================================================================
# CONFIGURATION & SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fl_studio_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# PyAutoGUI Configuration
pyautogui.FAILSAFE = True  # Move mouse to corner to stop
pyautogui.PAUSE = 0.1      # Pause between actions

FL_EXE_PATH = r"C:\Program Files\Image-Line\FL Studio 21\FL.exe"
IMAGE_CONFIDENCE = 0.8
DEFAULT_TIMEOUT = 30
DEFAULT_PAUSE = 0.2


@dataclass
class Point:
    """2D point."""
    x: int
    y: int

    def __iter__(self):
        return iter((self.x, self.y))


class WindowState(Enum):
    """Window states."""
    RUNNING = "running"
    STOPPED = "stopped"
    UNKNOWN = "unknown"


# ============================================================================
# AUTOMATION ENGINE
# ============================================================================

class FLStudioAutomation:
    """High-level FL Studio automation controller."""

    def __init__(self, fl_path: str = FL_EXE_PATH):
        """Initialize automation."""
        self.fl_path = fl_path
        self.fl_process = None
        self.pauses_between_actions = DEFAULT_PAUSE
        self.image_confidence = IMAGE_CONFIDENCE
        self.logger = logger

    # ========================================================================
    # LIFECYCLE MANAGEMENT
    # ========================================================================

    def launch(self, wait_seconds: int = 5) -> bool:
        """
        Launch FL Studio if not already running.

        Args:
            wait_seconds: Time to wait for startup

        Returns:
            True if successfully launched or already running
        """
        try:
            import psutil

            # Check if already running
            for proc in psutil.process_iter(['name']):
                try:
                    if 'FL.exe' in proc.name():
                        self.logger.info("FL Studio is already running")
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            # Launch FL Studio
            self.logger.info(f"Launching FL Studio from {self.fl_path}")
            self.fl_process = subprocess.Popen(self.fl_path)
            time.sleep(wait_seconds)

            self.logger.info(f"FL Studio launched (PID: {self.fl_process.pid})")
            return True

        except Exception as e:
            self.logger.error(f"Error launching FL Studio: {e}")
            return False

    def close(self) -> bool:
        """Close FL Studio."""
        try:
            if self.fl_process:
                self.fl_process.terminate()
                self.fl_process.wait(timeout=5)
                self.logger.info("FL Studio closed")
                return True
        except Exception as e:
            self.logger.error(f"Error closing FL Studio: {e}")
        return False

    def focus_window(self) -> bool:
        """Focus FL Studio window."""
        try:
            import pygetwindow as gw

            windows = gw.getWindowsWithTitle("FL Studio")
            if windows:
                window = windows[0]
                window.activate()
                time.sleep(0.5)
                self.logger.debug("FL Studio window focused")
                return True
            else:
                self.logger.error("FL Studio window not found")
                return False

        except Exception as e:
            self.logger.error(f"Error focusing window: {e}")
            return False

    # ========================================================================
    # MOUSE CONTROL
    # ========================================================================

    def click(self, x: int, y: int, button: str = 'left',
              retries: int = 1, wait_after: float = None) -> bool:
        """
        Click at coordinates with retry logic.

        Args:
            x, y: Coordinates
            button: 'left', 'right', or 'middle'
            retries: Number of retry attempts
            wait_after: Pause after click (seconds)

        Returns:
            True if successful
        """
        wait_after = wait_after or self.pauses_between_actions

        for attempt in range(retries):
            try:
                pyautogui.click(x, y, button=button)
                time.sleep(wait_after)
                self.logger.debug(f"Clicked ({x}, {y}) with {button} button")
                return True

            except Exception as e:
                if attempt == retries - 1:
                    self.logger.error(f"Click failed after {retries} attempts: {e}")
                    return False
                time.sleep(0.5)

        return False

    def double_click(self, x: int, y: int, wait_after: float = None) -> bool:
        """Double click at coordinates."""
        wait_after = wait_after or self.pauses_between_actions

        try:
            pyautogui.doubleClick(x, y)
            time.sleep(wait_after)
            self.logger.debug(f"Double clicked ({x}, {y})")
            return True
        except Exception as e:
            self.logger.error(f"Double click failed: {e}")
            return False

    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int,
             duration: float = 0.5) -> bool:
        """
        Drag from start to end point.

        Args:
            start_x, start_y: Start coordinates
            end_x, end_y: End coordinates
            duration: Duration of drag (seconds)

        Returns:
            True if successful
        """
        try:
            dx = end_x - start_x
            dy = end_y - start_y
            pyautogui.drag(dx, dy, duration=duration)
            time.sleep(self.pauses_between_actions)
            self.logger.debug(f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})")
            return True
        except Exception as e:
            self.logger.error(f"Drag failed: {e}")
            return False

    def move_to(self, x: int, y: int) -> bool:
        """Move mouse to coordinates."""
        try:
            pyautogui.moveTo(x, y)
            self.logger.debug(f"Mouse moved to ({x}, {y})")
            return True
        except Exception as e:
            self.logger.error(f"Mouse move failed: {e}")
            return False

    # ========================================================================
    # KEYBOARD CONTROL
    # ========================================================================

    def press_key(self, key: str, wait_after: float = None) -> bool:
        """
        Press a key.

        Args:
            key: Key name (e.g., 'enter', 'escape', 'delete')
            wait_after: Pause after key press

        Returns:
            True if successful
        """
        wait_after = wait_after or self.pauses_between_actions

        try:
            pyautogui.press(key)
            time.sleep(wait_after)
            self.logger.debug(f"Pressed key: {key}")
            return True
        except Exception as e:
            self.logger.error(f"Key press failed: {e}")
            return False

    def hotkey(self, *keys, wait_after: float = None) -> bool:
        """
        Press multiple keys simultaneously (hotkey).

        Args:
            *keys: Keys to press (e.g., 'ctrl', 's')
            wait_after: Pause after hotkey

        Returns:
            True if successful
        """
        wait_after = wait_after or self.pauses_between_actions

        try:
            pyautogui.hotkey(*keys)
            time.sleep(wait_after)
            self.logger.debug(f"Hotkey pressed: {'+'.join(keys)}")
            return True
        except Exception as e:
            self.logger.error(f"Hotkey failed: {e}")
            return False

    def type_text(self, text: str, speed: float = 0.05) -> bool:
        """
        Type text character by character.

        Args:
            text: Text to type
            speed: Delay between characters (seconds)

        Returns:
            True if successful
        """
        try:
            for char in text:
                pyautogui.typewrite(char)
                time.sleep(speed)

            time.sleep(self.pauses_between_actions)
            self.logger.debug(f"Typed: {text}")
            return True
        except Exception as e:
            self.logger.error(f"Type text failed: {e}")
            return False

    # ========================================================================
    # IMAGE RECOGNITION
    # ========================================================================

    def find_image(self, image_path: str, confidence: float = None,
                   timeout: int = DEFAULT_TIMEOUT) -> Optional[Point]:
        """
        Find image on screen.

        Args:
            image_path: Path to image file
            confidence: Match confidence (0-1)
            timeout: Timeout in seconds

        Returns:
            Point if found, None otherwise
        """
        confidence = confidence or self.image_confidence
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                location = pyautogui.locateOnScreen(
                    image_path,
                    confidence=confidence
                )
                if location:
                    point = Point(location[0], location[1])
                    self.logger.debug(f"Image found at {point}")
                    return point

            except Exception as e:
                self.logger.debug(f"Error locating image: {e}")

            time.sleep(0.5)

        self.logger.warning(f"Image not found after {timeout}s: {image_path}")
        return None

    def click_image(self, image_path: str, confidence: float = None,
                    retries: int = 3) -> bool:
        """
        Find and click an image.

        Args:
            image_path: Path to image file
            confidence: Match confidence
            retries: Number of retry attempts

        Returns:
            True if clicked
        """
        confidence = confidence or self.image_confidence

        for attempt in range(retries):
            point = self.find_image(image_path, confidence)
            if point:
                return self.click(point.x, point.y)

            if attempt < retries - 1:
                time.sleep(0.5)

        self.logger.error(f"Failed to find and click image: {image_path}")
        return False

    # ========================================================================
    # SCREENSHOT & DEBUGGING
    # ========================================================================

    def take_screenshot(self, filename: str = None) -> str:
        """
        Take screenshot of entire screen.

        Args:
            filename: Output filename (auto-generated if not provided)

        Returns:
            Path to saved screenshot
        """
        if filename is None:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fl_screenshot_{timestamp}.png"

        try:
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            self.logger.info(f"Screenshot saved: {filename}")
            return filename
        except Exception as e:
            self.logger.error(f"Screenshot failed: {e}")
            return None

    def take_region_screenshot(self, x: int, y: int, width: int, height: int,
                               filename: str = None) -> str:
        """
        Take screenshot of screen region.

        Args:
            x, y: Top-left coordinates
            width, height: Region dimensions
            filename: Output filename

        Returns:
            Path to saved screenshot
        """
        if filename is None:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fl_region_{timestamp}.png"

        try:
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            screenshot.save(filename)
            self.logger.info(f"Region screenshot saved: {filename}")
            return filename
        except Exception as e:
            self.logger.error(f"Region screenshot failed: {e}")
            return None


# ============================================================================
# HIGH-LEVEL WORKFLOWS
# ============================================================================

class FLStudioWorkflows(FLStudioAutomation):
    """High-level workflow implementations."""

    def create_new_project(self, project_name: str) -> bool:
        """
        Create a new FL Studio project.

        Args:
            project_name: Name for the project

        Returns:
            True if successful
        """
        self.logger.info(f"Creating new project: {project_name}")

        try:
            # Open File menu
            if not self.hotkey('alt', 'f'):
                return False
            time.sleep(0.5)

            # Click New or press N
            if not self.press_key('n'):
                return False
            time.sleep(1)

            # Type project name
            if not self.type_text(project_name):
                return False
            time.sleep(0.3)

            # Press Enter
            if not self.press_key('enter'):
                return False
            time.sleep(2)

            self.logger.info(f"Project created: {project_name}")
            return True

        except Exception as e:
            self.logger.error(f"Error creating project: {e}")
            return False

    def save_project(self, filepath: str = None) -> bool:
        """
        Save FL Studio project.

        Args:
            filepath: Path to save to (uses default if None)

        Returns:
            True if successful
        """
        self.logger.info("Saving project")

        try:
            # Ctrl+S to save
            if not self.hotkey('ctrl', 's'):
                return False
            time.sleep(2)

            if filepath:
                # Type filepath if saving as
                self.type_text(filepath)
                self.press_key('enter')
                time.sleep(2)

            self.logger.info("Project saved")
            return True

        except Exception as e:
            self.logger.error(f"Error saving project: {e}")
            return False

    def adjust_mixer_volume(self, track_index: int, volume: float,
                            duration: float = 0.5) -> bool:
        """
        Adjust mixer track volume.

        Args:
            track_index: Track index (0-based)
            volume: Volume level (0.0-1.0)
            duration: Duration of fader drag

        Returns:
            True if successful
        """
        # Validate volume
        volume = max(0.0, min(1.0, volume))

        self.logger.info(f"Setting track {track_index} volume to {volume:.2f}")

        try:
            # Calculate mixer track position
            # Approximate positions (depends on screen resolution)
            mixer_x = 50 + (track_index * 60)
            mixer_y = 400

            # Click on track
            if not self.click(mixer_x, mixer_y):
                return False

            time.sleep(0.3)

            # Drag fader
            fader_top = 320
            fader_bottom = 500
            fader_height = fader_bottom - fader_top
            target_y = int(fader_bottom - (volume * fader_height))

            if not self.drag(mixer_x, mixer_y, mixer_x, target_y, duration):
                return False

            self.logger.info(f"Track {track_index} volume adjusted")
            return True

        except Exception as e:
            self.logger.error(f"Error adjusting volume: {e}")
            return False

    def undo_last_action(self) -> bool:
        """Undo last action."""
        return self.hotkey('ctrl', 'z')

    def redo_last_action(self) -> bool:
        """Redo last undone action."""
        return self.hotkey('ctrl', 'y')

    def start_playback(self) -> bool:
        """Start playback."""
        return self.press_key('space')

    def stop_playback(self) -> bool:
        """Stop playback."""
        return self.press_key('space')


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    import sys

    # Create automation controller
    automation = FLStudioWorkflows()

    try:
        # Launch FL Studio
        if not automation.launch(wait_seconds=5):
            sys.exit(1)

        # Focus window
        if not automation.focus_window():
            sys.exit(1)

        time.sleep(2)

        # Example: Create new project
        automation.create_new_project("My Automation Project")
        time.sleep(1)

        # Example: Adjust mixer volumes
        for track in range(5):
            automation.adjust_mixer_volume(track, 0.7, duration=0.3)
            time.sleep(0.5)

        # Example: Save project
        automation.save_project()

        # Take screenshot
        automation.take_screenshot()

        logger.info("Automation completed successfully")

    except KeyboardInterrupt:
        logger.info("Automation interrupted by user")
    except Exception as e:
        logger.error(f"Automation error: {e}")
        automation.take_screenshot("error_screenshot.png")
    finally:
        # Optionally close FL Studio
        # automation.close()
        pass
