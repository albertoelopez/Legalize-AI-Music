"""
Practical Python examples for Ollama and LangChain integration.
These examples demonstrate common use cases and patterns.
"""

# ============================================================================
# Example 1: Basic Chat with Ollama
# ============================================================================

def example_basic_chat():
    """Simple chat with Ollama backend."""
    from langchain_ollama import ChatOllama

    llm = ChatOllama(
        model="llama2",
        temperature=0.7,
        base_url="http://localhost:11434"
    )

    # Single message
    response = llm.invoke("What is the capital of France?")
    print(f"Response: {response.content}")

    # Multiple messages (conversation)
    from langchain.schema import HumanMessage, AIMessage

    messages = [
        HumanMessage("Hi, what's your name?"),
        AIMessage("I'm an AI assistant."),
        HumanMessage("What can you help me with?")
    ]

    response = llm.invoke(messages)
    print(f"Response: {response.content}")


# ============================================================================
# Example 2: Streaming Responses
# ============================================================================

def example_streaming():
    """Stream responses character by character."""
    from langchain_ollama import ChatOllama

    llm = ChatOllama(model="mistral", temperature=0.7)

    print("Streaming response: ", end="", flush=True)
    for chunk in llm.stream("Explain quantum entanglement in simple terms"):
        print(chunk.content, end="", flush=True)
    print()  # New line


# ============================================================================
# Example 3: Creating Custom Tools
# ============================================================================

def example_custom_tools():
    """Create and use custom tools with agents."""
    from langchain.agents import tool
    from langchain_ollama import ChatOllama
    from langchain.agents import AgentExecutor, create_react_agent
    from langchain import hub

    # Define tools
    @tool
    def weather(location: str) -> str:
        """Get weather for a location (mock)."""
        return f"Weather in {location}: Sunny, 72°F"

    @tool
    def calculator(expression: str) -> str:
        """Evaluate math expressions."""
        try:
            result = eval(expression)
            return f"{expression} = {result}"
        except:
            return f"Error evaluating: {expression}"

    @tool
    def web_search(query: str) -> str:
        """Search the web (mock)."""
        return f"Search results for '{query}': [Results...]"

    # Setup agent
    llm = ChatOllama(model="mistral")
    tools = [weather, calculator, web_search]

    prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(llm, tools, prompt)

    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=5
    )

    # Use agent
    result = executor.invoke({"input": "What's the weather in NYC? And what's 25 * 4?"})
    print(f"Answer: {result['output']}")


# ============================================================================
# Example 4: Tool with Pydantic Schema
# ============================================================================

def example_structured_tool():
    """Tool with structured input schema."""
    from langchain.tools import BaseTool
    from pydantic import BaseModel, Field

    class CalculatorInput(BaseModel):
        """Input for calculator."""
        operation: str = Field(description="add, subtract, multiply, or divide")
        x: float = Field(description="First number")
        y: float = Field(description="Second number")

    class CalculatorTool(BaseTool):
        """A calculator tool."""
        name = "calculator"
        description = "Perform basic math operations"
        args_schema = CalculatorInput

        def _run(self, operation: str, x: float, y: float) -> str:
            if operation == "add":
                return str(x + y)
            elif operation == "subtract":
                return str(x - y)
            elif operation == "multiply":
                return str(x * y)
            elif operation == "divide":
                return str(x / y) if y != 0 else "Error: Division by zero"
            return "Unknown operation"

        async def _arun(self, operation: str, x: float, y: float) -> str:
            return self._run(operation, x, y)

    # Use the tool
    tool = CalculatorTool()
    print(tool.run({"operation": "add", "x": 10, "y": 5}))


# ============================================================================
# Example 5: Conversation with Memory
# ============================================================================

def example_conversation_memory():
    """Multi-turn conversation with memory."""
    from langchain_ollama import ChatOllama
    from langchain.memory import ConversationBufferMemory
    from langchain.chains import ConversationChain

    llm = ChatOllama(model="llama2")
    memory = ConversationBufferMemory()

    conversation = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=True
    )

    # Multi-turn conversation
    conversation.predict(input="Hi! My name is Alice")
    conversation.predict(input="What did I just tell you?")
    conversation.predict(input="How many letters in my name?")


# ============================================================================
# Example 6: Embeddings and Semantic Search
# ============================================================================

def example_embeddings():
    """Generate embeddings and perform similarity search."""
    from langchain_ollama import OllamaEmbeddings
    from langchain.vectorstores import FAISS
    from langchain.schema import Document

    embeddings = OllamaEmbeddings(model="mxbai-embed-large")

    # Create documents
    docs = [
        Document(page_content="Python is a programming language"),
        Document(page_content="JavaScript runs in web browsers"),
        Document(page_content="Machine learning models learn from data"),
        Document(page_content="Deep learning uses neural networks"),
    ]

    # Create vector store
    vectorstore = FAISS.from_documents(docs, embeddings)

    # Search
    results = vectorstore.similarity_search("programming languages", k=2)
    for doc in results:
        print(f"Result: {doc.page_content}")


# ============================================================================
# Example 7: ReAct Agent
# ============================================================================

def example_react_agent():
    """Create a ReAct agent that reasons and acts."""
    from langchain.agents import tool
    from langchain_ollama import ChatOllama
    from langchain.agents import AgentExecutor, create_react_agent
    from langchain import hub
    from datetime import datetime

    @tool
    def get_date() -> str:
        """Get current date."""
        return datetime.now().strftime("%Y-%m-%d")

    @tool
    def get_time() -> str:
        """Get current time."""
        return datetime.now().strftime("%H:%M:%S")

    @tool
    def todo_manager(action: str, task: str = "") -> str:
        """Manage tasks (mock)."""
        if action == "add":
            return f"Added task: {task}"
        elif action == "list":
            return "1. Complete project\n2. Review code\n3. Write docs"
        return "Unknown action"

    llm = ChatOllama(model="mistral")
    tools = [get_date, get_time, todo_manager]

    prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(llm, tools, prompt)

    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=10
    )

    result = executor.invoke({
        "input": "What time is it? And tell me my todos. Then add 'Learn Ollama' as a task."
    })
    print(f"Result: {result['output']}")


# ============================================================================
# Example 8: Error Handling and Retries
# ============================================================================

def example_error_handling():
    """Handle errors and implement retries."""
    from langchain_ollama import ChatOllama
    from tenacity import retry, stop_after_attempt, wait_exponential

    class RobustOllama:
        def __init__(self, model: str):
            self.llm = ChatOllama(model=model)

        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=2, max=10)
        )
        def invoke_with_retry(self, prompt: str):
            """Invoke with automatic retry on failure."""
            return self.llm.invoke(prompt).content

        def invoke_with_fallback(self, prompt: str, fallback_model: str = "mistral"):
            """Invoke with fallback model."""
            try:
                return self.llm.invoke(prompt).content
            except Exception as e:
                print(f"Primary model failed: {e}, trying fallback...")
                fallback = ChatOllama(model=fallback_model)
                return fallback.invoke(prompt).content

    agent = RobustOllama("llama2")
    result = agent.invoke_with_retry("Hello!")
    print(f"Result: {result}")


# ============================================================================
# Example 9: RAG with Vector Store
# ============================================================================

def example_rag():
    """Retrieval-Augmented Generation example."""
    from langchain_ollama import ChatOllama, OllamaEmbeddings
    from langchain.vectorstores import FAISS
    from langchain.chains import RetrievalQA
    from langchain.schema import Document

    # Create sample documents
    docs = [
        Document(page_content="Python 3.11 introduces exception groups"),
        Document(page_content="Machine learning requires large datasets"),
        Document(page_content="Vector databases store embeddings"),
        Document(page_content="LangChain is a framework for LLM apps"),
    ]

    # Create embeddings and vector store
    embeddings = OllamaEmbeddings(model="mxbai-embed-large")
    vectorstore = FAISS.from_documents(docs, embeddings)

    # Create RAG chain
    llm = ChatOllama(model="llama2")
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 2})
    )

    # Query
    response = qa_chain.run("What is LangChain?")
    print(f"Answer: {response}")


# ============================================================================
# Example 10: Code Generation Agent
# ============================================================================

def example_code_generation():
    """Agent that generates and executes code."""
    from langchain.agents import tool
    from langchain_ollama import ChatOllama
    from langchain.agents import AgentExecutor, create_react_agent
    from langchain import hub
    import subprocess

    @tool
    def execute_python(code: str) -> str:
        """Execute Python code safely."""
        try:
            with open("/tmp/temp.py", "w") as f:
                f.write(code)

            result = subprocess.run(
                ["python", "/tmp/temp.py"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return f"Output: {result.stdout}\nErrors: {result.stderr}"
        except subprocess.TimeoutExpired:
            return "Error: Execution timed out"
        except Exception as e:
            return f"Error: {str(e)}"

    llm = ChatOllama(model="codellama")
    tools = [execute_python]

    prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(llm, tools, prompt)

    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=5
    )

    result = executor.invoke({
        "input": "Write Python code to calculate fibonacci numbers up to 10 and run it"
    })
    print(f"Result: {result['output']}")


# ============================================================================
# Example 11: Batch Processing
# ============================================================================

def example_batch_processing():
    """Process multiple queries in parallel."""
    from langchain_ollama import ChatOllama
    from concurrent.futures import ThreadPoolExecutor

    llm = ChatOllama(model="mistral")

    queries = [
        "What is AI?",
        "What is ML?",
        "What is DL?",
    ]

    def process_query(query: str):
        response = llm.invoke(query)
        return (query, response.content[:100])

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(process_query, queries))

    for query, answer in results:
        print(f"Q: {query}")
        print(f"A: {answer}...\n")


# ============================================================================
# Example 12: Monitoring and Logging
# ============================================================================

def example_monitoring():
    """Monitor LLM performance and log results."""
    from langchain_ollama import ChatOllama
    from datetime import datetime
    import json

    class MonitoredLLM:
        def __init__(self, model: str):
            self.llm = ChatOllama(model=model)
            self.logs = []

        def invoke(self, prompt: str) -> str:
            start = datetime.now()
            response = self.llm.invoke(prompt)
            duration = (datetime.now() - start).total_seconds()

            self.logs.append({
                "timestamp": datetime.now().isoformat(),
                "prompt": prompt[:50],
                "duration": duration,
                "response_length": len(response.content)
            })

            return response.content

        def print_stats(self):
            if not self.logs:
                return

            total_duration = sum(log["duration"] for log in self.logs)
            avg_duration = total_duration / len(self.logs)

            print(f"Total queries: {len(self.logs)}")
            print(f"Average duration: {avg_duration:.2f}s")
            print(f"Total time: {total_duration:.2f}s")

    agent = MonitoredLLM("llama2")

    for i in range(3):
        agent.invoke(f"Question {i+1}: Tell me something interesting about AI")

    agent.print_stats()


# ============================================================================
# Main execution
# ============================================================================

if __name__ == "__main__":
    print("Ollama and LangChain Integration Examples")
    print("=" * 50)

    # Run examples (uncomment to execute)
    # example_basic_chat()
    # example_streaming()
    # example_custom_tools()
    # example_structured_tool()
    # example_conversation_memory()
    # example_embeddings()
    # example_react_agent()
    # example_error_handling()
    # example_rag()
    # example_code_generation()
    # example_batch_processing()
    # example_monitoring()

    print("\nNote: Ensure Ollama is running before executing examples")
    print("Start Ollama: ollama serve")
    print("Pull models: ollama pull llama2 mistral codellama")
