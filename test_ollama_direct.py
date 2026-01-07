#!/usr/bin/env python3
"""
Direct Ollama test without dependencies
"""
import json
import urllib.request

def test_ollama_connection():
    """Test basic Ollama connection"""
    print("Testing Ollama connection...")

    try:
        # Test version endpoint
        with urllib.request.urlopen('http://localhost:11434/api/version', timeout=5) as response:
            version_data = json.loads(response.read())
            print(f"✓ Ollama version: {version_data.get('version')}")

        # Test models list
        with urllib.request.urlopen('http://localhost:11434/api/tags', timeout=5) as response:
            models_data = json.loads(response.read())
            models = models_data.get('models', [])
            print(f"✓ Found {len(models)} model(s)")

            # Show available models
            for model in models[:3]:
                name = model.get('name')
                print(f"  - {name}")

        # Test a simple generation
        print("\nTesting generation with llama3.1:8b...")
        payload = {
            "model": "llama3.1:8b",
            "prompt": "Say 'Hello from Ollama!' in one short sentence.",
            "stream": False
        }

        req = urllib.request.Request(
            'http://localhost:11434/api/generate',
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read())
            generated_text = result.get('response', '')
            print(f"✓ Generated response: {generated_text[:100]}")

        print("\n✅ All Ollama tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Ollama test failed: {e}")
        return False

if __name__ == "__main__":
    test_ollama_connection()
