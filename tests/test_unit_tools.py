"""
Unit tests for agent tools
"""
import os
import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_langchain_tool_import():
    """Test that we can import LangChain tools"""
    try:
        from langchain_core.tools import tool
        assert tool is not None
    except ImportError as e:
        pytest.fail(f"Failed to import LangChain tool: {e}")


def test_create_simple_tool():
    """Test creating a simple tool"""
    from langchain_core.tools import tool

    @tool
    def test_function(text: str) -> str:
        """A test function"""
        return f"Processed: {text}"

    result = test_function.invoke("hello")
    assert result == "Processed: hello"
    assert test_function.name == "test_function"
    assert "test function" in test_function.description.lower()


def test_tool_with_complex_input():
    """Test tool with complex input"""
    from langchain_core.tools import tool

    @tool
    def calculate(a: int, b: int) -> int:
        """Add two numbers"""
        return a + b

    result = calculate.invoke({"a": 5, "b": 3})
    assert result == 8


def test_workflow_state_file():
    """Test workflow state file operations"""
    import json
    import tempfile

    # Create temp state file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        state = {"status": "running", "progress": 50}
        json.dump(state, f)
        temp_path = f.name

    try:
        # Read state
        with open(temp_path, 'r') as f:
            loaded_state = json.load(f)

        assert loaded_state["status"] == "running"
        assert loaded_state["progress"] == 50
    finally:
        os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
