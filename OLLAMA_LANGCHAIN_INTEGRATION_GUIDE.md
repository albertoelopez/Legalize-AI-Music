# Ollama and LangChain Integration Guide

## Overview

This comprehensive guide covers integrating Ollama with LangChain for building AI agents with local LLM inference. It includes setup instructions, practical examples, and best practices for local LLM agent orchestration.

## Table of Contents

1. [Part 1: Ollama Setup with Open Source Models](#part-1-ollama-setup)
2. [Part 2: LangChain Integration](#part-2-langchain-integration)
3. [Part 3: Creating Tools for LangChain Agents](#part-3-tools-creation)
4. [Part 4: Alternative - Claude Code SDK Adaptation](#part-4-claude-code-sdk)
5. [Part 5: Best Practices](#part-5-best-practices)
6. [Sample Code Examples](#sample-code-examples)

---

## Part 1: Ollama Setup with Open Source Models

### 1.1 Installation

**Installation by Operating System:**

**macOS:**
```bash
# Download from https://ollama.ai
# Run the installer, then verify:
ollama --version
```

**Linux (Ubuntu/Debian):**
```bash
# Download and install
curl https://ollama.ai/install.sh | sh

# Or using package manager
sudo apt-get install ollama

# Verify installation
ollama --version
```

**Windows:**
```bash
# Download installer from https://ollama.ai
# Run the .exe installer
# Ollama will run as a service in the background

# In PowerShell or Command Prompt
ollama --version
```

### 1.2 Starting the Ollama Server

The Ollama server runs automatically after installation on port 11434.

```bash
# Start Ollama server (runs in background)
ollama serve

# Verify server is running
curl http://localhost:11434/api/tags
```

### 1.3 Available Models

**Popular Open-Source Models:**

1. **Llama 2 / Llama 3** (Meta)
   - General purpose, 7B-70B parameter variants
   - Good balance of performance and quality
   ```bash
   ollama pull llama2        # 7B model
   ollama pull llama2:13b    # 13B model
   ollama pull llama3        # Latest version
   ollama pull llama3:70b    # Larger variant
   ```

2. **Mistral** (Mistral AI)
   - Fast, efficient, strong performance
   ```bash
   ollama pull mistral       # 7B model
   ollama pull mistral:8x7b  # Mixture of Experts variant
   ```

3. **CodeLlama** (Meta)
   - Specialized for code generation and understanding
   ```bash
   ollama pull codellama
   ollama pull codellama:34b
   ```

4. **Neural Chat** (Intel)
   - Optimized for conversation
   ```bash
   ollama pull neural-chat
   ```

5. **Orca** (Microsoft)
   - Strong reasoning capabilities
   ```bash
   ollama pull orca-mini
   ollama pull orca2
   ```

6. **Dolphin** (Eric Hartford)
   - Instruction-following, function calling
   ```bash
   ollama pull dolphin-mixtral
   ```

### 1.4 Model Management

```bash
# List installed models
ollama list

# Pull a model (downloads to local cache)
ollama pull llama2

# Remove a model (frees disk space)
ollama rm llama2

# Run a model interactively
ollama run llama2

# Show model details
ollama show llama2

# Set custom parameters
ollama run llama2 --temperature 0.7 --top-k 40
```

### 1.5 System Requirements

**Minimum Requirements:**
- 8GB RAM for 7B models
- Modern CPU or GPU
- 10-50GB disk space (depending on model size)

**Recommended for Development:**
- 16GB+ RAM for running multiple models
- NVIDIA GPU (CUDA) or Apple Metal GPU for 3x-10x speedup
- 100GB+ SSD storage

**Hardware-Specific Notes:**
- Linux with NVIDIA GPU: CUDA automatically enabled
- macOS: Metal acceleration automatic for Apple Silicon
- Windows: GPU acceleration available with NVIDIA drivers

### 1.6 Environment Configuration

```bash
# Set custom Ollama host/port
export OLLAMA_HOST=0.0.0.0:11434

# Set models directory
export OLLAMA_MODELS=/path/to/models

# Start with custom settings
OLLAMA_HOST=0.0.0.0:11434 ollama serve
```

### 1.7 API Endpoints

Ollama provides REST API endpoints compatible with OpenAI format:

```bash
# Generate endpoint (completion)
curl http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama2",
    "prompt": "Why is the sky blue?",
    "stream": false
  }'

# Chat endpoint
curl http://localhost:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama2",
    "messages": [
      {"role": "user", "content": "Hello, how are you?"}
    ],
    "stream": false
  }'

# Embeddings endpoint
curl http://localhost:11434/api/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mxbai-embed-large",
    "prompt": "The quick brown fox"
  }'
```

---

## Part 2: LangChain Integration

### 2.1 Installation

```bash
# Install langchain-ollama package
pip install langchain-ollama

# Install other required packages
pip install langchain langchain-community python-dotenv
```

### 2.2 Basic LangChain-Ollama Setup

```python
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Initialize the LLM
llm = ChatOllama(
    model="llama2",
    temperature=0.7,
    base_url="http://localhost:11434"  # Default, can be customized
)

# Create a simple chain
template = "You are a helpful assistant. Answer this: {question}"
prompt = PromptTemplate(template=template, input_variables=["question"])

chain = LLMChain(llm=llm, prompt=prompt)

# Use the chain
response = chain.run(question="What is machine learning?")
print(response)
```

### 2.3 LangChain Components

**ChatOllama** (for chat models):
```python
from langchain_ollama import ChatOllama
from langchain.schema import HumanMessage

llm = ChatOllama(model="llama2")

# Single message
response = llm.invoke("Hello!")

# Multiple messages with history
messages = [
    HumanMessage("Hi, what's your name?"),
    HumanMessage("Can you help me with Python?")
]
response = llm.invoke(messages)
```

**OllamaEmbeddings** (for semantic search):
```python
from langchain_ollama import OllamaEmbeddings

embeddings = OllamaEmbeddings(model="mxbai-embed-large")

# Generate embeddings
text = "The quick brown fox"
embedding = embeddings.embed_query(text)
print(len(embedding))  # 1024 dimensions

# Batch embeddings
texts = ["text1", "text2", "text3"]
embeddings_list = embeddings.embed_documents(texts)
```

**OllamaLLM** (legacy text completion):
```python
from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama2")
response = llm.invoke("Complete this: The meaning of life is")
```

### 2.4 Streaming Responses

For real-time response streaming:

```python
from langchain_ollama import ChatOllama

llm = ChatOllama(model="llama2", temperature=0.7)

# Stream responses
for chunk in llm.stream("Explain quantum computing in simple terms"):
    print(chunk.content, end="", flush=True)
```

### 2.5 Memory and Conversation

```python
from langchain_ollama import ChatOllama
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

llm = ChatOllama(model="llama2")

# Create conversation with memory
memory = ConversationBufferMemory()
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

# Multi-turn conversation
conversation.predict(input="Hi, I'm studying AI")
conversation.predict(input="What's the difference between ML and DL?")
conversation.predict(input="Can you give me some examples?")  # Will remember context
```

---

## Part 3: Creating Tools for LangChain Agents

### 3.1 Tool Creation Methods

**Method 1: Using @tool Decorator (Simplest)**

```python
from langchain.agents import tool
from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub

# Define tools with decorator
@tool
def calculate_circumference(radius: float) -> float:
    """Calculate the circumference of a circle given the radius."""
    import math
    return 2 * math.pi * radius

@tool
def search_wikipedia(query: str) -> str:
    """Search Wikipedia for information about a topic."""
    # In production, use actual Wikipedia API
    return f"Search results for: {query}"

@tool
def get_current_weather(location: str) -> str:
    """Get current weather for a location."""
    # Mock implementation - replace with real API
    return f"Weather in {location}: Sunny, 72°F"

# Create agent with tools
llm = ChatOllama(model="mistral")
tools = [calculate_circumference, search_wikipedia, get_current_weather]

# Get ReAct prompt
prompt = hub.pull("hwchase17/react")

# Create and execute agent
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=5
)

# Use the agent
response = agent_executor.invoke({
    "input": "What's the circumference of a circle with radius 5? And tell me about Eiffel Tower."
})
```

**Method 2: Using BaseTool Class (Advanced)**

```python
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional

class CalculatorInput(BaseModel):
    """Input for calculator tool."""
    operation: str = Field(
        description="The operation to perform: add, subtract, multiply, divide"
    )
    x: float = Field(description="First number")
    y: float = Field(description="Second number")

class CalculatorTool(BaseTool):
    """A calculator tool for mathematical operations."""
    name = "calculator"
    description = """
    A calculator tool that performs basic mathematical operations.
    Use this tool when you need to perform calculations.
    """
    args_schema = CalculatorInput

    def _run(self, operation: str, x: float, y: float) -> str:
        """Execute the calculation."""
        try:
            if operation == "add":
                result = x + y
            elif operation == "subtract":
                result = x - y
            elif operation == "multiply":
                result = x * y
            elif operation == "divide":
                if y == 0:
                    return "Error: Division by zero"
                result = x / y
            else:
                return f"Unknown operation: {operation}"

            return f"{x} {operation} {y} = {result}"
        except Exception as e:
            return f"Error: {str(e)}"

    async def _arun(self, operation: str, x: float, y: float) -> str:
        """Async implementation."""
        return self._run(operation, x, y)

# Use the tool
calculator = CalculatorTool()
result = calculator.run({"operation": "add", "x": 10, "y": 5})
print(result)  # Output: 10 add 5 = 15
```

**Method 3: Using Tool.from_function()**

```python
from langchain.tools import Tool

def multiply(x: float, y: float) -> float:
    """Multiply two numbers."""
    return x * y

def divide(x: float, y: float) -> str:
    """Divide two numbers."""
    if y == 0:
        return "Error: Cannot divide by zero"
    return f"{x} / {y} = {x / y}"

# Create tools from functions
multiply_tool = Tool.from_function(
    func=multiply,
    name="Multiply",
    description="Multiply two numbers together"
)

divide_tool = Tool.from_function(
    func=divide,
    name="Divide",
    description="Divide one number by another"
)

tools = [multiply_tool, divide_tool]
```

### 3.2 Complete Agent with Tools Example

```python
from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_react_agent
from langchain.agents import tool
from langchain import hub

# Define multiple tools
@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression."""
    try:
        result = eval(expression)
        return f"Result of {expression} is {result}"
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def date_tool() -> str:
    """Get current date and time."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool
def web_search_mock(query: str) -> str:
    """Search the web for information (mock implementation)."""
    return f"Search results for '{query}': [Mock result 1], [Mock result 2]"

# Setup agent
llm = ChatOllama(
    model="mistral",
    temperature=0.7
)

tools = [calculator, date_tool, web_search_mock]
prompt = hub.pull("hwchase17/react")

agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=10
)

# Test the agent
queries = [
    "What is 25 * 4?",
    "What's today's date?",
    "Search for information about quantum computing"
]

for query in queries:
    print(f"\nQuery: {query}")
    result = agent_executor.invoke({"input": query})
    print(f"Answer: {result['output']}")
```

### 3.3 Tool Best Practices

```python
from langchain.agents import tool

# GOOD: Clear, descriptive naming and documentation
@tool
def fetch_user_data(user_id: int) -> dict:
    """
    Fetch user data from the database.

    Args:
        user_id: The unique identifier of the user

    Returns:
        Dictionary containing user information
    """
    # Implementation
    pass

# BAD: Vague naming and poor description
@tool
def get_data(x):
    """Get something."""
    pass

# GOOD: Input validation
@tool
def process_payment(amount: float, currency: str) -> str:
    """Process a payment transaction."""
    if amount <= 0:
        return "Error: Amount must be positive"
    if currency not in ["USD", "EUR", "GBP"]:
        return f"Error: Unsupported currency {currency}"

    # Process payment
    return f"Processed {amount} {currency}"

# GOOD: Error handling
@tool
def call_api(endpoint: str) -> str:
    """Call an external API."""
    try:
        import requests
        response = requests.get(f"https://api.example.com{endpoint}", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return f"API Error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"
```

---

## Part 4: Alternative - Claude Code SDK Adaptation

### 4.1 Why Direct Integration Isn't Possible

Claude Code is a proprietary tool from Anthropic that uses their Anthropic API. Direct integration with local LLMs isn't supported. However, there are adaptation strategies:

### 4.2 Using API Translation Proxies

**Strategy 1: LiteLLM Proxy**

LiteLLM acts as a bridge between Anthropic API format (expected by Claude Code) and OpenAI-compatible endpoints (provided by Ollama).

```bash
# Install LiteLLM
pip install litellm

# Create proxy configuration
cat > litellm_config.yaml << EOF
model_list:
  - model_name: "ollama/llama2"
    litellm_params:
      model: "ollama/llama2"
      api_base: "http://localhost:11434"

  - model_name: "ollama/mistral"
    litellm_params:
      model: "ollama/mistral"
      api_base: "http://localhost:11434"

router_settings:
  timeout: 600
EOF

# Start proxy server
litellm --config litellm_config.yaml --port 8000
```

**Using with applications:**

```python
import anthropic

# Point to local proxy instead of Anthropic API
client = anthropic.Anthropic(
    api_key="sk-local",  # Dummy key for local server
    base_url="http://localhost:8000"  # Your LiteLLM proxy
)

response = client.messages.create(
    model="ollama/mistral",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)
print(response.content[0].text)
```

**Strategy 2: OpenCode (Open-Source Alternative)**

OpenCode is an open-source alternative that natively supports local LLMs:

```bash
# Install OpenCode
pip install opencode

# Configure for local Ollama
export OPENCODE_API_KEY="local"
export OPENCODE_API_BASE="http://localhost:11434"
export OPENCODE_MODEL="llama2"

# Run OpenCode
opencode --model llama2 --api-base http://localhost:11434
```

### 4.3 Building a Custom Claude-Like Agent with Ollama

Instead of adapting Claude Code directly, build a custom agent:

```python
from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_react_agent
from langchain.agents import tool
from langchain import hub
import subprocess
import os

@tool
def execute_python(code: str) -> str:
    """Execute Python code safely in a sandboxed environment."""
    try:
        # Create temporary file
        with open("/tmp/temp_code.py", "w") as f:
            f.write(code)

        # Execute with timeout
        result = subprocess.run(
            ["python", "/tmp/temp_code.py"],
            capture_output=True,
            text=True,
            timeout=10
        )

        return f"Output:\n{result.stdout}\nErrors:\n{result.stderr}"
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out"
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def read_file(filepath: str) -> str:
    """Read contents of a file."""
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found - {filepath}"
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def write_file(filepath: str, content: str) -> str:
    """Write content to a file."""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
        return f"Successfully wrote to {filepath}"
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def list_files(directory: str = ".") -> str:
    """List files in a directory."""
    try:
        files = os.listdir(directory)
        return "\n".join(files)
    except Exception as e:
        return f"Error: {str(e)}"

# Create coding agent
llm = ChatOllama(model="codellama", temperature=0.1)
tools = [execute_python, read_file, write_file, list_files]

prompt = hub.pull("hwchase17/react")
agent = create_react_agent(llm, tools, prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=15
)

# Use the agent for code tasks
response = agent_executor.invoke({
    "input": "Create a Python script that calculates fibonacci numbers up to 10"
})
```

---

## Part 5: Best Practices for Local LLM Agent Orchestration

### 5.1 Resource Management

```python
from langchain_ollama import ChatOllama
import psutil
import time

class ResourceMonitoredLLM:
    """LLM wrapper that monitors system resources."""

    def __init__(self, model: str):
        self.llm = ChatOllama(model=model)
        self.max_memory_percent = 80

    def check_resources(self):
        """Check if system has sufficient resources."""
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=1)

        if memory.percent > self.max_memory_percent:
            raise RuntimeError(f"Memory usage too high: {memory.percent}%")

        return {
            "memory_percent": memory.percent,
            "cpu_percent": cpu,
            "available_memory_gb": memory.available / (1024**3)
        }

    def invoke(self, prompt: str, max_retries: int = 3):
        """Invoke with resource monitoring and retry logic."""
        for attempt in range(max_retries):
            try:
                self.check_resources()
                return self.llm.invoke(prompt)
            except RuntimeError as e:
                print(f"Resource check failed: {e}")
                if attempt < max_retries - 1:
                    print(f"Waiting 10 seconds before retry {attempt + 2}/{max_retries}...")
                    time.sleep(10)
                else:
                    raise
```

### 5.2 Model Quantization

Using quantized models saves memory while maintaining performance:

```bash
# Available model variants (quantization levels)
ollama pull llama2          # Default (usually 4-bit quantization)
ollama pull llama2:7b       # 7B parameter variant
ollama pull llama2:70b      # 70B parameter variant

# Memory usage comparison:
# - Full precision (fp32): ~28GB for 7B model
# - 8-bit quantized: ~7GB for 7B model
# - 4-bit quantized: ~4GB for 7B model
```

### 5.3 Streaming for Better UX

```python
from langchain_ollama import ChatOllama

llm = ChatOllama(model="llama2")

# Display streaming responses in real-time
print("Response: ", end="", flush=True)
for chunk in llm.stream("Explain machine learning in 3 sentences"):
    print(chunk.content, end="", flush=True)
print()  # New line at end
```

### 5.4 Caching and Optimization

```python
from langchain.cache import SQLiteCache
from langchain.globals import set_llm_cache
from langchain_ollama import ChatOllama

# Enable LLM response caching
set_llm_cache(SQLiteCache(database_path=".langchain.db"))

llm = ChatOllama(model="llama2")

# First call - hits Ollama
response1 = llm.invoke("What is Python?")

# Second identical call - returns from cache (instant)
response2 = llm.invoke("What is Python?")

# Different query - hits Ollama again
response3 = llm.invoke("What is JavaScript?")
```

### 5.5 Model Validation on Initialization

```python
from langchain_ollama import ChatOllama
import requests

def validate_ollama_setup(model: str, api_base: str = "http://localhost:11434"):
    """Validate that Ollama server and model are available."""
    try:
        # Check server is running
        response = requests.get(f"{api_base}/api/tags", timeout=5)
        if response.status_code != 200:
            raise ConnectionError("Ollama server not responding")

        # Check model is available
        models = response.json().get("models", [])
        model_names = [m["name"].split(":")[0] for m in models]

        if model not in model_names:
            raise ValueError(f"Model '{model}' not found. Available: {model_names}")

        print(f"✓ Ollama server is running")
        print(f"✓ Model '{model}' is available")
        return True

    except ConnectionError as e:
        print(f"✗ Connection error: {e}")
        print(f"  Make sure Ollama is running: ollama serve")
        return False
    except ValueError as e:
        print(f"✗ {e}")
        print(f"  Download model: ollama pull {model}")
        return False

# Initialize LLM only if validation passes
if validate_ollama_setup("llama2"):
    llm = ChatOllama(model="llama2")
else:
    raise RuntimeError("Ollama setup validation failed")
```

### 5.6 Batch Processing

```python
from langchain_ollama import ChatOllama
from concurrent.futures import ThreadPoolExecutor
from typing import List

def batch_process(queries: List[str], model: str = "llama2", max_workers: int = 2):
    """Process multiple queries in parallel batches."""
    llm = ChatOllama(model=model)

    def process_query(query: str) -> tuple:
        response = llm.invoke(query)
        return (query, response.content)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_query, queries))

    return results

# Example usage
queries = [
    "What is AI?",
    "What is ML?",
    "What is DL?",
    "What is NLP?"
]

results = batch_process(queries, model="mistral", max_workers=2)
for query, response in results:
    print(f"Q: {query}")
    print(f"A: {response}\n")
```

### 5.7 Error Handling and Retries

```python
from langchain_ollama import ChatOllama
from tenacity import retry, stop_after_attempt, wait_exponential

class RobustLLMAgent:
    """LLM agent with robust error handling."""

    def __init__(self, model: str):
        self.llm = ChatOllama(model=model, temperature=0.7)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def invoke_with_retry(self, prompt: str) -> str:
        """Invoke with automatic retry on failure."""
        return self.llm.invoke(prompt).content

    def invoke_with_fallback(self, prompt: str, fallback_model: str = "mistral") -> str:
        """Invoke with fallback to another model."""
        try:
            return self.llm.invoke(prompt).content
        except Exception as e:
            print(f"Failed with primary model: {e}")
            print(f"Falling back to {fallback_model}...")
            fallback_llm = ChatOllama(model=fallback_model)
            return fallback_llm.invoke(prompt).content

# Usage
agent = RobustLLMAgent("llama2")
result = agent.invoke_with_retry("Tell me about quantum computing")
result = agent.invoke_with_fallback("Complex query here")
```

### 5.8 Security Considerations

```python
import os
from functools import wraps
from langchain_ollama import ChatOllama

def secure_llm_access(func):
    """Decorator to enforce security best practices."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Validate API endpoint is local
        api_base = kwargs.get('api_base', 'http://localhost:11434')
        if not api_base.startswith(('http://localhost', 'http://127.0.0.1')):
            raise SecurityError("Only local Ollama instances are allowed")

        # Validate authentication if needed
        api_key = os.getenv('OLLAMA_API_KEY')
        if api_key and not api_key.startswith('sk-'):
            print("Warning: API key doesn't follow expected format")

        return func(*args, **kwargs)

    return wrapper

@secure_llm_access
def get_secure_llm(model: str, api_base: str = "http://localhost:11434"):
    """Get LLM with security validation."""
    return ChatOllama(model=model, base_url=api_base)

class SecurityError(Exception):
    """Security validation error."""
    pass

# Usage
llm = get_secure_llm("llama2")  # OK
# llm = get_secure_llm("llama2", api_base="https://external-api.com")  # Raises error
```

### 5.9 Monitoring and Logging

```python
import logging
from datetime import datetime
from langchain_ollama import ChatOllama

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ollama_agent.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class MonitoredLLMAgent:
    """Agent with comprehensive logging."""

    def __init__(self, model: str):
        self.llm = ChatOllama(model=model)
        self.logger = logger

    def invoke(self, prompt: str, **kwargs) -> str:
        """Invoke with logging."""
        start_time = datetime.now()
        self.logger.info(f"Starting inference with prompt: {prompt[:100]}...")

        try:
            response = self.llm.invoke(prompt, **kwargs)
            duration = (datetime.now() - start_time).total_seconds()

            self.logger.info(
                f"Inference completed. Duration: {duration:.2f}s, "
                f"Response length: {len(response.content)} chars"
            )

            return response.content

        except Exception as e:
            self.logger.error(f"Inference failed: {str(e)}", exc_info=True)
            raise

# Usage
agent = MonitoredLLMAgent("llama2")
response = agent.invoke("What is AI?")
```

---

## Sample Code Examples

### Complete RAG Application with Ollama and LangChain

```python
"""
Complete RAG (Retrieval-Augmented Generation) application using Ollama and LangChain.
This example builds a Q&A system over local documents.
"""

from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.document_loaders import TextLoader
import os

# 1. Load documents
documents = []
for file in os.listdir("./documents"):
    if file.endswith(".txt"):
        loader = TextLoader(f"./documents/{file}")
        documents.extend(loader.load())

# 2. Split documents into chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
chunks = splitter.split_documents(documents)

# 3. Create embeddings and vector store
embeddings = OllamaEmbeddings(model="mxbai-embed-large")
vectorstore = FAISS.from_documents(chunks, embeddings)

# 4. Create RAG chain
llm = ChatOllama(model="llama3", temperature=0.1)
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3})
)

# 5. Query the system
query = "What are the main topics discussed?"
response = qa_chain.run(query)
print(f"Question: {query}")
print(f"Answer: {response}")
```

### Multi-Agent System with Tool Orchestration

```python
"""
Multi-agent system where different agents handle different domains.
"""

from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_react_agent, tool
from langchain import hub

@tool
def research_agent(topic: str) -> str:
    """Research a topic and provide information."""
    return f"Research on {topic}: [comprehensive findings]"

@tool
def code_analysis_agent(code: str) -> str:
    """Analyze code and provide feedback."""
    return f"Code analysis: [performance metrics, security issues]"

@tool
def writing_agent(topic: str, style: str) -> str:
    """Generate written content."""
    return f"Written content about {topic} in {style} style: [generated text]"

class MultiAgentOrchestrator:
    def __init__(self):
        self.research_llm = ChatOllama(model="mistral")
        self.code_llm = ChatOllama(model="codellama")
        self.writing_llm = ChatOllama(model="llama2")

        self.tools = [research_agent, code_analysis_agent, writing_agent]
        self.prompt = hub.pull("hwchase17/react")

    def route_task(self, task: str, content: str) -> str:
        """Route task to appropriate agent."""

        if "research" in task.lower():
            agent = create_react_agent(self.research_llm, self.tools, self.prompt)
        elif "code" in task.lower():
            agent = create_react_agent(self.code_llm, self.tools, self.prompt)
        else:
            agent = create_react_agent(self.writing_llm, self.tools, self.prompt)

        executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)
        return executor.invoke({"input": content})["output"]

# Usage
orchestrator = MultiAgentOrchestrator()
result = orchestrator.route_task("research", "Explain quantum computing")
```

### Real-time Streaming Chat Application

```python
"""
Interactive streaming chat application with Ollama backend.
"""

from langchain_ollama import ChatOllama
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
import sys

class StreamingChatApp:
    def __init__(self, model: str = "llama2"):
        self.llm = ChatOllama(
            model=model,
            temperature=0.7,
            top_k=40,
            top_p=0.9
        )
        self.memory = ConversationBufferMemory()
        self.chain = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            verbose=False
        )

    def stream_response(self, user_input: str):
        """Stream response character by character."""
        print(f"User: {user_input}\nAssistant: ", end="", flush=True)

        # Use streaming
        for chunk in self.llm.stream(user_input):
            print(chunk.content, end="", flush=True)

        print()  # New line
        self.memory.chat_memory.add_user_message(user_input)

    def run_interactive(self):
        """Run interactive chat loop."""
        print("Chat with Ollama (type 'exit' to quit)")
        print("-" * 50)

        while True:
            try:
                user_input = input("You: ").strip()

                if user_input.lower() == 'exit':
                    print("Goodbye!")
                    break

                if not user_input:
                    continue

                self.stream_response(user_input)

            except KeyboardInterrupt:
                print("\nInterrupted. Goodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")

# Run the app
if __name__ == "__main__":
    app = StreamingChatApp(model="mistral")
    app.run_interactive()
```

---

## Additional Resources

### Official Documentation
- [LangChain Documentation](https://docs.langchain.com/oss/python/langchain/overview)
- [LangChain Ollama Integration](https://python.langchain.com/docs/integrations/llms/ollama)
- [Ollama Official Website](https://ollama.ai)

### Community Tools
- [LangGraph - For agent orchestration](https://langchain-ai.github.io/langgraph/)
- [LiteLLM - API proxy for local models](https://github.com/BerriAI/litellm)
- [OpenCode - Open-source Claude alternative](https://github.com/hackerspace-team/opencode)

### Model Downloads
- [Ollama Model Library](https://ollama.ai/library)
- [HuggingFace Model Hub](https://huggingface.co/models)

---

## Troubleshooting

### Ollama Server Not Running
```bash
# Check if server is running
curl http://localhost:11434/api/tags

# If not running, start it
ollama serve

# On macOS, check system preferences for Ollama
# On Linux, check systemctl status
systemctl status ollama
```

### Model Not Found
```bash
# List installed models
ollama list

# Pull the missing model
ollama pull llama2

# Check available models
curl http://localhost:11434/api/tags
```

### Out of Memory
```bash
# Use a smaller model
ollama pull llama2:7b  # Instead of 13b or 70b

# Check available memory
free -h  # Linux
vm_stat  # macOS
```

### Slow Performance
```bash
# Enable GPU acceleration if available
# NVIDIA: Ensure CUDA is installed
# AMD: Use ROCm
# Apple: Metal is automatic

# Use quantized models (4-bit preferred)
ollama pull mistral  # Usually 4-bit by default

# Monitor resources while running
watch nvidia-smi  # For NVIDIA GPUs
```

