# Examples

This document provides practical examples for using the Suno AI to MIDI FL Studio automation system.

## Table of Contents

1. [Quick Start Examples](#quick-start-examples)
2. [Audio to MIDI Conversion](#audio-to-midi-conversion)
3. [FL Studio Automation](#fl-studio-automation)
4. [Agent-Driven Workflows](#agent-driven-workflows)
5. [Advanced Use Cases](#advanced-use-cases)

## Quick Start Examples

### Example 1: Convert Single Audio File to MIDI

```bash
# Activate virtual environment
source venv/bin/activate

# Convert audio to MIDI
python src/main.py convert my_song.mp3

# Output: output/midi/my_song.mid
```

### Example 2: Convert and Add to FL Studio

```bash
python src/main.py convert my_song.mp3 --add-to-fl
```

### Example 3: Agent-Driven Workflow

```bash
python src/main.py start --prompt "Convert all MP3 files in ./music folder to MIDI and add them to FL Studio"
```

## Audio to MIDI Conversion

### Basic Conversion with Default Settings

```python
from audio_to_midi import AudioToMIDIConverter

converter = AudioToMIDIConverter()

# Convert with defaults
result = converter.convert(
    audio_path="path/to/audio.mp3",
    output_dir="output/midi"
)

print(f"MIDI file: {result['output_midi']}")
print(f"Duration: {result['midi_info']['duration']} seconds")
print(f"Total notes: {result['midi_info']['total_notes']}")
```

### Advanced Conversion with Custom Parameters

```python
# Fine-tuned conversion for better accuracy
result = converter.convert(
    audio_path="vocals.mp3",
    output_dir="output/midi",
    onset_threshold=0.3,        # Lower = more sensitive
    frame_threshold=0.2,        # Lower = more notes detected
    minimum_note_length=100,    # Minimum note duration (ms)
    minimum_frequency=80.0,     # Min freq to detect (Hz)
    maximum_frequency=800.0,    # Max freq to detect (Hz)
)
```

### Batch Conversion

```python
# Convert multiple files
audio_files = [
    "track1.mp3",
    "track2.wav",
    "track3.flac"
]

results = converter.convert_batch(
    audio_files=audio_files,
    output_dir="output/midi",
    onset_threshold=0.5
)

for result in results:
    if result['success']:
        print(f"✓ {result['audio_file']} -> {result['midi_file']}")
    else:
        print(f"✗ {result['audio_file']}: {result['error']}")
```

### Pre-processing Audio for Better Results

```python
from audio_to_midi import AudioProcessor, AudioToMIDIConverter

processor = AudioProcessor()
converter = AudioToMIDIConverter()

# Enhance audio before conversion
enhanced_audio = processor.enhance_for_midi(
    audio_path="raw_audio.mp3",
    output_path="enhanced.wav",
    normalize=True,
    remove_silence=True
)

# Convert enhanced audio
result = converter.convert(enhanced_audio, "output/midi")
```

## FL Studio Automation

### Using the MCP Server (Python)

```python
import asyncio
from mcp_servers.fl_studio_mcp import fl_studio_mcp_server

async def automate_fl_studio():
    # Launch FL Studio
    await fl_studio_mcp_server.launch_fl_studio({})

    # Wait for startup
    await asyncio.sleep(3)

    # Create new project
    await fl_studio_mcp_server.create_project({
        "project_name": "My AI Project"
    })

    # Save project
    await fl_studio_mcp_server.save_project({})

asyncio.run(automate_fl_studio())
```

### Using PyAutoGUI Automation

```python
from fl_studio_automation import fl_studio_pyautogui_automation

# Create automation instance
fl = fl_studio_pyautogui_automation.FLStudioWorkflows()

# Launch FL Studio
fl.launch()

# Create and setup project
fl.create_new_project("AI Music Project")

# Adjust mixer volumes
fl.adjust_mixer_volume(track=0, volume=0.8)
fl.adjust_mixer_volume(track=1, volume=0.6)

# Save project
fl.save_project("output/fl_projects/my_project.flp")
```

### CLI-based FL Studio Control

```bash
# Start FL Studio
python src/fl_studio_automation/cli.py launch

# Create project
python src/fl_studio_automation/cli.py create-project "My Project"

# Adjust mixer
python src/fl_studio_automation/cli.py mixer --track 0 --volume 0.8

# Save
python src/fl_studio_automation/cli.py save "output/projects/myproject.flp"
```

## Agent-Driven Workflows

### Example 1: Simple Audio to MIDI + FL Studio

```python
from workflow import WorkflowOrchestrator

orchestrator = WorkflowOrchestrator(
    model_name="mistral",
    ollama_url="http://localhost:11434"
)

# Let the agent handle everything
result = orchestrator.start(
    "Convert audio.mp3 to MIDI and add it to FL Studio on track 1"
)

print(result)
```

### Example 2: Batch Processing with Agent

```python
# Process multiple files
result = orchestrator.start(
    """
    Convert all MP3 files in ./music/ to MIDI.
    Add each MIDI file to FL Studio on separate tracks.
    Set volumes to 80% for all tracks.
    Save the project as 'Batch_Project.flp'
    """
)
```

### Example 3: Advanced Music Production

```python
# Complex workflow
result = orchestrator.start(
    """
    1. Convert vocals.mp3, drums.wav, and bass.flac to MIDI
    2. Create a new FL Studio project called 'AI Remix'
    3. Add vocals MIDI to track 1 (volume 90%)
    4. Add drums MIDI to track 2 (volume 100%)
    5. Add bass MIDI to track 3 (volume 70%)
    6. Adjust the mixer to balance the tracks
    7. Save the project
    8. Take a screenshot of the final setup
    """
)
```

### Example 4: Async Workflow

```python
import asyncio

async def process_music():
    orchestrator = WorkflowOrchestrator()

    result = await orchestrator.start_async(
        "Convert song.mp3 to MIDI and create an FL Studio project"
    )

    return result

result = asyncio.run(process_music())
```

## Advanced Use Cases

### Use Case 1: Audio Enhancement Pipeline

```python
from audio_to_midi import AudioProcessor, AudioToMIDIConverter
from workflow import WorkflowOrchestrator

# Setup
processor = AudioProcessor()
converter = AudioToMIDIConverter()
orchestrator = WorkflowOrchestrator()

# 1. Enhance audio
enhanced = processor.enhance_for_midi(
    "raw_vocals.mp3",
    "enhanced_vocals.wav",
    normalize=True,
    remove_silence=True
)

# 2. Convert to MIDI
midi_result = converter.convert(
    enhanced,
    "output/midi"
)

# 3. Let agent add to FL Studio
orchestrator.start(
    f"Add {midi_result['output_midi']} to FL Studio and configure it as vocals"
)
```

### Use Case 2: Multi-Track Production

```python
# Process multiple instrument tracks
tracks = {
    "vocals": "vocals.mp3",
    "guitar": "guitar.wav",
    "drums": "drums.flac",
    "bass": "bass.mp3"
}

# Convert all to MIDI
midi_files = {}
for name, audio_file in tracks.items():
    result = converter.convert(audio_file, "output/midi")
    midi_files[name] = result['output_midi']

# Use agent to arrange in FL Studio
prompt = f"""
Create an FL Studio project with these tracks:
- Vocals: {midi_files['vocals']} on track 1 (volume 85%)
- Guitar: {midi_files['guitar']} on track 2 (volume 75%)
- Drums: {midi_files['drums']} on track 3 (volume 100%)
- Bass: {midi_files['bass']} on track 4 (volume 70%)

Balance the mixer and save as 'Multi_Track_Project.flp'
"""

orchestrator.start(prompt)
```

### Use Case 3: Automated A/B Testing

```python
# Test different conversion settings
settings_presets = [
    {"onset_threshold": 0.3, "frame_threshold": 0.2},
    {"onset_threshold": 0.5, "frame_threshold": 0.3},
    {"onset_threshold": 0.7, "frame_threshold": 0.4},
]

for i, settings in enumerate(settings_presets):
    result = converter.convert(
        "test_audio.mp3",
        f"output/midi/test_{i}",
        **settings
    )

    # Add to FL Studio for comparison
    orchestrator.start(
        f"Add {result['output_midi']} to FL Studio on track {i+1}"
    )

orchestrator.start("Save project as 'AB_Test.flp'")
```

### Use Case 4: Watch Folder Automation

```python
import time
import os
from pathlib import Path

# Watch folder for new audio files
watch_folder = Path("./incoming_audio")
processed_folder = Path("./processed")

while True:
    for audio_file in watch_folder.glob("*.mp3"):
        print(f"Processing: {audio_file}")

        # Convert to MIDI
        result = converter.convert(
            str(audio_file),
            "output/midi"
        )

        # Add to FL Studio
        orchestrator.start(
            f"Add {result['output_midi']} to current FL Studio project"
        )

        # Move to processed folder
        audio_file.rename(processed_folder / audio_file.name)

    time.sleep(5)  # Check every 5 seconds
```

### Use Case 5: API Integration

```python
from fastapi import FastAPI, UploadFile
from workflow import WorkflowOrchestrator
import shutil

app = FastAPI()
orchestrator = WorkflowOrchestrator()

@app.post("/convert-and-add")
async def convert_and_add(file: UploadFile):
    # Save uploaded file
    file_path = f"temp/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Process with agent
    result = await orchestrator.start_async(
        f"Convert {file_path} to MIDI and add to FL Studio"
    )

    return {"status": "success", "result": result}

# Run with: uvicorn api:app --reload
```

## Command Line Examples

### Start/Stop Workflow

```bash
# Start workflow
python src/main.py start --prompt "Convert audio.mp3 to MIDI"

# Check status (in another terminal)
python src/main.py status

# Stop workflow
python src/main.py stop
```

### Using Different Models

```bash
# Use Llama2
python src/main.py start --prompt "Process files" --model llama2

# Use CodeLlama for technical tasks
python src/main.py start --prompt "Debug conversion" --model codellama
```

### Async Mode

```bash
# Run in async mode for better responsiveness
python src/main.py start --prompt "Batch process" --async-mode
```

## Troubleshooting Examples

### Debug Conversion Issues

```python
# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)

converter = AudioToMIDIConverter()
result = converter.convert("problem_audio.mp3", "output/midi")

# Check result details
print("Success:", result['success'])
if not result['success']:
    print("Error:", result.get('error'))
else:
    print("MIDI info:", result['midi_info'])
```

### Test Ollama Connection

```bash
# Test if Ollama is accessible
python src/main.py test-ollama

# Test with specific model
python src/main.py test-ollama --model mistral
```

### Verify FL Studio Automation

```python
# Test FL Studio automation
from fl_studio_automation import fl_studio_pyautogui_automation

fl = fl_studio_pyautogui_automation.FLStudioAutomation()

# Check if FL Studio is running
if fl.is_running():
    print("FL Studio is running")
else:
    print("FL Studio is not running")
    fl.launch()
```

## Performance Tips

### Optimize Batch Processing

```python
# Use parallel processing for large batches
from workflow import WorkflowOrchestrator

orchestrator = WorkflowOrchestrator()

# Process files in parallel (up to 5 concurrent)
audio_files = ["track1.mp3", "track2.mp3", "track3.mp3",
               "track4.mp3", "track5.mp3"]

result = orchestrator.process_audio_batch(
    audio_files,
    add_to_fl_studio=True
)
```

### Cache Conversion Results

```python
# Cache MIDI conversions to avoid reprocessing
import hashlib
import json
from pathlib import Path

cache_file = "conversion_cache.json"

def get_file_hash(filepath):
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

# Load cache
cache = {}
if Path(cache_file).exists():
    with open(cache_file, 'r') as f:
        cache = json.load(f)

# Check cache before converting
audio_hash = get_file_hash("audio.mp3")
if audio_hash in cache:
    print("Using cached MIDI:", cache[audio_hash])
else:
    result = converter.convert("audio.mp3", "output/midi")
    cache[audio_hash] = result['output_midi']
    with open(cache_file, 'w') as f:
        json.dump(cache, f)
```

## Next Steps

- Review [API Documentation](API.md) for detailed API reference
- Check [Configuration](CONFIGURATION.md) for advanced settings
- See [Troubleshooting](TROUBLESHOOTING.md) for common issues
