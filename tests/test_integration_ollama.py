"""
Integration tests for Ollama connection
"""
import os
import sys
import pytest
import json
import urllib.request
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def ollama_available():
    """Check if Ollama is available"""
    try:
        with urllib.request.urlopen('http://localhost:11434/api/version', timeout=2) as response:
            return response.status == 200
    except:
        return False


def test_ollama_connection(ollama_available):
    """Test basic Ollama connection"""
    if not ollama_available:
        pytest.skip("Ollama not available")

    with urllib.request.urlopen('http://localhost:11434/api/version', timeout=5) as response:
        data = json.loads(response.read())
        assert 'version' in data
        assert data['version'] is not None


def test_ollama_models_list(ollama_available):
    """Test listing Ollama models"""
    if not ollama_available:
        pytest.skip("Ollama not available")

    with urllib.request.urlopen('http://localhost:11434/api/tags', timeout=5) as response:
        data = json.loads(response.read())
        assert 'models' in data
        assert isinstance(data['models'], list)


def test_ollama_generation(ollama_available):
    """Test Ollama text generation"""
    if not ollama_available:
        pytest.skip("Ollama not available")

    payload = {
        "model": "llama3.1:8b",
        "prompt": "Say 'test' in one word.",
        "stream": False
    }

    req = urllib.request.Request(
        'http://localhost:11434/api/generate',
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read())
        assert 'response' in result
        assert len(result['response']) > 0


def test_ollama_client_import():
    """Test importing Ollama client"""
    try:
        from ollama import Client
        assert Client is not None
    except ImportError as e:
        pytest.fail(f"Failed to import Ollama client: {e}")


def test_ollama_client_connection(ollama_available):
    """Test Ollama client connection"""
    if not ollama_available:
        pytest.skip("Ollama not available")

    from ollama import Client

    client = Client(host='http://localhost:11434')
    response = client.generate(
        model='llama3.1:8b',
        prompt='Say hello in one word'
    )

    assert 'response' in response
    assert len(response['response']) > 0


def test_langchain_ollama_import():
    """Test importing LangChain Ollama integration"""
    try:
        from langchain_community.llms import Ollama
        assert Ollama is not None
    except ImportError as e:
        pytest.fail(f"Failed to import LangChain Ollama: {e}")


def test_langchain_ollama_generation(ollama_available):
    """Test LangChain with Ollama generation"""
    if not ollama_available:
        pytest.skip("Ollama not available")

    from langchain_community.llms import Ollama

    llm = Ollama(
        model="llama3.1:8b",
        base_url="http://localhost:11434"
    )

    response = llm.invoke("Say 'integration test' in two words")
    assert isinstance(response, str)
    assert len(response) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
