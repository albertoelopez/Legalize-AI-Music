# Suno AI to MIDI FL Studio Automation

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ollama](https://img.shields.io/badge/Ollama-Open%20Source-green.svg)](https://ollama.ai)

An intelligent, open-source system for converting audio to MIDI files and automating FL Studio production workflows using local LLM agents powered by Ollama.

## 🌟 Features

### Core Capabilities

- **🎵 Audio to MIDI Conversion**
  - High-quality polyphonic conversion using Spotify's Basic-Pitch
  - Support for MP3, WAV, FLAC, and other audio formats
  - Batch processing for multiple files
  - Audio preprocessing and enhancement

- **🎹 FL Studio Automation**
  - Desktop automation via Model Context Protocol (MCP) server
  - PyAutoGUI-based UI automation
  - MIDI scripting API support
  - Project creation, track management, mixer control

- **🤖 AI Agent Orchestration**
  - Ollama integration for local, open-source LLMs (Mistral, Llama2, CodeLlama)
  - LangChain agent framework with custom tools
  - Natural language workflow execution
  - Async subagents for parallel processing

- **🎛️ User Control**
  - CLI interface with rich console output
  - Start/stop/status workflow controls
  - Python API for programmatic access
  - Configurable via YAML and environment variables

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+ (for MCP server)
- [Ollama](https://ollama.ai) installed and running
- FL Studio (Windows only)

### Installation

```bash
# Clone the repository
cd ralph_app

# Run automated setup
chmod +x setup.sh
./setup.sh

# Or manual setup:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd mcp_servers/fl_studio_mcp && npm install && cd ../..
```

### Configuration

```bash
# Create environment file
cp .env.example .env

# Edit with your settings
nano .env
```

### Start Ollama

```bash
# Start Ollama server
ollama serve

# Pull models (first time)
ollama pull mistral
ollama pull llama2
```

### Your First Conversion

```bash
# Activate virtual environment
source venv/bin/activate

# Convert audio to MIDI
python src/main.py convert audio.mp3

# Convert and add to FL Studio
python src/main.py convert audio.mp3 --add-to-fl
```

### Your First Agent Workflow

```bash
# Let AI agent handle the workflow
python src/main.py start --prompt "Convert my_song.mp3 to MIDI and add it to FL Studio on track 1"
```

## 📖 Documentation

- **[Quick Start Guide](docs/QUICKSTART.md)** - Get running in 5 minutes
- **[Usage Guide](docs/USAGE.md)** - Detailed usage instructions
- **[Examples](docs/EXAMPLES.md)** - Code examples and workflows
- **[Setup Guide](docs/SETUP.md)** - Detailed installation guide
- **[API Documentation](docs/API.md)** - Complete API reference
- **[Configuration](docs/CONFIGURATION.md)** - Configuration options

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interface                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │     CLI      │  │  Python API  │  │   Workflow   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Agent Orchestration                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Ollama Agent (Mistral/Llama2)                       │  │
│  │  + LangChain Framework + Custom Tools                │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
           ↓                           ↓
┌────────────────────────┐  ┌──────────────────────────────┐
│  Audio to MIDI Module  │  │  FL Studio Automation        │
│  ┌──────────────────┐  │  │  ┌────────────────────────┐ │
│  │  Basic-Pitch     │  │  │  │  MCP Server            │ │
│  │  Audio Processor │  │  │  │  PyAutoGUI Automation  │ │
│  │  MIDI Generator  │  │  │  │  MIDI Scripting API    │ │
│  └──────────────────┘  │  │  └────────────────────────┘ │
└────────────────────────┘  └──────────────────────────────┘
```

### Directory Structure

```
ralph_app/
├── src/
│   ├── audio_to_midi/        # Audio to MIDI conversion
│   │   ├── converter.py      # Main converter using Basic-Pitch
│   │   └── processor.py      # Audio preprocessing
│   ├── fl_studio_automation/  # FL Studio automation
│   │   ├── fl_studio_pyautogui_automation.py
│   │   └── fl_studio_midi_controller.py
│   ├── agent_framework/       # AI agent system
│   │   ├── ollama_agent.py   # Ollama + LangChain agent
│   │   └── tools.py          # Custom agent tools
│   └── workflow/              # Workflow orchestration
│       ├── orchestrator.py   # Main workflow coordinator
│       └── cli.py            # CLI interface
├── mcp_servers/
│   └── fl_studio_mcp/         # MCP server for FL Studio
│       ├── index.js          # Node.js MCP server
│       └── fl_studio_mcp_server.py  # Python MCP server
├── config/
│   └── config.yaml           # Main configuration
├── docs/                      # Documentation
├── tests/                     # Test suite
│   └── test_full_workflow.py # Integration tests
└── output/                    # Generated files
    ├── midi/                 # MIDI outputs
    ├── enhanced_audio/       # Processed audio
    └── fl_projects/          # FL Studio projects
```

## 💻 Usage Examples

### CLI Examples

```bash
# Convert single file
python src/main.py convert my_song.mp3

# Convert multiple files
python src/main.py convert track1.mp3 track2.wav track3.flac

# Convert with custom output directory
python src/main.py convert audio.mp3 -o /custom/output

# Agent workflow
python src/main.py start --prompt "Convert all MP3 files to MIDI and create FL Studio project"

# Check status
python src/main.py status

# Stop workflow
python src/main.py stop

# Test Ollama connection
python src/main.py test-ollama
```

### Python API Examples

#### Basic Audio to MIDI Conversion

```python
from audio_to_midi import AudioToMIDIConverter

converter = AudioToMIDIConverter()
result = converter.convert(
    audio_path="input.mp3",
    output_dir="output/midi"
)

print(f"MIDI: {result['output_midi']}")
print(f"Notes: {result['midi_info']['total_notes']}")
```

#### Advanced Conversion with Preprocessing

```python
from audio_to_midi import AudioProcessor, AudioToMIDIConverter

# Preprocess audio
processor = AudioProcessor()
enhanced = processor.enhance_for_midi(
    "raw_audio.mp3",
    "enhanced.wav",
    normalize=True,
    remove_silence=True
)

# Convert to MIDI
converter = AudioToMIDIConverter()
result = converter.convert(
    enhanced,
    "output/midi",
    onset_threshold=0.5,
    frame_threshold=0.3
)
```

#### Agent-Driven Workflow

```python
from workflow import WorkflowOrchestrator

orchestrator = WorkflowOrchestrator(
    model_name="mistral",
    ollama_url="http://localhost:11434"
)

# Natural language workflow
result = orchestrator.start(
    """
    Convert vocals.mp3, drums.wav, and bass.mp3 to MIDI.
    Create FL Studio project 'My Song'.
    Add files to separate tracks and balance mixer.
    Save the project.
    """
)
```

#### FL Studio Automation

```python
from fl_studio_automation import fl_studio_pyautogui_automation

fl = fl_studio_pyautogui_automation.FLStudioWorkflows()

# Launch and create project
fl.launch()
fl.create_new_project("AI Music Project")

# Adjust mixer
fl.adjust_mixer_volume(track=0, volume=0.8)
fl.adjust_mixer_volume(track=1, volume=0.6)

# Save
fl.save_project("output/projects/myproject.flp")
```

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# Output Paths
OUTPUT_DIR=output
MIDI_OUTPUT_DIR=output/midi

# FL Studio
FL_STUDIO_PATH="C:\\Program Files\\Image-Line\\FL Studio 21\\FL64.exe"

# Logging
LOG_LEVEL=INFO
```

### YAML Configuration (config/config.yaml)

```yaml
# Ollama Settings
ollama:
  model: "mistral"
  temperature: 0.7

# Audio to MIDI Settings
audio_to_midi:
  onset_threshold: 0.5
  frame_threshold: 0.3
  minimum_note_length: 127.70

# FL Studio Settings
fl_studio:
  automation_delay: 1000
  default_drop_position:
    x: 400
    y: 300

# Workflow Settings
workflow:
  max_concurrent_conversions: 5
  auto_cleanup: false
```

## 🧪 Testing

```bash
# Run full workflow tests
python tests/test_full_workflow.py

# Run specific test
python -m pytest tests/test_audio_conversion.py
```

## 🤝 Technology Stack

- **Audio Processing**: [Basic-Pitch](https://github.com/spotify/basic-pitch) (Spotify), librosa, pretty_midi
- **LLM Orchestration**: [Ollama](https://ollama.ai), [LangChain](https://langchain.com)
- **Desktop Automation**: [PyAutoGUI](https://pyautogui.readthedocs.io), [MCP](https://modelcontextprotocol.io)
- **FL Studio**: MIDI Scripting API, native Python integration
- **CLI**: Click, Rich

## 📊 Supported Models

### Ollama Models (Recommended)

- **Mistral** (Default) - Best balance of speed and capability
- **Llama2** - Faster, lighter weight
- **CodeLlama** - Better for technical tasks
- **Other** - Any Ollama-compatible model

### Audio Formats

- MP3, WAV, FLAC, OGG, M4A
- Sample rates: 16kHz - 48kHz
- Mono and stereo supported

## 🎯 Use Cases

1. **Music Production**: Convert audio ideas to MIDI for editing
2. **Sampling**: Extract melodies from audio samples
3. **Transcription**: Convert performances to MIDI notation
4. **Workflow Automation**: Automate repetitive FL Studio tasks
5. **Batch Processing**: Process entire music libraries
6. **AI-Assisted Production**: Use agents for creative workflows

## 🛠️ Development

### Built with Ralph Wiggum Technique

This project was developed using the [Ralph Wiggum technique](https://ghuntley.com/ralph/) - an iterative AI development methodology using continuous loops.

### Contributing

Contributions are welcome! Please check the issues page.

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Spotify Basic-Pitch](https://github.com/spotify/basic-pitch) for audio-to-MIDI conversion
- [Ollama](https://ollama.ai) for local LLM execution
- [LangChain](https://langchain.com) for agent framework
- [Model Context Protocol](https://modelcontextprotocol.io) for tool standardization
- [Geoffrey Huntley](https://ghuntley.com/ralph/) for the Ralph Wiggum technique

## 📞 Support

- **Documentation**: See `docs/` folder
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

## 🗺️ Roadmap

- [ ] Add support for more audio formats
- [ ] Implement real-time audio to MIDI conversion
- [ ] Add more FL Studio automation features
- [ ] Support for other DAWs (Ableton, Logic Pro)
- [ ] Web interface for remote control
- [ ] Cloud deployment options
- [ ] Plugin system for extensibility

---

**Made with ❤️ using open source tools and AI agents**
