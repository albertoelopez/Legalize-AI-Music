#!/bin/bash
# Setup script for Suno AI to MIDI FL Studio Automation

set -e

echo "========================================="
echo "Suno AI to MIDI FL Studio Setup"
echo "========================================="

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Setup MCP server
echo "Setting up FL Studio MCP server..."
cd mcp_servers/fl_studio_mcp
npm install
cd ../..

# Create output directories
echo "Creating output directories..."
mkdir -p output/midi
mkdir -p output/enhanced_audio
mkdir -p output/fl_projects

# Copy environment file
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please edit .env file with your configuration"
fi

# Check Ollama installation
echo "Checking Ollama installation..."
if command -v ollama &> /dev/null; then
    echo "✓ Ollama is installed"

    # Check if mistral model is available
    if ollama list | grep -q "mistral"; then
        echo "✓ Mistral model is available"
    else
        echo "Pulling Mistral model..."
        ollama pull mistral
    fi
else
    echo "⚠ Ollama is not installed"
    echo "Please install Ollama from: https://ollama.ai"
    echo "Then run: ollama pull mistral"
fi

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Edit .env file with your configuration"
echo "3. Ensure Ollama is running: ollama serve"
echo "4. Test the installation: python src/main.py test-ollama"
echo "5. Start using: python src/main.py start --prompt 'Your task'"
echo ""
echo "For more information, see README.md"
