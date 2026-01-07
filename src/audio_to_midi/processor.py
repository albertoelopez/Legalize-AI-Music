"""Audio pre-processing utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple, Any

# Optional audio processing imports
try:
    import librosa
    import soundfile as sf
    import numpy as np
    AUDIO_DEPS_AVAILABLE = True
except ImportError:
    AUDIO_DEPS_AVAILABLE = False


class AudioProcessor:
    """Pre-process audio files for optimal MIDI conversion."""

    def __init__(self, target_sr: int = 22050):
        """Initialize processor.

        Args:
            target_sr: Target sample rate for processing
        """
        self.target_sr = target_sr

    def load_audio(
        self,
        audio_path: str,
        sr: Optional[int] = None,
        mono: bool = True
    ) -> Tuple[np.ndarray, int]:
        """Load audio file.

        Args:
            audio_path: Path to audio file
            sr: Target sample rate (uses default if None)
            mono: Convert to mono

        Returns:
            Tuple of (audio_data, sample_rate)
        """
        sr = sr or self.target_sr
        audio, sample_rate = librosa.load(audio_path, sr=sr, mono=mono)
        return audio, sample_rate

    def normalize_audio(self, audio: np.ndarray) -> np.ndarray:
        """Normalize audio to [-1, 1] range.

        Args:
            audio: Audio data

        Returns:
            Normalized audio
        """
        max_val = np.abs(audio).max()
        if max_val > 0:
            return audio / max_val
        return audio

    def remove_silence(
        self,
        audio: np.ndarray,
        sr: int,
        top_db: int = 30
    ) -> np.ndarray:
        """Remove silence from audio.

        Args:
            audio: Audio data
            sr: Sample rate
            top_db: Threshold in decibels

        Returns:
            Audio with silence removed
        """
        non_silent_intervals = librosa.effects.split(audio, top_db=top_db)

        # Concatenate non-silent parts
        if len(non_silent_intervals) > 0:
            audio_trimmed = np.concatenate([
                audio[start:end] for start, end in non_silent_intervals
            ])
            return audio_trimmed
        return audio

    def enhance_for_midi(
        self,
        audio_path: str,
        output_path: str,
        normalize: bool = True,
        remove_silence: bool = True,
    ) -> str:
        """Enhance audio file for better MIDI conversion.

        Args:
            audio_path: Input audio path
            output_path: Output audio path
            normalize: Whether to normalize
            remove_silence: Whether to remove silence

        Returns:
            Path to enhanced audio file
        """
        # Load audio
        audio, sr = self.load_audio(audio_path)

        # Enhance
        if normalize:
            audio = self.normalize_audio(audio)

        if remove_silence:
            audio = self.remove_silence(audio, sr)

        # Save enhanced audio
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        sf.write(output_path, audio, sr)

        return str(output_path)

    def get_audio_info(self, audio_path: str) -> dict:
        """Get audio file information.

        Args:
            audio_path: Path to audio file

        Returns:
            Dict with audio metadata
        """
        audio, sr = self.load_audio(audio_path)

        return {
            "duration": librosa.get_duration(y=audio, sr=sr),
            "sample_rate": sr,
            "n_samples": len(audio),
            "rms_energy": float(np.sqrt(np.mean(audio**2))),
            "max_amplitude": float(np.abs(audio).max()),
        }
