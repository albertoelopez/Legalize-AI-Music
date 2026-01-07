"""
Unit tests for configuration loading
"""
import os
import sys
import yaml
import pytest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_config_yaml_exists():
    """Test that config.yaml exists"""
    config_path = Path("config/config.yaml")
    assert config_path.exists(), "config.yaml should exist"


def test_config_yaml_valid():
    """Test that config.yaml is valid YAML"""
    config_path = Path("config/config.yaml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    assert config is not None, "Config should not be empty"
    assert isinstance(config, dict), "Config should be a dictionary"


def test_config_has_required_sections():
    """Test that config has all required sections"""
    config_path = Path("config/config.yaml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    required_sections = ['ollama', 'audio_to_midi', 'fl_studio', 'workflow', 'agent', 'logging']

    for section in required_sections:
        assert section in config, f"Config should have '{section}' section"


def test_ollama_config():
    """Test Ollama configuration"""
    config_path = Path("config/config.yaml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    ollama = config['ollama']
    assert 'base_url' in ollama
    assert 'model' in ollama
    assert 'temperature' in ollama
    assert isinstance(ollama['temperature'], (int, float))
    assert 0 <= ollama['temperature'] <= 2


def test_env_example_exists():
    """Test that .env.example exists"""
    env_example = Path(".env.example")
    assert env_example.exists(), ".env.example should exist"


def test_env_example_has_required_vars():
    """Test that .env.example has required variables"""
    env_example = Path(".env.example")
    with open(env_example, 'r') as f:
        content = f.read()

    required_vars = [
        'OLLAMA_BASE_URL',
        'OLLAMA_MODEL',
        'OUTPUT_DIR',
        'LOG_LEVEL'
    ]

    for var in required_vars:
        assert var in content, f".env.example should contain {var}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
