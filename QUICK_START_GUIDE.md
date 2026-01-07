# Quick Start Guide: Ollama + LangChain Local Agent

## 5-Minute Setup

### Step 1: Install Ollama (2 minutes)

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl https://ollama.ai/install.sh | sh
```

**Windows:**
- Download from https://ollama.ai
- Run installer

### Step 2: Start Ollama Server (1 minute)

```bash
# Start the server (runs in background)
ollama serve

# In another terminal, verify it's running
curl http://localhost:11434/api/tags
```

### Step 3: Download a Model (1 minute)

```bash
# Download Mistral (fast, good performance)
ollama pull mistral

# Or download Llama 2
ollama pull llama2

# Or CodeLlama for code tasks
ollama pull codellama
```

### Step 4: Install Python Dependencies (1 minute)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install langchain langchain-ollama langchain-community
```

## Your First Agent (5 minutes)

**Create file: `my_first_agent.py`**

```python
from langchain_ollama import ChatOllama
from langchain.agents import tool, AgentExecutor, create_react_agent
from langchain import hub

# Step 1: Define tools
@tool
def multiply(x: float, y: float) -> float:
    """Multiply two numbers."""
    return x * y

@tool
def add(x: float, y: float) -> float:
    """Add two numbers."""
    return x + y

# Step 2: Create LLM
llm = ChatOllama(model="mistral", temperature=0.1)

# Step 3: Create agent
tools = [multiply, add]
prompt = hub.pull("hwchase17/react")
agent = create_react_agent(llm, tools, prompt)

executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=5
)

# Step 4: Run!
response = executor.invoke({
    "input": "What is 15 * 3 plus 42?"
})

print(f"\nFinal Answer: {response['output']}")
```

**Run it:**
```bash
python my_first_agent.py
```

## Common Tasks

### Chat with the Model

```python
from langchain_ollama import ChatOllama

llm = ChatOllama(model="mistral")
response = llm.invoke("What is machine learning?")
print(response.content)
```

### Stream Responses (for UX)

```python
from langchain_ollama import ChatOllama

llm = ChatOllama(model="mistral")

print("Response: ", end="", flush=True)
for chunk in llm.stream("Explain quantum computing"):
    print(chunk.content, end="", flush=True)
```

### Create a File Tool

```python
from langchain.agents import tool
import os

@tool
def create_file(name: str, content: str) -> str:
    """Create a file with the given name and content."""
    try:
        with open(name, 'w') as f:
            f.write(content)
        return f"Created {name} with {len(content)} bytes"
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def read_file(name: str) -> str:
    """Read a file and return its content."""
    try:
        with open(name, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return f"File not found: {name}"
```

### Add Memory to Conversations

```python
from langchain_ollama import ChatOllama
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

llm = ChatOllama(model="mistral")
memory = ConversationBufferMemory()

conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

conversation.predict(input="Hi, I'm Alex")
conversation.predict(input="What's my name?")  # Will remember!
```

### Create a Coding Agent

```python
from langchain.agents import tool
from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
import subprocess

@tool
def run_python(code: str) -> str:
    """Run Python code and return output."""
    try:
        result = subprocess.run(
            ["python", "-c", code],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "Error: Timeout"

llm = ChatOllama(model="codellama")
tools = [run_python]

prompt = hub.pull("hwchase17/react")
agent = create_react_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

response = executor.invoke({
    "input": "Write a Python function that calculates factorial and test it with 5"
})
```

## Available Models

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| **mistral** | 7B | ⚡⚡⚡ | ⭐⭐⭐⭐ | General purpose, fast |
| **llama2** | 7B | ⚡⚡ | ⭐⭐⭐⭐⭐ | General purpose, best quality |
| **codellama** | 7B | ⚡⚡ | ⭐⭐⭐⭐ | Code generation/analysis |
| **neural-chat** | 7B | ⚡⚡⚡ | ⭐⭐⭐ | Conversations |
| **orca-mini** | 3B | ⚡⚡⚡⚡ | ⭐⭐⭐ | Very fast, lightweight |

```bash
# Download models
ollama pull mistral
ollama pull llama2
ollama pull codellama
ollama pull neural-chat
ollama pull orca-mini

# List downloaded models
ollama list

# Switch models easily
llm = ChatOllama(model="llama2")  # Just change the model parameter
```

## Troubleshooting

### Server Not Running?
```bash
# Start Ollama
ollama serve

# Check if running
curl http://localhost:11434/api/tags
```

### Model Not Found?
```bash
# List what you have
ollama list

# Download what you need
ollama pull mistral
```

### Agent Hangs?
```python
# Add iteration limit
executor = AgentExecutor(
    agent=agent,
    tools=tools,
    max_iterations=5  # Stop after 5 attempts
)
```

### Out of Memory?
```bash
# Use smaller model
ollama pull orca-mini  # Only 3B

# Or use quantized version
ollama pull llama2:7b  # 7B instead of 13B
```

## Key Concepts

### What is a Tool?
A function that an agent can call to interact with the world:

```python
@tool
def my_tool(input: str) -> str:
    """What the agent will see as description."""
    return "Result"
```

### What is an Agent?
An LLM that:
1. Thinks about what to do
2. Decides which tool to use
3. Calls the tool
4. Gets results
5. Repeats until done

### What is a Prompt?
Instructions that tell the agent HOW to use tools. LangChain provides pre-made prompts:

```python
from langchain import hub

# Popular prompts
prompt = hub.pull("hwchase17/react")  # ReAct agent
prompt = hub.pull("hwchase17/openai-tools")  # Tool use
```

### What is Temperature?
How "creative" the model is (0-1):
- **0** = Always same answer (deterministic)
- **0.5** = Balanced
- **1.0** = Very creative/random

```python
llm = ChatOllama(model="mistral", temperature=0.1)  # For tasks
llm = ChatOllama(model="mistral", temperature=0.7)  # For creativity
```

## Next Steps

1. **Read the full guide**: `OLLAMA_LANGCHAIN_INTEGRATION_GUIDE.md`
2. **Explore examples**: `ollama_langchain_examples.py`
3. **Try the setup script**: `bash setup_ollama_local.sh`
4. **Build your project**: Use these patterns for your use case

## Useful Commands Reference

```bash
# Model management
ollama list                    # List models
ollama pull llama2            # Download model
ollama rm llama2              # Remove model
ollama show llama2            # Show model info

# Server management
ollama serve                  # Start server
pkill ollama                  # Stop server

# Testing
curl http://localhost:11434/api/tags           # Check server
python test_ollama_langchain.py                # Run test
```

## Python Code Snippets

**Simple Q&A:**
```python
from langchain_ollama import ChatOllama

llm = ChatOllama(model="mistral")
answer = llm.invoke("What is AI?")
print(answer.content)
```

**Create Agent Quickly:**
```python
from langchain.agents import tool
from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub

@tool
def my_tool(input: str) -> str:
    return f"Tool result for: {input}"

llm = ChatOllama(model="mistral")
tools = [my_tool]
prompt = hub.pull("hwchase17/react")
agent = create_react_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

result = executor.invoke({"input": "Your task here"})
print(result["output"])
```

**With Memory:**
```python
from langchain_ollama import ChatOllama
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

llm = ChatOllama(model="mistral")
memory = ConversationBufferMemory()
chat = ConversationChain(llm=llm, memory=memory)

chat.predict(input="Hi, I'm John")
chat.predict(input="What's my name?")
```

## Performance Tips

1. **Use smaller models for speed**: mistral, orca-mini
2. **Use larger models for quality**: llama2:13b, llama2:70b
3. **Enable streaming for UX**: `llm.stream()`
4. **Cache results**: Use LLM cache for repeated queries
5. **Batch requests**: Process multiple queries in parallel

## Resources

- **Official Docs**: https://docs.langchain.com
- **Ollama Docs**: https://ollama.ai
- **Models**: https://ollama.ai/library
- **LangChain Community**: https://python.langchain.com

## Quick Reference: Agent Workflow

```
User Input → LLM Thinks → Chooses Tool → Executes Tool →
Gets Result → LLM Thinks More → (repeat or stop) → Final Answer
```

That's it! You now have a local AI agent. Happy building!
