"""Ollama-based agent for workflow orchestration."""

from typing import Optional, List, Dict, Any
from langchain_community.llms import Ollama
from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate
from .tools import AudioToMIDITool, FLStudioTool, WorkflowTool


class OllamaAgent:
    """Agent that uses Ollama with open source models for workflow orchestration."""

    def __init__(
        self,
        model_name: str = "mistral",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.7,
    ):
        """Initialize the Ollama agent.

        Args:
            model_name: Name of the Ollama model to use
            base_url: Base URL for Ollama API
            temperature: Sampling temperature
        """
        self.model_name = model_name
        self.base_url = base_url
        self.llm = Ollama(
            model=model_name,
            base_url=base_url,
            temperature=temperature,
        )

        self.tools = self._setup_tools()

    def _setup_tools(self) -> Dict[str, Any]:
        """Setup tools for the agent.

        Returns:
            Dict of tool name to tool instance
        """
        return {
            "audio_to_midi": AudioToMIDITool(),
            "fl_studio": FLStudioTool(),
            "workflow": WorkflowTool(),
        }

    def run(self, task: str) -> Dict[str, Any]:
        """Run the agent with a task.

        Args:
            task: Task description

        Returns:
            Dict with output and status
        """
        try:
            # Use LLM directly for now
            prompt = f"""You are an AI agent that helps automate music production workflows.
You can convert audio to MIDI and integrate with FL Studio.

Task: {task}

Provide a response outlining how to accomplish this task."""

            result = self.llm.invoke(prompt)
            return {
                "success": True,
                "output": result,
                "task": task,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "task": task,
            }

    async def arun(self, task: str) -> Dict[str, Any]:
        """Run the agent asynchronously.

        Args:
            task: Task description

        Returns:
            Dict with output and status
        """
        try:
            prompt = f"""You are an AI agent that helps automate music production workflows.
You can convert audio to MIDI and integrate with FL Studio.

Task: {task}

Provide a response outlining how to accomplish this task."""

            result = await self.llm.ainvoke(prompt)
            return {
                "success": True,
                "output": result,
                "task": task,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "task": task,
            }
