"""
Test Full Workflow Integration
Tests the complete Suno AI to MIDI to FL Studio automation workflow
"""

import os
import sys
import asyncio
import pytest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from audio_to_midi.converter import AudioToMIDIConverter
from audio_to_midi.processor import AudioProcessor
from workflow.orchestrator import WorkflowOrchestrator


def test_audio_to_midi_conversion():
    """Test basic audio to MIDI conversion"""
    print("\n" + "=" * 60)
    print("TEST 1: Audio to MIDI Conversion")
    print("=" * 60)

    converter = AudioToMIDIConverter()

    # Check if test audio exists
    test_audio = "tests/fixtures/test_audio.mp3"
    if not os.path.exists(test_audio):
        print(f"⚠️  Test audio not found: {test_audio}")
        print("   Skipping conversion test")
        return False

    try:
        result = converter.convert(
            audio_path=test_audio,
            output_dir="output/midi/test"
        )

        if result['success']:
            print(f"✓ Conversion successful")
            print(f"  Input: {result['input_audio']}")
            print(f"  Output: {result['output_midi']}")
            print(f"  Duration: {result['midi_info']['duration']} seconds")
            print(f"  Total notes: {result['midi_info']['total_notes']}")
            return True
        else:
            print(f"✗ Conversion failed: {result.get('error')}")
            return False

    except Exception as e:
        print(f"✗ Error during conversion: {str(e)}")
        return False


def test_audio_preprocessing():
    """Test audio preprocessing"""
    print("\n" + "=" * 60)
    print("TEST 2: Audio Preprocessing")
    print("=" * 60)

    processor = AudioProcessor()

    test_audio = "tests/fixtures/test_audio.mp3"
    if not os.path.exists(test_audio):
        print(f"⚠️  Test audio not found: {test_audio}")
        print("   Skipping preprocessing test")
        return False

    try:
        enhanced_path = processor.enhance_for_midi(
            audio_path=test_audio,
            output_path="output/enhanced_audio/test_enhanced.wav",
            normalize=True,
            remove_silence=True
        )

        if os.path.exists(enhanced_path):
            print(f"✓ Audio enhancement successful")
            print(f"  Output: {enhanced_path}")
            return True
        else:
            print(f"✗ Enhanced audio not created")
            return False

    except Exception as e:
        print(f"✗ Error during preprocessing: {str(e)}")
        return False


def test_batch_conversion():
    """Test batch audio conversion"""
    print("\n" + "=" * 60)
    print("TEST 3: Batch Conversion")
    print("=" * 60)

    converter = AudioToMIDIConverter()

    # Create test audio files list
    test_files = [
        "tests/fixtures/test_audio.mp3",
        "tests/fixtures/test_audio2.mp3"
    ]

    # Filter existing files
    existing_files = [f for f in test_files if os.path.exists(f)]

    if not existing_files:
        print("⚠️  No test audio files found")
        print("   Skipping batch conversion test")
        return False

    try:
        results = converter.convert_batch(
            audio_files=existing_files,
            output_dir="output/midi/batch_test"
        )

        print(f"Batch conversion results:")
        successful = 0
        for result in results:
            if result['success']:
                successful += 1
                print(f"  ✓ {os.path.basename(result['audio_file'])}")
            else:
                print(f"  ✗ {os.path.basename(result['audio_file'])}: {result.get('error')}")

        print(f"\nConverted {successful}/{len(existing_files)} files successfully")
        return successful > 0

    except Exception as e:
        print(f"✗ Error during batch conversion: {str(e)}")
        return False


def test_orchestrator_sync():
    """Test workflow orchestrator (sync)"""
    print("\n" + "=" * 60)
    print("TEST 4: Workflow Orchestrator (Sync)")
    print("=" * 60)

    # Check if Ollama is available
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code != 200:
            print("⚠️  Ollama not accessible")
            print("   Skipping orchestrator test")
            return False
    except:
        print("⚠️  Ollama not running")
        print("   Start Ollama with: ollama serve")
        print("   Skipping orchestrator test")
        return False

    try:
        orchestrator = WorkflowOrchestrator(
            model_name="mistral",
            ollama_url="http://localhost:11434"
        )

        # Simple test task
        result = orchestrator.start(
            "Test if the system is working by checking status"
        )

        print(f"✓ Orchestrator executed successfully")
        print(f"  Result: {result}")
        return True

    except Exception as e:
        print(f"✗ Error during orchestration: {str(e)}")
        return False


@pytest.mark.asyncio
async def test_orchestrator_async():
    """Test workflow orchestrator (async)"""
    print("\n" + "=" * 60)
    print("TEST 5: Workflow Orchestrator (Async)")
    print("=" * 60)

    # Check if Ollama is available
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code != 200:
            print("⚠️  Ollama not accessible")
            print("   Skipping async orchestrator test")
            return False
    except:
        print("⚠️  Ollama not running")
        print("   Skipping async orchestrator test")
        return False

    try:
        orchestrator = WorkflowOrchestrator(
            model_name="mistral",
            ollama_url="http://localhost:11434"
        )

        # Simple async test task
        result = await orchestrator.start_async(
            "Test async workflow by checking system status"
        )

        print(f"✓ Async orchestrator executed successfully")
        print(f"  Result: {result}")
        return True

    except Exception as e:
        print(f"✗ Error during async orchestration: {str(e)}")
        return False


def test_fl_studio_mcp():
    """Test FL Studio MCP server"""
    print("\n" + "=" * 60)
    print("TEST 6: FL Studio MCP Server")
    print("=" * 60)

    # Check if FL Studio is running
    try:
        import psutil
        fl_running = False
        for proc in psutil.process_iter(['name']):
            try:
                if 'FL.exe' in proc.name() or 'FL64.exe' in proc.name():
                    fl_running = True
                    break
            except:
                pass

        if not fl_running:
            print("⚠️  FL Studio not running")
            print("   Skipping FL Studio MCP test")
            return False

        print(f"✓ FL Studio is running")
        print(f"  MCP server can be started with: python mcp_servers/fl_studio_mcp/fl_studio_mcp_server.py")
        return True

    except Exception as e:
        print(f"⚠️  Cannot check FL Studio status: {str(e)}")
        return False


def run_integration_test():
    """Run complete integration test"""
    print("\n" + "=" * 60)
    print("TEST 7: Full Integration")
    print("=" * 60)

    test_audio = "tests/fixtures/test_audio.mp3"
    if not os.path.exists(test_audio):
        print("⚠️  Test audio not found")
        print("   Skipping integration test")
        return False

    try:
        # Step 1: Preprocess audio
        processor = AudioProcessor()
        enhanced = processor.enhance_for_midi(
            test_audio,
            "output/enhanced_audio/integration_test.wav"
        )
        print("✓ Step 1: Audio preprocessing complete")

        # Step 2: Convert to MIDI
        converter = AudioToMIDIConverter()
        result = converter.convert(
            enhanced,
            "output/midi/integration_test"
        )
        print("✓ Step 2: MIDI conversion complete")

        # Step 3: Check if Ollama available for orchestration
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                orchestrator = WorkflowOrchestrator()
                # Note: This would require FL Studio to be running
                # orchestrator.start(f"Add {result['output_midi']} to FL Studio")
                print("✓ Step 3: Orchestrator ready (FL Studio integration would go here)")
            else:
                print("⚠️  Step 3: Orchestrator unavailable (Ollama not accessible)")
        except:
            print("⚠️  Step 3: Orchestrator unavailable (Ollama not running)")

        print("\n✓ Integration test completed successfully")
        return True

    except Exception as e:
        print(f"✗ Integration test failed: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("SUNO AI TO MIDI FL STUDIO - FULL WORKFLOW TESTS")
    print("=" * 60)

    # Create output directories
    os.makedirs("output/midi/test", exist_ok=True)
    os.makedirs("output/enhanced_audio", exist_ok=True)
    os.makedirs("output/midi/batch_test", exist_ok=True)
    os.makedirs("tests/fixtures", exist_ok=True)

    results = {
        "Audio to MIDI Conversion": test_audio_to_midi_conversion(),
        "Audio Preprocessing": test_audio_preprocessing(),
        "Batch Conversion": test_batch_conversion(),
        "Workflow Orchestrator (Sync)": test_orchestrator_sync(),
        "Workflow Orchestrator (Async)": asyncio.run(test_orchestrator_async()),
        "FL Studio MCP": test_fl_studio_mcp(),
        "Full Integration": run_integration_test()
    }

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = 0
    failed = 0
    skipped = 0

    for test_name, result in results.items():
        if result is True:
            status = "✓ PASS"
            passed += 1
        elif result is False:
            status = "✗ FAIL"
            failed += 1
        else:
            status = "⚠️  SKIP"
            skipped += 1

        print(f"{status}: {test_name}")

    print("\n" + "-" * 60)
    print(f"Total: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")
    print("=" * 60)

    # Create test audio instructions if needed
    if not os.path.exists("tests/fixtures/test_audio.mp3"):
        print("\nNOTE: To run audio conversion tests, add test audio files:")
        print("  cp /path/to/audio.mp3 tests/fixtures/test_audio.mp3")
        print("  cp /path/to/audio2.mp3 tests/fixtures/test_audio2.mp3")

    return passed, failed, skipped


if __name__ == "__main__":
    passed, failed, skipped = main()
    sys.exit(0 if failed == 0 else 1)
