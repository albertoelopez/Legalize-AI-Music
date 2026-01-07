# Setup Guide

## Prerequisites

1. **Python 3.10+**
   ```bash
   python3 --version
   ```

2. **Node.js 18+** (for MCP server)
   ```bash
   node --version
   npm --version
   ```

3. **Ollama** (for running open source LLMs)
   - Download from: https://ollama.ai
   - Follow installation instructions for your OS

4. **FL Studio** (Windows only)
   - Required for the automation features
   - Install from: https://www.image-line.com

## Installation

### Automated Setup (Linux/Mac)

```bash
chmod +x setup.sh
./setup.sh
```

### Manual Setup

1. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install MCP server dependencies**
   ```bash
   cd mcp_servers/fl_studio_mcp
   npm install
   cd ../..
   ```

4. **Pull Ollama models**
   ```bash
   ollama pull mistral
   ollama pull llama2  # Optional alternative
   ```

5. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

## Configuration

### Environment Variables

Edit `.env` file:

```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# Output Paths
OUTPUT_DIR=output
MIDI_OUTPUT_DIR=output/midi

# FL Studio (Windows only)
FL_STUDIO_PATH="C:\\Program Files\\Image-Line\\FL Studio 21\\FL64.exe"

# Logging
LOG_LEVEL=INFO
```

### YAML Configuration

Edit `config/config.yaml` for detailed settings:

- Audio processing parameters
- FL Studio automation settings
- Agent behavior configuration
- Workflow options

## Testing Installation

1. **Test Ollama connection**
   ```bash
   python src/main.py test-ollama
   ```

2. **Check status**
   ```bash
   python src/main.py status
   ```

3. **Convert a test audio file**
   ```bash
   python src/main.py convert path/to/audio.mp3
   ```

## Troubleshooting

### Ollama Not Found

```bash
# Install Ollama
# Linux/Mac: Follow instructions at https://ollama.ai
# Windows: Download installer from https://ollama.ai

# Verify installation
ollama --version

# Start Ollama service
ollama serve
```

### Model Not Available

```bash
# Pull the model
ollama pull mistral

# List available models
ollama list
```

### Python Dependencies Issues

```bash
# Clear pip cache
pip cache purge

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### MCP Server Issues

```bash
# Rebuild node modules
cd mcp_servers/fl_studio_mcp
rm -rf node_modules package-lock.json
npm install
```

### FL Studio Not Detected

- Ensure FL Studio is installed
- Verify the path in `.env` is correct
- Make sure FL Studio is running before automation attempts

## Next Steps

Once setup is complete:

1. Read the [Usage Guide](USAGE.md)
2. Check out [Examples](EXAMPLES.md)
3. Review the [API Documentation](API.md)

## Support

For issues:
1. Check the [FAQ](FAQ.md)
2. Review existing issues on GitHub
3. Create a new issue with detailed information
