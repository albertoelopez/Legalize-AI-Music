# Production Deployment Guide: Ollama + LangChain Agents

## Overview

This guide covers deploying Ollama and LangChain agents to production environments with proper security, monitoring, and scalability.

## Table of Contents

1. [Architecture Design](#architecture)
2. [Security Hardening](#security)
3. [Performance Optimization](#performance)
4. [Monitoring and Logging](#monitoring)
5. [Scaling Strategies](#scaling)
6. [Docker Deployment](#docker)
7. [Kubernetes Deployment](#kubernetes)
8. [Best Practices Checklist](#checklist)

---

## Architecture Design {#architecture}

### Recommended Production Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway / LB                         │
└────────────┬────────────────────────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
┌───▼──────┐    ┌──────▼───┐
│ Agent    │    │ Agent    │
│ Service  │    │ Service  │
│ (Flask)  │    │ (FastAPI)│
└───┬──────┘    └──────┬───┘
    │                 │
    │    ┌────────────┴────────────┐
    │    │                         │
    │    │  Ollama Model Server    │
    │    │  (GPU Accelerated)      │
    │    │                         │
    │    └────────────┬────────────┘
    │
    ├──────────────────────┐
    │                      │
┌───▼──────┐        ┌──────▼───┐
│ Cache    │        │ Database  │
│(Redis)   │        │(PostgreSQL│
└──────────┘        └───────────┘

┌──────────────────────────────────┐
│     Monitoring & Logging          │
│ (Prometheus, ELK, Jaeger)        │
└──────────────────────────────────┘
```

### Components Breakdown

**API Gateway:**
- Load balance requests
- Rate limiting
- Authentication
- Request validation

**Agent Services:**
- Stateless, horizontally scalable
- Handle user requests
- Coordinate tools
- Cache frequently used results

**Ollama Model Server:**
- Single shared instance (GPU)
- Model management
- Inference engine
- Response caching

**Supporting Services:**
- Redis: Query/response caching
- PostgreSQL: Persistent data storage
- Monitoring: Health and performance tracking

---

## Security Hardening {#security}

### 1. API Authentication and Authorization

```python
# secure_agent_api.py

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from typing import Optional
import jwt
from datetime import datetime, timedelta

app = FastAPI()
security = HTTPBearer()

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"

class TokenData:
    def __init__(self, user_id: str, role: str):
        self.user_id = user_id
        self.role = role

def verify_token(credentials: HTTPAuthCredentials = Depends(security)):
    """Verify JWT token."""
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        user_id: str = payload.get("user_id")
        role: str = payload.get("role", "user")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        return TokenData(user_id, role)

    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )

@app.post("/agent/chat")
async def chat(
    message: str,
    current_user: TokenData = Depends(verify_token)
):
    """Chat endpoint with authentication."""
    if current_user.role not in ["user", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )

    # Process request
    response = process_chat(message, current_user.user_id)
    return {"response": response, "user_id": current_user.user_id}
```

### 2. Input Validation and Sanitization

```python
from pydantic import BaseModel, validator, Field
from typing import Optional

class AgentRequest(BaseModel):
    """Validated agent request."""

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User prompt"
    )

    model: str = Field(
        default="mistral",
        pattern="^[a-z0-9-]+$",  # Only allow safe characters
        description="Model to use"
    )

    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Model temperature"
    )

    timeout: int = Field(
        default=30,
        ge=5,
        le=300,
        description="Request timeout in seconds"
    )

    @validator("prompt")
    def validate_prompt(cls, v):
        """Validate prompt content."""
        # Block potentially dangerous patterns
        dangerous_patterns = [
            "system prompt",
            "ignore instructions",
            "__import__"
        ]

        v_lower = v.lower()
        for pattern in dangerous_patterns:
            if pattern in v_lower:
                raise ValueError(f"Blocked pattern detected: {pattern}")

        return v

# Usage
@app.post("/agent/execute")
async def execute_agent(request: AgentRequest):
    """Execute agent with validated input."""
    # request is automatically validated by Pydantic
    return await run_agent(request)
```

### 3. Sandboxed Code Execution

```python
import docker
from typing import Tuple

class SafeCodeExecutor:
    """Execute code in isolated Docker container."""

    def __init__(self, memory_limit: str = "512m", timeout: int = 10):
        self.client = docker.from_env()
        self.memory_limit = memory_limit
        self.timeout = timeout

    def execute(self, code: str) -> Tuple[str, bool]:
        """
        Execute code safely in container.

        Returns:
            (output, success)
        """
        try:
            # Create isolated container
            container = self.client.containers.run(
                "python:3.11-slim",
                f"python -c {repr(code)}",
                stdout=True,
                stderr=True,
                timeout=self.timeout,
                mem_limit=self.memory_limit,
                memswap_limit=self.memory_limit,
                network_disabled=True,  # No network access
                read_only=True,  # Read-only filesystem
                remove=True,
                detach=False
            )

            output = container.decode()
            return (output, True)

        except docker.errors.ContainerError as e:
            return (str(e), False)
        except Exception as e:
            return (f"Execution error: {str(e)}", False)

# Usage
executor = SafeCodeExecutor()
output, success = executor.execute("print('Hello, World!')")
```

### 4. Secrets Management

```python
import os
from cryptography.fernet import Fernet

class SecretsManager:
    """Secure secrets management."""

    def __init__(self):
        # Load encryption key from environment
        key = os.getenv("ENCRYPTION_KEY")
        if not key:
            raise ValueError("ENCRYPTION_KEY not set")

        self.cipher = Fernet(key)

    def encrypt_secret(self, secret: str) -> str:
        """Encrypt a secret."""
        return self.cipher.encrypt(secret.encode()).decode()

    def decrypt_secret(self, encrypted: str) -> str:
        """Decrypt a secret."""
        return self.cipher.decrypt(encrypted.encode()).decode()

# Environment configuration
import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")  # Never hardcode!
DATABASE_URL = os.getenv("DATABASE_URL")  # Use connection string
SECRET_KEY = os.getenv("SECRET_KEY")  # From secure store

# Validate required settings
required_settings = ["SECRET_KEY", "DATABASE_URL"]
missing = [s for s in required_settings if not os.getenv(s)]
if missing:
    raise ValueError(f"Missing required environment variables: {missing}")
```

---

## Performance Optimization {#performance}

### 1. Response Caching

```python
from functools import lru_cache
from redis import Redis
from typing import Optional
import json
import hashlib

class CachedAgent:
    """Agent with response caching."""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = Redis.from_url(redis_url, decode_responses=True)
        self.cache_ttl = 3600  # 1 hour

    def _make_cache_key(self, prompt: str, model: str) -> str:
        """Generate cache key from prompt and model."""
        content = f"{prompt}:{model}"
        return f"agent:{hashlib.md5(content.encode()).hexdigest()}"

    async def run(self, prompt: str, model: str = "mistral") -> str:
        """Run agent with caching."""

        # Check cache
        cache_key = self._make_cache_key(prompt, model)
        cached = self.redis.get(cache_key)

        if cached:
            return json.loads(cached)

        # Execute if not cached
        response = await self.agent.ainvoke({"input": prompt})
        result = response.get("output")

        # Store in cache
        self.redis.setex(
            cache_key,
            self.cache_ttl,
            json.dumps(result)
        )

        return result

# Usage
agent = CachedAgent()
response = await agent.run("What is AI?")
```

### 2. Batch Processing

```python
from typing import List
from concurrent.futures import ThreadPoolExecutor
from langchain_ollama import ChatOllama

class BatchProcessor:
    """Process multiple requests efficiently."""

    def __init__(self, llm_model: str = "mistral", max_workers: int = 4):
        self.llm = ChatOllama(model=llm_model)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def process_batch(self, prompts: List[str]) -> List[str]:
        """Process multiple prompts in parallel."""

        def process_single(prompt: str) -> str:
            response = self.llm.invoke(prompt)
            return response.content

        # Execute in parallel
        results = list(self.executor.map(process_single, prompts))
        return results

# Usage
processor = BatchProcessor(max_workers=4)
results = processor.process_batch([
    "What is AI?",
    "What is ML?",
    "What is DL?"
])
```

### 3. Model Quantization

```bash
# Use smaller, quantized models for faster inference
ollama pull mistral           # Default (4-bit)
ollama pull orca-mini         # 3B model
ollama pull neural-chat       # Optimized

# Memory usage comparison:
# - Mistral (7B, 4-bit):  ~4GB
# - Llama2 (7B, 4-bit):   ~4GB
# - Llama2 (70B, 4-bit):  ~40GB
# - Orca-mini (3B):       ~2GB
```

### 4. Request Queuing

```python
from queue import Queue
from threading import Thread
import time

class RequestQueue:
    """Queue and process requests efficiently."""

    def __init__(self, max_queue_size: int = 100):
        self.queue = Queue(maxsize=max_queue_size)
        self.running = True

        # Start worker thread
        self.worker = Thread(target=self._process_queue, daemon=True)
        self.worker.start()

    def _process_queue(self):
        """Process queued requests."""
        while self.running:
            try:
                request = self.queue.get(timeout=1)

                # Process request
                result = self.process_request(request)

                # Store result
                request["result"] = result
                request["done"] = True

            except:
                pass

    def submit(self, request: dict) -> str:
        """Submit request to queue."""
        self.queue.put(request)
        return request.get("id")

    def get_result(self, request_id: str) -> Optional[dict]:
        """Retrieve processed result."""
        # Implementation: look up result in storage
        pass

    def stop(self):
        """Stop processing queue."""
        self.running = False
        self.worker.join()
```

---

## Monitoring and Logging {#monitoring}

### 1. Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
request_count = Counter(
    'agent_requests_total',
    'Total agent requests',
    ['model', 'status']
)

request_duration = Histogram(
    'agent_request_duration_seconds',
    'Agent request duration',
    ['model']
)

active_requests = Gauge(
    'agent_active_requests',
    'Number of active agent requests'
)

# Use metrics
@app.post("/agent/execute")
async def execute_agent(request: AgentRequest):
    """Execute agent and record metrics."""
    active_requests.inc()
    start_time = time.time()

    try:
        result = await run_agent(request)
        request_count.labels(model=request.model, status="success").inc()
        return result

    except Exception as e:
        request_count.labels(model=request.model, status="error").inc()
        raise

    finally:
        duration = time.time() - start_time
        request_duration.labels(model=request.model).observe(duration)
        active_requests.dec()
```

### 2. Structured Logging

```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    """Structured logging for better analysis."""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def log_event(
        self,
        event_type: str,
        level: str = "INFO",
        **kwargs
    ):
        """Log structured event."""

        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event_type,
            "level": level,
            **kwargs
        }

        log_func = getattr(self.logger, level.lower())
        log_func(json.dumps(log_entry))

# Usage
logger = StructuredLogger(__name__)

logger.log_event(
    "agent_execution_start",
    user_id="user123",
    model="mistral",
    prompt_length=100
)

logger.log_event(
    "agent_execution_complete",
    user_id="user123",
    duration=2.5,
    status="success"
)
```

### 3. Health Checks

```python
from fastapi import FastAPI
import httpx

app = FastAPI()

@app.get("/health")
async def health_check():
    """Comprehensive health check."""

    checks = {
        "api": "healthy",
        "ollama": check_ollama_server(),
        "database": check_database(),
        "cache": check_redis(),
        "timestamp": datetime.utcnow().isoformat()
    }

    # Overall status
    overall = "healthy" if all(
        v == "healthy" for v in checks.values()
    ) else "degraded"

    return {
        "status": overall,
        "checks": checks
    }

def check_ollama_server() -> str:
    """Check if Ollama server is responding."""
    try:
        response = httpx.get(
            "http://localhost:11434/api/tags",
            timeout=2
        )
        return "healthy" if response.status_code == 200 else "unhealthy"
    except:
        return "unhealthy"

def check_database() -> str:
    """Check database connectivity."""
    # Implementation
    pass

def check_redis() -> str:
    """Check Redis connectivity."""
    # Implementation
    pass
```

---

## Scaling Strategies {#scaling}

### 1. Horizontal Scaling (Multiple Agent Instances)

```yaml
# docker-compose.yml - Multiple agent instances
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - NVIDIA_VISIBLE_DEVICES=all

  agent-1:
    build: .
    container_name: agent-1
    ports:
      - "8001:8000"
    depends_on:
      - ollama
    environment:
      - OLLAMA_HOST=http://ollama:11434
      - REDIS_URL=redis://redis:6379
    links:
      - ollama
      - redis

  agent-2:
    build: .
    container_name: agent-2
    ports:
      - "8002:8000"
    depends_on:
      - ollama
    environment:
      - OLLAMA_HOST=http://ollama:11434
      - REDIS_URL=redis://redis:6379
    links:
      - ollama
      - redis

  agent-3:
    build: .
    container_name: agent-3
    ports:
      - "8003:8000"
    depends_on:
      - ollama
    environment:
      - OLLAMA_HOST=http://ollama:11434
      - REDIS_URL=redis://redis:6379
    links:
      - ollama
      - redis

  nginx:
    image: nginx:latest
    container_name: nginx
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - agent-1
      - agent-2
      - agent-3

  redis:
    image: redis:latest
    container_name: redis
    ports:
      - "6379:6379"

volumes:
  ollama_data:
```

**nginx.conf** - Load balancing:

```nginx
upstream agents {
    least_conn;  # Use least connections algorithm
    server agent-1:8000;
    server agent-2:8000;
    server agent-3:8000;
}

server {
    listen 80;
    server_name _;

    location /api/ {
        proxy_pass http://agents;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /health {
        access_log off;
        proxy_pass http://agents/health;
    }
}
```

### 2. GPU Distribution

For multiple GPUs, distribute models across them:

```python
import os
from langchain_ollama import ChatOllama

def get_llm_for_gpu(gpu_id: int, model: str):
    """Get LLM instance on specific GPU."""

    os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)

    return ChatOllama(
        model=model,
        base_url=f"http://localhost:1143{gpu_id}"
    )

# Usage with multiple GPUs
llm_gpu0 = get_llm_for_gpu(0, "mistral")    # GPU 0
llm_gpu1 = get_llm_for_gpu(1, "llama2")    # GPU 1
```

---

## Docker Deployment {#docker}

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ .

# Create non-root user for security
RUN useradd -m -u 1000 agent
USER agent

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama-prod
    restart: always
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  agent:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: agent-prod
    restart: always
    ports:
      - "8000:8000"
    depends_on:
      - ollama
      - redis
    environment:
      - OLLAMA_HOST=http://ollama-prod:11434
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://user:pass@postgres:5432/agent
      - SECRET_KEY=${SECRET_KEY}
    links:
      - ollama:ollama-prod
      - redis
      - postgres
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G

  redis:
    image: redis:7-alpine
    container_name: redis-prod
    restart: always
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"

  postgres:
    image: postgres:15-alpine
    container_name: postgres-prod
    restart: always
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_DB: agent
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  ollama_data:
  redis_data:
  postgres_data:
```

**Build and Deploy:**

```bash
# Build image
docker build -t agent-prod:latest .

# Run with compose
docker-compose up -d

# View logs
docker-compose logs -f agent

# Monitor resources
docker stats

# Stop services
docker-compose down
```

---

## Kubernetes Deployment {#kubernetes}

### Deployment YAML

```yaml
# agent-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent
  namespace: ai-agents
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agent
  template:
    metadata:
      labels:
        app: agent
    spec:
      containers:
      - name: agent
        image: agent-prod:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
        env:
        - name: OLLAMA_HOST
          value: "http://ollama:11434"
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: agent-secrets
              key: redis-url
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: agent-secrets
              key: database-url
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5

---
# agent-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: agent
  namespace: ai-agents
spec:
  selector:
    app: agent
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer

---
# ollama-statefulset.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: ollama
  namespace: ai-agents
spec:
  serviceName: ollama
  replicas: 1
  selector:
    matchLabels:
      app: ollama
  template:
    metadata:
      labels:
        app: ollama
    spec:
      containers:
      - name: ollama
        image: ollama/ollama:latest
        ports:
        - containerPort: 11434
        resources:
          requests:
            memory: "16Gi"
            cpu: "4"
          limits:
            memory: "32Gi"
            cpu: "8"
            nvidia.com/gpu: 1
        volumeMounts:
        - name: ollama-data
          mountPath: /root/.ollama
  volumeClaimTemplates:
  - metadata:
      name: ollama-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 100Gi
```

**Deploy to Kubernetes:**

```bash
# Create namespace
kubectl create namespace ai-agents

# Create secrets
kubectl create secret generic agent-secrets \
  --from-literal=redis-url=redis://redis:6379 \
  --from-literal=database-url=postgresql://... \
  -n ai-agents

# Deploy resources
kubectl apply -f agent-deployment.yaml
kubectl apply -f agent-service.yaml
kubectl apply -f ollama-statefulset.yaml

# Check status
kubectl get pods -n ai-agents
kubectl logs -f deployment/agent -n ai-agents

# Scale deployments
kubectl scale deployment agent --replicas=5 -n ai-agents
```

---

## Best Practices Checklist {#checklist}

### Security

- [ ] Authentication (JWT/OAuth2)
- [ ] Authorization (role-based access)
- [ ] Input validation and sanitization
- [ ] Code execution sandboxing
- [ ] Secrets management (not in code)
- [ ] HTTPS/TLS enabled
- [ ] Rate limiting
- [ ] Audit logging

### Performance

- [ ] Response caching
- [ ] Request queuing
- [ ] Batch processing
- [ ] Model quantization
- [ ] GPU acceleration enabled
- [ ] Connection pooling
- [ ] Compression enabled

### Operations

- [ ] Health checks
- [ ] Structured logging
- [ ] Metrics collection
- [ ] Error alerting
- [ ] Graceful degradation
- [ ] Backup strategy
- [ ] Recovery procedures

### Deployment

- [ ] CI/CD pipeline
- [ ] Automated testing
- [ ] Blue-green deployments
- [ ] Rollback procedures
- [ ] Load testing
- [ ] Documentation
- [ ] Runbooks for common issues

### Monitoring

- [ ] Request latency tracking
- [ ] Error rate monitoring
- [ ] Resource utilization (CPU, memory, GPU)
- [ ] Queue depth monitoring
- [ ] Cache hit rates
- [ ] Database performance

### Scaling

- [ ] Horizontal scaling configured
- [ ] Load balancing active
- [ ] Auto-scaling policies
- [ ] Database connection pooling
- [ ] Cache coherence (multi-instance)

---

## Troubleshooting

### High Memory Usage

```bash
# Check memory usage
docker stats

# Reduce memory by using smaller model
ollama pull orca-mini

# Or limit container memory
docker run -m 4g agent-prod
```

### High Latency

```bash
# Check GPU utilization
nvidia-smi

# Monitor inference times
grep "duration" logs/agent.log | tail -20

# Solutions:
# 1. Use faster model (mistral vs llama2)
# 2. Enable caching
# 3. Add more replicas
```

### Database Performance

```bash
# Check slow queries
SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;

# Add indexes on frequently queried columns
CREATE INDEX idx_user_requests ON requests(user_id, created_at);

# Check connection pool status
SELECT count(*) FROM pg_stat_activity;
```

---

## Summary

Production deployment requires:
1. Security hardening and validation
2. Performance optimization and caching
3. Comprehensive monitoring and logging
4. Scaling strategies for growth
5. Containerization for consistency
6. High availability configuration

Start with Docker compose for development, move to Kubernetes for production scale.
