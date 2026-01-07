"""Agent framework for orchestrating Suno AI to MIDI workflow with Ollama."""

from .ollama_agent import OllamaAgent
from .tools import AudioToMIDITool, FLStudioTool, WorkflowTool

__all__ = ["OllamaAgent", "AudioToMIDITool", "FLStudioTool", "WorkflowTool"]
