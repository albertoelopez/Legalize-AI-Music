"""Main workflow orchestrator."""

import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List
import sys

sys.path.append(str(Path(__file__).parent.parent))

from agent_framework import OllamaAgent
from audio_to_midi import AudioToMIDIConverter, AudioProcessor


class WorkflowOrchestrator:
    """Orchestrates the Suno AI to MIDI FL Studio workflow."""

    def __init__(
        self,
        model_name: str = "mistral",
        ollama_url: str = "http://localhost:11434",
    ):
        """Initialize the orchestrator.

        Args:
            model_name: Ollama model to use
            ollama_url: Ollama API URL
        """
        self.agent = OllamaAgent(
            model_name=model_name,
            base_url=ollama_url,
        )
        self.audio_converter = AudioToMIDIConverter()
        self.audio_processor = AudioProcessor()
        self.is_running = False
        self.output_dir = Path("output")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def start(self, prompt: str) -> Dict[str, Any]:
        """Start the workflow with a user prompt.

        Args:
            prompt: User's task description

        Returns:
            Dict with workflow results
        """
        self.is_running = True

        try:
            # Parse the prompt to understand the task
            task = f"""
            User Request: {prompt}

            Your task is to:
            1. If audio files are mentioned, convert them to MIDI
            2. If FL Studio actions are needed, perform them
            3. Provide a clear summary of actions taken

            Execute the workflow step by step.
            """

            result = self.agent.run(task)

            return {
                "success": True,
                "prompt": prompt,
                "agent_output": result,
                "status": "completed",
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "status": "failed",
            }
        finally:
            self.is_running = False

    async def start_async(self, prompt: str) -> Dict[str, Any]:
        """Start the workflow asynchronously.

        Args:
            prompt: User's task description

        Returns:
            Dict with workflow results
        """
        self.is_running = True

        try:
            task = f"""
            User Request: {prompt}

            Your task is to:
            1. If audio files are mentioned, convert them to MIDI
            2. If FL Studio actions are needed, perform them
            3. Provide a clear summary of actions taken

            Execute the workflow step by step.
            """

            result = await self.agent.arun(task)

            return {
                "success": True,
                "prompt": prompt,
                "agent_output": result,
                "status": "completed",
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "status": "failed",
            }
        finally:
            self.is_running = False

    def stop(self) -> Dict[str, Any]:
        """Stop the workflow.

        Returns:
            Dict with stop status
        """
        if self.is_running:
            self.is_running = False
            return {
                "success": True,
                "message": "Workflow stopped",
            }
        else:
            return {
                "success": False,
                "message": "No workflow is running",
            }

    def get_status(self) -> Dict[str, Any]:
        """Get workflow status.

        Returns:
            Dict with status information
        """
        return {
            "is_running": self.is_running,
            "output_directory": str(self.output_dir),
            "model": self.agent.llm.model,
        }

    def process_audio_batch(
        self,
        audio_files: List[str],
        add_to_fl_studio: bool = False,
    ) -> Dict[str, Any]:
        """Process a batch of audio files.

        Args:
            audio_files: List of audio file paths
            add_to_fl_studio: Whether to add to FL Studio

        Returns:
            Dict with processing results
        """
        results = []

        for audio_file in audio_files:
            try:
                # Convert to MIDI
                midi_output_dir = self.output_dir / "midi"
                midi_output_dir.mkdir(parents=True, exist_ok=True)

                result = self.audio_converter.convert(
                    audio_file,
                    str(midi_output_dir)
                )

                results.append({
                    "audio_file": audio_file,
                    "midi_file": result.get("output_midi"),
                    "success": result.get("success"),
                    "midi_info": result.get("midi_info"),
                })

                # Optionally add to FL Studio
                if add_to_fl_studio and result.get("success"):
                    fl_task = f"Add MIDI file {result.get('output_midi')} to FL Studio"
                    self.agent.run(fl_task)

            except Exception as e:
                results.append({
                    "audio_file": audio_file,
                    "success": False,
                    "error": str(e),
                })

        return {
            "success": True,
            "total_files": len(audio_files),
            "results": results,
        }
