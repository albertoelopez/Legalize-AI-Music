#!/usr/bin/env python3
"""
Simple structure and integration test
Tests project structure without requiring full dependencies
"""

import os
import sys
from pathlib import Path

def test_directory_structure():
    """Test that all required directories exist"""
    print("\n" + "="*60)
    print("TEST 1: Directory Structure")
    print("="*60)

    required_dirs = [
        "src/audio_to_midi",
        "src/fl_studio_automation",
        "src/agent_framework",
        "src/workflow",
        "mcp_servers/fl_studio_mcp",
        "config",
        "docs",
        "tests",
        "output"
    ]

    all_exist = True
    for directory in required_dirs:
        exists = os.path.isdir(directory)
        status = "✓" if exists else "✗"
        print(f"{status} {directory}")
        if not exists:
            all_exist = False

    return all_exist


def test_required_files():
    """Test that all required files exist"""
    print("\n" + "="*60)
    print("TEST 2: Required Files")
    print("="*60)

    required_files = [
        "src/audio_to_midi/converter.py",
        "src/audio_to_midi/processor.py",
        "src/agent_framework/ollama_agent.py",
        "src/agent_framework/tools.py",
        "src/workflow/orchestrator.py",
        "src/workflow/cli.py",
        "mcp_servers/fl_studio_mcp/index.js",
        "mcp_servers/fl_studio_mcp/package.json",
        "mcp_servers/fl_studio_mcp/fl_studio_mcp_server.py",
        "config/config.yaml",
        ".env.example",
        "requirements.txt",
        "setup.sh",
        "README.md"
    ]

    all_exist = True
    for filepath in required_files:
        exists = os.path.isfile(filepath)
        status = "✓" if exists else "✗"
        print(f"{status} {filepath}")
        if not exists:
            all_exist = False

    return all_exist


def test_python_syntax():
    """Test Python files for syntax errors"""
    print("\n" + "="*60)
    print("TEST 3: Python Syntax")
    print("="*60)

    python_files = [
        "src/audio_to_midi/converter.py",
        "src/audio_to_midi/processor.py",
        "src/agent_framework/ollama_agent.py",
        "src/agent_framework/tools.py",
        "src/workflow/orchestrator.py",
        "src/workflow/cli.py",
        "tests/test_full_workflow.py"
    ]

    all_valid = True
    for filepath in python_files:
        try:
            with open(filepath, 'r') as f:
                compile(f.read(), filepath, 'exec')
            print(f"✓ {filepath}")
        except SyntaxError as e:
            print(f"✗ {filepath}: {e}")
            all_valid = False
        except FileNotFoundError:
            print(f"✗ {filepath}: File not found")
            all_valid = False

    return all_valid


def test_documentation():
    """Test that documentation files exist"""
    print("\n" + "="*60)
    print("TEST 4: Documentation")
    print("="*60)

    doc_files = [
        "README.md",
        "docs/QUICKSTART.md",
        "docs/USAGE.md",
        "docs/EXAMPLES.md",
        "docs/SETUP.md"
    ]

    all_exist = True
    for filepath in doc_files:
        exists = os.path.isfile(filepath)
        size = os.path.getsize(filepath) if exists else 0
        status = "✓" if exists else "✗"
        print(f"{status} {filepath} ({size:,} bytes)")
        if not exists:
            all_exist = False

    return all_exist


def test_ollama_connection():
    """Test Ollama connection"""
    print("\n" + "="*60)
    print("TEST 5: Ollama Connection")
    print("="*60)

    try:
        import urllib.request
        import json

        with urllib.request.urlopen('http://localhost:11434/api/version', timeout=2) as response:
            data = json.loads(response.read())
            print(f"✓ Ollama is running")
            print(f"  Version: {data.get('version', 'unknown')}")
            return True
    except Exception as e:
        print(f"✗ Ollama connection failed: {e}")
        print(f"  Make sure Ollama is running: ollama serve")
        return False


def test_ollama_models():
    """Test available Ollama models"""
    print("\n" + "="*60)
    print("TEST 6: Ollama Models")
    print("="*60)

    try:
        import urllib.request
        import json

        with urllib.request.urlopen('http://localhost:11434/api/tags', timeout=2) as response:
            data = json.loads(response.read())
            models = data.get('models', [])

            if models:
                print(f"✓ Found {len(models)} model(s):")
                for model in models[:5]:  # Show first 5
                    name = model.get('name', 'unknown')
                    size = model.get('size', 0) / 1024 / 1024 / 1024  # Convert to GB
                    print(f"  - {name} ({size:.1f} GB)")

                # Check for recommended models
                model_names = [m['name'] for m in models]
                has_mistral = any('mistral' in name for name in model_names)
                has_llama = any('llama' in name for name in model_names)

                if not (has_mistral or has_llama):
                    print(f"  ⚠️  Recommended models (mistral or llama) not found")
                    print(f"     Install with: ollama pull mistral")

                return True
            else:
                print(f"⚠️  No models installed")
                print(f"   Install with: ollama pull mistral")
                return False

    except Exception as e:
        print(f"✗ Failed to check models: {e}")
        return False


def test_config_files():
    """Test configuration files"""
    print("\n" + "="*60)
    print("TEST 7: Configuration")
    print("="*60)

    try:
        # Check .env.example
        if os.path.isfile('.env.example'):
            print(f"✓ .env.example exists")
        else:
            print(f"✗ .env.example missing")
            return False

        # Check if .env exists
        if os.path.isfile('.env'):
            print(f"✓ .env exists (configured)")
        else:
            print(f"⚠️  .env not found (copy from .env.example)")

        # Check config.yaml
        if os.path.isfile('config/config.yaml'):
            print(f"✓ config/config.yaml exists")
        else:
            print(f"✗ config/config.yaml missing")
            return False

        return True

    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("RALPH APP - STRUCTURE AND INTEGRATION TEST")
    print("="*60)

    results = {
        "Directory Structure": test_directory_structure(),
        "Required Files": test_required_files(),
        "Python Syntax": test_python_syntax(),
        "Documentation": test_documentation(),
        "Ollama Connection": test_ollama_connection(),
        "Ollama Models": test_ollama_models(),
        "Configuration": test_config_files()
    }

    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for v in results.values() if v)
    failed = sum(1 for v in results.values() if not v)

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print("\n" + "-"*60)
    print(f"Total: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print("="*60)

    if failed == 0:
        print("\n🎉 All tests passed! Project structure is valid.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Copy .env.example to .env and configure")
        print("3. Run full tests: python tests/test_full_workflow.py")
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
