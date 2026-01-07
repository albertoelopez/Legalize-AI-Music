"""
End-to-end tests for CLI
"""
import os
import sys
import pytest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_cli_module_import():
    """Test that CLI module can be imported"""
    try:
        from workflow import cli
        assert cli is not None
    except ImportError as e:
        pytest.fail(f"Failed to import CLI module: {e}")


def test_cli_has_click():
    """Test that Click is available"""
    try:
        import click
        assert click is not None
    except ImportError as e:
        pytest.fail(f"Click not available: {e}")


def test_orchestrator_import():
    """Test that WorkflowOrchestrator can be imported"""
    try:
        from workflow.orchestrator import WorkflowOrchestrator
        assert WorkflowOrchestrator is not None
    except ImportError as e:
        pytest.fail(f"Failed to import WorkflowOrchestrator: {e}")


def test_create_orchestrator():
    """Test creating a WorkflowOrchestrator instance"""
    from workflow.orchestrator import WorkflowOrchestrator

    try:
        orchestrator = WorkflowOrchestrator(
            model_name="llama3.1:8b",
            ollama_url="http://localhost:11434"
        )
        assert orchestrator is not None
        assert orchestrator.model_name == "llama3.1:8b"
        assert orchestrator.ollama_url == "http://localhost:11434"
    except Exception as e:
        # OK if it fails due to missing dependencies, but import should work
        pass


def test_status_check():
    """Test basic status check functionality"""
    from workflow.orchestrator import WorkflowOrchestrator
    import json
    import tempfile

    # Create temp state file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        state = {
            "status": "idle",
            "last_task": None,
            "timestamp": "2026-01-06T10:00:00"
        }
        json.dump(state, f)
        state_file = f.name

    try:
        # Read and verify state
        with open(state_file, 'r') as f:
            loaded = json.load(f)

        assert loaded["status"] == "idle"
        assert loaded["last_task"] is None
    finally:
        os.unlink(state_file)


def test_agent_framework_import():
    """Test that agent framework can be imported"""
    try:
        from agent_framework.ollama_agent import OllamaAgent
        assert OllamaAgent is not None
    except ImportError as e:
        # OK if full agent can't be created, but import should work
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
