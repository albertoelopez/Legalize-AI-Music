#!/bin/bash

# Setup script for Ollama and LangChain local development environment
# Supports macOS, Linux, and Windows (WSL)

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

# Check OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
    else
        OS="unknown"
    fi
}

# 1. Install Ollama
install_ollama() {
    print_header "Installing Ollama"

    if command -v ollama &> /dev/null; then
        print_success "Ollama is already installed"
        return
    fi

    case $OS in
        linux)
            print_info "Installing Ollama for Linux..."
            curl https://ollama.ai/install.sh | sh
            print_success "Ollama installed successfully"
            ;;
        macos)
            print_info "Installing Ollama for macOS..."
            if command -v brew &> /dev/null; then
                brew install ollama
            else
                print_info "Downloading Ollama for macOS (Intel/Apple Silicon)..."
                open "https://ollama.ai"
                print_info "Please download and install Ollama from the website"
            fi
            ;;
        windows)
            print_info "Windows detected (WSL/MSYS2)..."
            print_info "Please download Ollama from https://ollama.ai for Windows"
            print_info "Or for WSL, run: curl https://ollama.ai/install.sh | sh"
            ;;
        *)
            print_error "Unsupported OS. Please install Ollama manually from https://ollama.ai"
            exit 1
            ;;
    esac
}

# 2. Start Ollama server
start_ollama_server() {
    print_header "Starting Ollama Server"

    if pgrep -x "ollama" > /dev/null; then
        print_success "Ollama server is already running"
        return
    fi

    case $OS in
        linux)
            if command -v systemctl &> /dev/null; then
                print_info "Starting Ollama with systemctl..."
                sudo systemctl start ollama
                sleep 2
                if systemctl is-active --quiet ollama; then
                    print_success "Ollama server started"
                else
                    print_error "Failed to start Ollama"
                    exit 1
                fi
            else
                print_info "Starting Ollama in background..."
                ollama serve &
                sleep 3
            fi
            ;;
        macos)
            print_info "Ollama should run automatically. Checking..."
            sleep 2
            if curl -s http://localhost:11434/api/tags > /dev/null; then
                print_success "Ollama server is running"
            else
                print_error "Ollama server not responding. Try running 'ollama serve'"
            fi
            ;;
        windows)
            print_info "Ensure Ollama is running (should start automatically on Windows)"
            ;;
    esac

    # Verify server is responding
    print_info "Verifying Ollama server..."
    max_retries=10
    retry=0

    while [ $retry -lt $max_retries ]; do
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            print_success "Ollama server is responding"
            return
        fi
        retry=$((retry + 1))
        sleep 1
    done

    print_error "Ollama server did not respond after $max_retries seconds"
    exit 1
}

# 3. Download models
download_models() {
    print_header "Downloading Models"

    models=("llama2" "mistral" "mxbai-embed-large")

    for model in "${models[@]}"; do
        print_info "Checking if $model is installed..."

        if ollama list | grep -q "$model"; then
            print_success "$model is already installed"
        else
            print_info "Downloading $model..."
            ollama pull "$model"
            print_success "$model downloaded"
        fi
    done
}

# 4. Setup Python environment
setup_python_env() {
    print_header "Setting Up Python Environment"

    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.8 or higher"
        exit 1
    fi

    python_version=$(python3 --version | awk '{print $2}')
    print_success "Python version: $python_version"

    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_info "Creating Python virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_success "Virtual environment already exists"
    fi

    # Activate virtual environment
    print_info "Activating virtual environment..."
    source venv/bin/activate

    # Upgrade pip
    print_info "Upgrading pip..."
    pip install --upgrade pip setuptools wheel

    # Install requirements
    if [ -f "requirements_ollama_langchain.txt" ]; then
        print_info "Installing requirements..."
        pip install -r requirements_ollama_langchain.txt
        print_success "Requirements installed"
    else
        print_error "requirements_ollama_langchain.txt not found"
        exit 1
    fi
}

# 5. Verify installation
verify_installation() {
    print_header "Verifying Installation"

    # Check Ollama
    if command -v ollama &> /dev/null; then
        print_success "Ollama CLI installed"
    else
        print_error "Ollama CLI not found"
    fi

    # Check Ollama server
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        models=$(curl -s http://localhost:11434/api/tags | grep -o '"name":"[^"]*"' | head -3)
        print_success "Ollama server is running"
        print_info "Available models: $models"
    else
        print_error "Ollama server is not responding"
        print_info "Try running: ollama serve"
    fi

    # Check Python packages
    print_info "Checking Python packages..."

    python3 -c "import langchain; print(f'LangChain version: {langchain.__version__}')" && \
        print_success "LangChain installed" || \
        print_error "LangChain not found"

    python3 -c "import langchain_ollama" && \
        print_success "langchain-ollama installed" || \
        print_error "langchain-ollama not found"

    python3 -c "import ollama" && \
        print_success "ollama Python client installed" || \
        print_error "ollama Python client not found"
}

# 6. Create test script
create_test_script() {
    print_header "Creating Test Script"

    cat > test_ollama_langchain.py << 'EOF'
#!/usr/bin/env python3
"""
Simple test script to verify Ollama and LangChain setup.
"""

from langchain_ollama import ChatOllama
import sys

def test_connection():
    """Test connection to Ollama server."""
    print("Testing Ollama and LangChain setup...")
    print("-" * 50)

    try:
        # Try to initialize ChatOllama with default server
        llm = ChatOllama(model="llama2", temperature=0.7)
        print("✓ Connected to Ollama server")

        # Try a simple inference
        print("\nTesting inference with prompt...")
        response = llm.invoke("Hi! In one sentence, explain what you can do.")

        print(f"✓ Inference successful!")
        print(f"\nResponse:\n{response.content}")

        print("\n" + "-" * 50)
        print("✓ Setup is working correctly!")
        return True

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Is Ollama running? Try: ollama serve")
        print("2. Is llama2 model installed? Try: ollama pull llama2")
        print("3. Is the server on port 11434? Check: curl http://localhost:11434/api/tags")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
EOF

    chmod +x test_ollama_langchain.py
    print_success "Test script created: test_ollama_langchain.py"
}

# 7. Print setup summary
print_summary() {
    print_header "Setup Summary"

    cat << EOF
Installation and configuration completed!

Next steps:

1. Verify the setup:
   python3 test_ollama_langchain.py

2. View available models:
   ollama list

3. Download additional models:
   ollama pull mistral
   ollama pull codellama
   ollama pull neural-chat

4. Start developing:
   - Check examples in: ollama_langchain_examples.py
   - Read guide: OLLAMA_LANGCHAIN_INTEGRATION_GUIDE.md

5. Run Ollama in production (Linux):
   sudo systemctl start ollama
   sudo systemctl enable ollama

Common commands:
   ollama serve              # Start Ollama server
   ollama list              # List installed models
   ollama pull <model>      # Download a model
   ollama run <model>       # Run a model interactively
   ollama rm <model>        # Remove a model

For more information, visit: https://ollama.ai

Environment variables:
   OLLAMA_HOST              # Server address (default: localhost:11434)
   OLLAMA_MODELS            # Model storage directory

EOF
}

# Main execution
main() {
    print_header "Ollama and LangChain Setup Script"

    detect_os
    print_info "Detected OS: $OS"

    # Run setup steps
    install_ollama
    start_ollama_server
    download_models
    setup_python_env
    verify_installation
    create_test_script
    print_summary
}

# Run main
main
