"""Main audio to MIDI converter using Basic-Pitch and librosa."""

import os
from pathlib import Path
from typing import Optional, Dict, Any

# Optional audio processing imports
try:
    import numpy as np
    from basic_pitch.inference import predict_and_save
    from basic_pitch import ICASSP_2022_MODEL_PATH
    import librosa
    import pretty_midi
    AUDIO_DEPS_AVAILABLE = True
except ImportError:
    AUDIO_DEPS_AVAILABLE = False
    # Provide dummy values for when dependencies aren't installed
    ICASSP_2022_MODEL_PATH = None


class AudioToMIDIConverter:
    """Convert audio files to MIDI using open source ML models."""

    def __init__(self, model_path: Optional[str] = None):
        """Initialize converter with optional custom model path.

        Args:
            model_path: Path to Basic-Pitch model (uses default if None)
        """
        self.model_path = model_path or ICASSP_2022_MODEL_PATH

    def convert(
        self,
        audio_path: str,
        output_dir: str,
        onset_threshold: float = 0.5,
        frame_threshold: float = 0.3,
        minimum_note_length: float = 127.70,
        minimum_frequency: Optional[float] = None,
        maximum_frequency: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Convert audio file to MIDI.

        Args:
            audio_path: Path to input audio file
            output_dir: Directory for output MIDI file
            onset_threshold: Threshold for note onset detection
            frame_threshold: Threshold for frame-level note detection
            minimum_note_length: Minimum note length in milliseconds
            minimum_frequency: Minimum frequency in Hz (optional)
            maximum_frequency: Maximum frequency in Hz (optional)

        Returns:
            Dict containing paths and metadata
        """
        if not AUDIO_DEPS_AVAILABLE:
            return {
                "success": False,
                "error": "Audio processing dependencies not installed. Install with: pip install basic-pitch librosa pretty_midi"
            }

        audio_path = Path(audio_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Use Basic-Pitch for conversion
        model_output, midi_data, note_events = predict_and_save(
            audio_path_list=[audio_path],
            output_directory=output_dir,
            save_midi=True,
            sonify_midi=False,
            save_model_outputs=False,
            save_notes=False,
            model_or_model_path=self.model_path,
            onset_threshold=onset_threshold,
            frame_threshold=frame_threshold,
            minimum_note_length=minimum_note_length,
            minimum_frequency=minimum_frequency,
            maximum_frequency=maximum_frequency,
        )

        # Get output MIDI file path
        midi_filename = audio_path.stem + "_basic_pitch.mid"
        midi_path = output_dir / midi_filename

        # Load and analyze the MIDI
        midi_info = self._analyze_midi(str(midi_path))

        return {
            "input_audio": str(audio_path),
            "output_midi": str(midi_path),
            "midi_info": midi_info,
            "success": midi_path.exists()
        }

    def _analyze_midi(self, midi_path: str) -> Dict[str, Any]:
        """Analyze MIDI file and return metadata.

        Args:
            midi_path: Path to MIDI file

        Returns:
            Dict with MIDI metadata
        """
        try:
            midi_data = pretty_midi.PrettyMIDI(midi_path)

            return {
                "duration": midi_data.get_end_time(),
                "tempo_changes": len(midi_data.get_tempo_changes()[0]),
                "num_instruments": len(midi_data.instruments),
                "total_notes": sum(len(inst.notes) for inst in midi_data.instruments),
                "time_signature_changes": len(midi_data.time_signature_changes),
            }
        except Exception as e:
            return {"error": str(e)}

    def convert_batch(
        self,
        audio_files: list[str],
        output_dir: str,
        **kwargs
    ) -> list[Dict[str, Any]]:
        """Convert multiple audio files to MIDI.

        Args:
            audio_files: List of audio file paths
            output_dir: Output directory
            **kwargs: Additional arguments for convert()

        Returns:
            List of result dicts
        """
        results = []
        for audio_file in audio_files:
            try:
                result = self.convert(audio_file, output_dir, **kwargs)
                results.append(result)
            except Exception as e:
                results.append({
                    "input_audio": audio_file,
                    "error": str(e),
                    "success": False
                })
        return results
