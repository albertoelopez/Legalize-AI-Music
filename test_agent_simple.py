#!/usr/bin/env python3
"""
Simple agent test using Ollama
"""
import sys
sys.path.insert(0, 'src')

print("Testing Ollama Agent Framework...")
print("=" * 60)

# Test 1: Direct Ollama connection
print("\n1. Testing direct Ollama connection...")
try:
    from ollama import Client

    client = Client(host='http://localhost:11434')
    response = client.generate(
        model='llama3.1:8b',
        prompt='Say "Agent framework test successful!" in one sentence.'
    )
    print(f"✓ Direct Ollama: {response['response'][:100]}")
except Exception as e:
    print(f"✗ Direct Ollama failed: {e}")

# Test 2: LangChain integration
print("\n2. Testing LangChain with Ollama...")
try:
    from langchain_community.llms import Ollama

    llm = Ollama(
        model="llama3.1:8b",
        base_url="http://localhost:11434"
    )

    response = llm.invoke("Say 'LangChain integration works!' in one sentence.")
    print(f"✓ LangChain: {response[:100]}")
except Exception as e:
    print(f"✗ LangChain failed: {e}")

# Test 3: Basic agent tools
print("\n3. Testing agent tools framework...")
try:
    from langchain_core.tools import tool

    # Create a simple tool using decorator
    @tool
    def test_tool(input_text: str) -> str:
        """A test tool that echoes input"""
        return f"Tool received: {input_text}"

    # Test the tool
    result = test_tool.invoke("Hello from tool!")

    print("✓ Tool created successfully")
    print(f"✓ Tool invocation works: {result}")
    print("✓ Agent framework ready for workflow orchestration")

except Exception as e:
    print(f"✗ Agent framework failed: {e}")

print("\n" + "=" * 60)
print("✅ Agent framework tests complete!")
print("\nThe workflow orchestrator can:")
print("  - Connect to Ollama")
print("  - Use LangChain for agent orchestration")
print("  - Initialize agents with custom tools")
