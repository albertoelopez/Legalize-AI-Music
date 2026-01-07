# Usage Guide

## Quick Start

### Starting the Workflow

```bash
# Activate virtual environment
source venv/bin/activate

# Start workflow with a prompt
python src/main.py start --prompt "Convert my_audio.mp3 to MIDI and add it to FL Studio"
```

### CLI Commands

#### 1. Start Workflow

```bash
python src/main.py start --prompt "Your task description"

# Options:
# --model, -m: Ollama model to use (default: mistral)
# --ollama-url: Ollama API URL (default: http://localhost:11434)
# --async-mode: Run asynchronously
```

**Examples:**

```bash
# Basic usage
python src/main.py start --prompt "Convert audio to MIDI"

# Use different model
python src/main.py start --prompt "Process all files" --model llama2

# Async mode
python src/main.py start --prompt "Batch process" --async-mode
```

#### 2. Convert Audio to MIDI

```bash
python src/main.py convert <audio_files...>

# Options:
# --output-dir, -o: Output directory (default: output/midi)
# --add-to-fl: Automatically add to FL Studio
```

**Examples:**

```bash
# Convert single file
python src/main.py convert my_song.mp3

# Convert multiple files
python src/main.py convert song1.mp3 song2.wav song3.flac

# Convert and add to FL Studio
python src/main.py convert my_song.mp3 --add-to-fl

# Specify output directory
python src/main.py convert my_song.mp3 -o /path/to/output
```

#### 3. Check Status

```bash
python src/main.py status
```

Displays:
- Current workflow status
- Output directory
- Active model

#### 4. Stop Workflow

```bash
python src/main.py stop
```

Stops the currently running workflow.

#### 5. Test Ollama Connection

```bash
python src/main.py test-ollama

# Test with specific model
python src/main.py test-ollama --model llama2
```

## Using the Agent Framework

### Python API

```python
from workflow import WorkflowOrchestrator

# Initialize orchestrator
orchestrator = WorkflowOrchestrator(
    model_name="mistral",
    ollama_url="http://localhost:11434"
)

# Start workflow
result = orchestrator.start("Convert audio.mp3 to MIDI and add to FL Studio")

# Process audio batch
audio_files = ["song1.mp3", "song2.wav"]
results = orchestrator.process_audio_batch(audio_files, add_to_fl_studio=True)
```

### Async Usage

```python
import asyncio
from workflow import WorkflowOrchestrator

async def main():
    orchestrator = WorkflowOrchestrator()
    result = await orchestrator.start_async("Your task")
    print(result)

asyncio.run(main())
```

## Audio to MIDI Conversion

### Basic Conversion

```python
from audio_to_midi import AudioToMIDIConverter

converter = AudioToMIDIConverter()
result = converter.convert(
    audio_path="input.mp3",
    output_dir="output/midi"
)

print(f"MIDI saved to: {result['output_midi']}")
print(f"Duration: {result['midi_info']['duration']} seconds")
print(f"Total notes: {result['midi_info']['total_notes']}")
```

### Advanced Conversion

```python
result = converter.convert(
    audio_path="input.mp3",
    output_dir="output/midi",
    onset_threshold=0.5,        # Note onset detection threshold
    frame_threshold=0.3,        # Frame-level detection threshold
    minimum_note_length=127.70, # Minimum note length (ms)
    minimum_frequency=80.0,     # Minimum frequency (Hz)
    maximum_frequency=1000.0,   # Maximum frequency (Hz)
)
```

### Audio Pre-processing

```python
from audio_to_midi import AudioProcessor

processor = AudioProcessor()

# Enhance audio for better conversion
enhanced_path = processor.enhance_for_midi(
    audio_path="input.mp3",
    output_path="enhanced.wav",
    normalize=True,
    remove_silence=True
)

# Then convert the enhanced audio
result = converter.convert(enhanced_path, "output/midi")
```

## FL Studio Automation

### Using MCP Tools

The FL Studio MCP server provides desktop automation:

1. **Find FL Studio Window**
   - Locates and focuses FL Studio

2. **Click at Position**
   - Clicks at specific coordinates

3. **Send Keyboard Input**
   - Sends hotkeys and text input

4. **Drag & Drop MIDI**
   - Adds MIDI files to FL Studio

5. **Take Screenshot**
   - Captures FL Studio window

### Via Agent

```python
from agent_framework import OllamaAgent

agent = OllamaAgent()

# Let the agent handle FL Studio
result = agent.run("Add MIDI file to FL Studio and save project")
```

## Workflow Examples

### Example 1: Simple Conversion

```bash
python src/main.py convert my_song.mp3
```

### Example 2: Full Workflow

```bash
python src/main.py start --prompt "Convert all MP3 files in music/ folder to MIDI, add them to FL Studio, and save the project as 'My_Project'"
```

### Example 3: Batch Processing

```python
from workflow import WorkflowOrchestrator

orchestrator = WorkflowOrchestrator()

audio_files = [
    "track1.mp3",
    "track2.mp3",
    "track3.mp3"
]

results = orchestrator.process_audio_batch(
    audio_files,
    add_to_fl_studio=True
)

for result in results["results"]:
    print(f"{result['audio_file']} -> {result['midi_file']}")
```

## Tips and Best Practices

### Audio Quality

- Use high-quality audio files (WAV, FLAC preferred)
- Mono audio generally works better than stereo
- Remove silence and normalize audio for best results

### FL Studio Automation

- Keep FL Studio window visible during automation
- Avoid interfering with mouse/keyboard during automation
- Use consistent FL Studio window positions

### Ollama Models

- **mistral**: Good balance of speed and capability
- **llama2**: Faster, lighter weight
- **codellama**: Better for technical tasks

### Performance

- Use async mode for better responsiveness
- Process audio files in batches for efficiency
- Enable caching for repeated operations

## Troubleshooting

### Audio Conversion Issues

**Problem**: Low-quality MIDI output
- Solution: Adjust thresholds, enhance audio first

**Problem**: Missing notes
- Solution: Lower onset_threshold and frame_threshold

### FL Studio Automation Issues

**Problem**: Clicks not registering
- Solution: Increase automation_delay in config.yaml

**Problem**: Window not found
- Solution: Ensure FL Studio is running and visible

### Agent Issues

**Problem**: Agent not responding
- Solution: Check Ollama is running (`ollama serve`)

**Problem**: Parsing errors
- Solution: Simplify the prompt, be more specific

## Next Steps

- Check [API Documentation](API.md) for detailed API reference
- See [Examples](EXAMPLES.md) for more use cases
- Review [Configuration](CONFIGURATION.md) for advanced settings
