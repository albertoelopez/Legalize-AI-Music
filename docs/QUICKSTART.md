# Quick Start Guide

Get up and running with Suno AI to MIDI FL Studio automation in 5 minutes.

## Prerequisites

- Python 3.10+
- Node.js 18+ (for MCP server)
- FL Studio (Windows)
- Ollama installed and running

## Installation

### 1. Clone and Setup

```bash
cd ralph_app

# Run automated setup
chmod +x setup.sh
./setup.sh
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit configuration (use your favorite editor)
nano .env
```

Update these values:
```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
FL_STUDIO_PATH="C:\Program Files\Image-Line\FL Studio 21\FL64.exe"
```

### 3. Start Ollama

```bash
# In a separate terminal
ollama serve

# Pull the model (first time only)
ollama pull mistral
```

### 4. Test Installation

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Test Ollama connection
python src/main.py test-ollama

# Check status
python src/main.py status
```

## Your First Conversion

### Convert Audio to MIDI

```bash
# Basic conversion
python src/main.py convert path/to/your/audio.mp3

# Result: output/midi/audio.mid
```

### Convert and Add to FL Studio

```bash
# Automatically adds to FL Studio
python src/main.py convert audio.mp3 --add-to-fl
```

## Your First Agent Workflow

### Simple Task

```bash
python src/main.py start --prompt "Convert my_song.mp3 to MIDI and add it to FL Studio"
```

### Complex Task

```bash
python src/main.py start --prompt "Convert all MP3 files in ./music folder, add them to FL Studio on separate tracks, balance the mixer, and save as 'My_Project.flp'"
```

## Common Commands

### Start Workflow

```bash
# Basic
python src/main.py start --prompt "Your task here"

# With different model
python src/main.py start --prompt "Your task" --model llama2

# Async mode
python src/main.py start --prompt "Your task" --async-mode
```

### Convert Audio Files

```bash
# Single file
python src/main.py convert audio.mp3

# Multiple files
python src/main.py convert track1.mp3 track2.wav track3.flac

# With custom output directory
python src/main.py convert audio.mp3 -o /custom/output
```

### Monitor and Control

```bash
# Check status
python src/main.py status

# Stop workflow
python src/main.py stop

# Test Ollama
python src/main.py test-ollama
```

## Python API Quick Start

### Basic Usage

```python
from workflow import WorkflowOrchestrator

# Create orchestrator
orchestrator = WorkflowOrchestrator(
    model_name="mistral",
    ollama_url="http://localhost:11434"
)

# Run task
result = orchestrator.start(
    "Convert audio.mp3 to MIDI and add to FL Studio"
)

print(result)
```

### Audio Conversion

```python
from audio_to_midi import AudioToMIDIConverter

# Create converter
converter = AudioToMIDIConverter()

# Convert
result = converter.convert(
    audio_path="input.mp3",
    output_dir="output/midi"
)

print(f"MIDI: {result['output_midi']}")
print(f"Notes: {result['midi_info']['total_notes']}")
```

### FL Studio Automation

```python
from fl_studio_automation import fl_studio_pyautogui_automation

# Create automation
fl = fl_studio_pyautogui_automation.FLStudioWorkflows()

# Launch and setup
fl.launch()
fl.create_new_project("My Project")
fl.save_project("output/projects/myproject.flp")
```

## Directory Structure

After installation, your project should look like this:

```
ralph_app/
├── src/
│   ├── audio_to_midi/       # Audio to MIDI conversion
│   ├── fl_studio_automation/ # FL Studio control
│   ├── agent_framework/      # Ollama agents
│   └── workflow/             # Orchestration
├── mcp_servers/
│   └── fl_studio_mcp/        # MCP server for FL Studio
├── output/
│   ├── midi/                 # Generated MIDI files
│   ├── enhanced_audio/       # Processed audio
│   └── fl_projects/          # FL Studio projects
├── config/
│   └── config.yaml           # Configuration
├── docs/                     # Documentation
└── tests/                    # Test files
```

## Workflow Examples

### Example 1: Convert One Audio File

```bash
# Step 1: Place audio file in project folder
cp ~/Music/mysong.mp3 .

# Step 2: Convert to MIDI
python src/main.py convert mysong.mp3

# Step 3: Check output
ls output/midi/
# Result: mysong.mid
```

### Example 2: Batch Convert with FL Studio

```bash
# Step 1: Create music folder with audio files
mkdir music
cp ~/Music/*.mp3 music/

# Step 2: Convert all and add to FL Studio
python src/main.py start --prompt "Convert all files in music/ folder to MIDI and add to FL Studio"

# Step 3: Check FL Studio - all tracks should be loaded
```

### Example 3: Custom Workflow

```python
# create_project.py
from workflow import WorkflowOrchestrator

orchestrator = WorkflowOrchestrator()

# Define your workflow
workflow = """
1. Convert vocals.mp3, drums.wav, bass.mp3 to MIDI
2. Create FL Studio project 'My Song'
3. Add vocals to track 1 (volume 90%)
4. Add drums to track 2 (volume 100%)
5. Add bass to track 3 (volume 75%)
6. Save project
"""

# Execute
result = orchestrator.start(workflow)
print("Workflow completed:", result)
```

Run it:
```bash
python create_project.py
```

## Configuration Tips

### Optimize Audio Conversion

Edit `config/config.yaml`:

```yaml
audio_to_midi:
  onset_threshold: 0.5      # Lower = more sensitive (0.3-0.7)
  frame_threshold: 0.3      # Lower = more notes (0.2-0.4)
  minimum_note_length: 127.70  # Minimum note duration (ms)
  minimum_frequency: null   # Auto-detect
  maximum_frequency: null   # Auto-detect
```

### Adjust FL Studio Automation

```yaml
fl_studio:
  automation_delay: 1000    # Delay between actions (ms)
  default_drop_position:
    x: 400                  # Default drop X position
    y: 300                  # Default drop Y position
```

### Agent Configuration

```yaml
agent:
  max_iterations: 10        # Max agent iterations
  verbose: true             # Show detailed logs
  handle_parsing_errors: true
```

## Troubleshooting Quick Fixes

### Ollama Not Found

```bash
# Check if Ollama is running
ollama list

# If not, start it
ollama serve
```

### FL Studio Not Detected

1. Verify FL Studio is installed
2. Check path in `.env` is correct
3. Make sure FL Studio is running

### Conversion Quality Issues

```python
# Try adjusting thresholds
from audio_to_midi import AudioToMIDIConverter

converter = AudioToMIDIConverter()
result = converter.convert(
    "audio.mp3",
    "output/midi",
    onset_threshold=0.3,  # More sensitive
    frame_threshold=0.2   # Detect more notes
)
```

### Model Not Responding

```bash
# Check Ollama connection
python src/main.py test-ollama

# Try a different model
python src/main.py start --prompt "Test" --model llama2
```

## Next Steps

Now that you're set up, explore:

- [Usage Guide](USAGE.md) - Detailed usage instructions
- [Examples](EXAMPLES.md) - More workflow examples
- [API Documentation](API.md) - Complete API reference
- [Configuration](CONFIGURATION.md) - Advanced configuration

## Getting Help

- Check [FAQ](FAQ.md) for common questions
- Review [Troubleshooting](TROUBLESHOOTING.md) guide
- Open an issue on GitHub

## Tips for Best Results

1. **Audio Quality**: Use high-quality audio files (WAV/FLAC preferred)
2. **Mono Audio**: Mono tracks convert better than stereo
3. **Pre-processing**: Use audio enhancement for better MIDI quality
4. **FL Studio**: Keep window visible during automation
5. **Models**: Use `mistral` for best results, `llama2` for speed
6. **Prompts**: Be specific and clear with your task descriptions

## Quick Reference

### Essential Commands

```bash
# Setup
./setup.sh

# Test
python src/main.py test-ollama
python src/main.py status

# Convert
python src/main.py convert audio.mp3
python src/main.py convert audio.mp3 --add-to-fl

# Workflow
python src/main.py start --prompt "Your task"
python src/main.py stop
```

### Essential Imports

```python
# Workflow
from workflow import WorkflowOrchestrator

# Audio conversion
from audio_to_midi import AudioToMIDIConverter, AudioProcessor

# FL Studio
from fl_studio_automation import fl_studio_pyautogui_automation
```

That's it! You're ready to start converting audio to MIDI and automating FL Studio with AI agents.
