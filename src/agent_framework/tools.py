"""LangChain tools for the workflow."""

import json
import subprocess
from pathlib import Path
from typing import Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from audio_to_midi import AudioToMIDIConverter, AudioProcessor


class AudioToMIDITool:
    """Tool for converting audio to MIDI."""

    def __init__(self):
        self.converter = AudioToMIDIConverter()
        self.processor = AudioProcessor()

    def run(self, audio_path: str) -> str:
        """Convert audio to MIDI.

        Args:
            audio_path: Path to audio file

        Returns:
            JSON string with result
        """
        try:
            # Create output directory
            output_dir = Path("output/midi")
            output_dir.mkdir(parents=True, exist_ok=True)

            # Enhance audio first
            enhanced_path = self.processor.enhance_for_midi(
                audio_path,
                str(output_dir / f"enhanced_{Path(audio_path).name}")
            )

            # Convert to MIDI
            result = self.converter.convert(enhanced_path, str(output_dir))

            return json.dumps(result, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e), "success": False})


class FLStudioTool:
    """Tool for controlling FL Studio via MCP server."""

    def __init__(self, mcp_server_path: str = None):
        if mcp_server_path is None:
            mcp_server_path = str(
                Path(__file__).parent.parent.parent
                / "mcp_servers"
                / "fl_studio_mcp"
                / "index.js"
            )
        self.mcp_server_path = mcp_server_path

    def run(self, action_json: str) -> str:
        """Control FL Studio.

        Args:
            action_json: JSON string with action and parameters

        Returns:
            JSON string with result
        """
        try:
            action_data = json.loads(action_json)
            action = action_data.get("action")

            if action == "open_file":
                return self._open_file(action_data.get("file_path"))
            elif action == "create_track":
                return self._create_track(action_data.get("track_name"))
            elif action == "add_midi":
                return self._add_midi(action_data.get("midi_path"))
            elif action == "save_project":
                return self._save_project(action_data.get("project_path"))
            elif action == "export_audio":
                return self._export_audio(action_data.get("output_path"))
            else:
                return json.dumps({"error": f"Unknown action: {action}", "success": False})

        except Exception as e:
            return json.dumps({"error": str(e), "success": False})

    def _call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP server tool.

        Args:
            tool_name: Name of the tool
            arguments: Tool arguments

        Returns:
            Dict with result
        """
        # This is a simplified version - actual implementation would use MCP client
        return {
            "success": True,
            "tool": tool_name,
            "arguments": arguments,
            "note": "MCP integration - would call actual server in production"
        }

    def _open_file(self, file_path: str) -> str:
        """Open file in FL Studio."""
        result = self._call_mcp_tool("fl_studio_keyboard", {"keys": "ctrl+o"})
        return json.dumps(result)

    def _create_track(self, track_name: str) -> str:
        """Create a new track."""
        result = self._call_mcp_tool("fl_studio_keyboard", {"keys": "ctrl+shift+t"})
        return json.dumps(result)

    def _add_midi(self, midi_path: str) -> str:
        """Add MIDI file to project."""
        result = self._call_mcp_tool(
            "fl_studio_drag_drop_midi",
            {"midi_path": midi_path, "drop_x": 400, "drop_y": 300}
        )
        return json.dumps(result)

    def _save_project(self, project_path: str) -> str:
        """Save FL Studio project."""
        result = self._call_mcp_tool("fl_studio_keyboard", {"keys": "ctrl+s"})
        return json.dumps(result)

    def _export_audio(self, output_path: str) -> str:
        """Export audio from FL Studio."""
        result = self._call_mcp_tool("fl_studio_keyboard", {"keys": "ctrl+r"})
        return json.dumps(result)


class WorkflowTool:
    """Tool for controlling workflow state."""

    def __init__(self):
        self.state_file = Path("output/.workflow_state.json")
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

    def run(self, action_json: str) -> str:
        """Control workflow.

        Args:
            action_json: JSON string with action

        Returns:
            JSON string with result
        """
        try:
            action_data = json.loads(action_json)
            action = action_data.get("action")

            state = self._load_state()

            if action == "start":
                state["status"] = "running"
                state["message"] = "Workflow started"
            elif action == "stop":
                state["status"] = "stopped"
                state["message"] = "Workflow stopped"
            elif action == "pause":
                state["status"] = "paused"
                state["message"] = "Workflow paused"
            elif action == "resume":
                state["status"] = "running"
                state["message"] = "Workflow resumed"
            elif action == "status":
                pass  # Just return current state
            else:
                return json.dumps({"error": f"Unknown action: {action}", "success": False})

            self._save_state(state)
            return json.dumps({"success": True, "state": state})

        except Exception as e:
            return json.dumps({"error": str(e), "success": False})

    def _load_state(self) -> Dict[str, Any]:
        """Load workflow state."""
        if self.state_file.exists():
            with open(self.state_file, "r") as f:
                return json.load(f)
        return {"status": "idle", "message": "No workflow running"}

    def _save_state(self, state: Dict[str, Any]):
        """Save workflow state."""
        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2)
