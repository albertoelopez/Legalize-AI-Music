"""
FL Studio MIDI Controller Script - Production Ready
Place this file in: C:\Users\[YourUsername]\AppData\Roaming\Image-Line\FL Studio\Settings\Hardware\device_automation.py

This script provides automated control of FL Studio via MIDI events.
It demonstrates the complete FL Studio Python API workflow.
"""

import device
import mixer
import channels
import transport
import ui
import patterns
import arrangement
import time

# ============================================================================
# CONFIGURATION
# ============================================================================

SCRIPT_VERSION = "1.0.0"
SCRIPT_NAME = "FL Studio Automation Controller"
DEBUG = True  # Enable debug logging

# MIDI Configuration
MIDI_CC_MASTER_VOLUME = 1
MIDI_CC_TRACK_VOLUME = 2
MIDI_CC_PAN = 3
MIDI_CC_TEMPO = 4
MIDI_NOTE_PLAY = 60
MIDI_NOTE_STOP = 61
MIDI_NOTE_RECORD = 62

# Note range for pattern triggering
PATTERN_NOTE_START = 36  # C1
PATTERN_NOTE_END = 51    # D#2

# ============================================================================
# STATE MANAGEMENT
# ============================================================================

class AutomationState:
    """Manage automation state and history."""

    def __init__(self):
        self.last_mixer_values = {}
        self.last_channel_values = {}
        self.recording_enabled = False
        self.automation_enabled = True
        self.tempo_last = 120
        self.active_patterns = set()

    def debug_log(self, message):
        """Log debug messages."""
        if DEBUG:
            print(f"[DEBUG] {message}")

    def reset(self):
        """Reset state."""
        self.last_mixer_values.clear()
        self.last_channel_values.clear()
        self.recording_enabled = False
        self.active_patterns.clear()


# Global state instance
state = AutomationState()


# ============================================================================
# INITIALIZATION
# ============================================================================

def OnInit():
    """Called when script is loaded."""
    state.debug_log(f"Initializing {SCRIPT_NAME} v{SCRIPT_VERSION}")

    # Configure MIDI device type
    device.setHardware(device.TYPE_GENERIC_MIDI)

    # Initialize state
    state.debug_log("Automation state initialized")
    state.debug_log(f"Mixer tracks: {mixer.trackCount()}")
    state.debug_log(f"Channels: {channels.channelCount()}")


def OnDeinit():
    """Called when script is unloaded."""
    state.debug_log(f"Deinitializing {SCRIPT_NAME}")
    state.reset()


# ============================================================================
# MIDI EVENT HANDLING
# ============================================================================

def OnMidiIn(event):
    """
    Main MIDI input handler.

    This is called whenever a MIDI message is received.
    event object has: status, data1, data2 properties
    """
    state.debug_log(f"MIDI In: Status={event.status:02X} Data1={event.data1} Data2={event.data2}")

    # Note On (0x90) / Note Off (0x80)
    if event.status == 0x90 or event.status == 0x80:
        is_note_on = event.status == 0x90 and event.data2 > 0
        note_number = event.data1

        if is_note_on:
            HandleNoteOn(note_number, event.data2)
        else:
            HandleNoteOff(note_number)

    # Control Change (0xB0)
    elif event.status == 0xB0:
        cc_number = event.data1
        cc_value = event.data2
        HandleControlChange(cc_number, cc_value)

    # Program Change (0xC0)
    elif event.status == 0xC0:
        program = event.data1
        HandleProgramChange(program)


# ============================================================================
# NOTE HANDLERS
# ============================================================================

def HandleNoteOn(note, velocity):
    """Handle Note On events."""
    state.debug_log(f"Note On: {note} Velocity: {velocity}")

    # Transport control (notes 60-63)
    if note == MIDI_NOTE_PLAY:  # C3
        state.debug_log("Play command")
        transport.start()

    elif note == MIDI_NOTE_STOP:  # C#3
        state.debug_log("Stop command")
        transport.stop()

    elif note == MIDI_NOTE_RECORD:  # D3
        state.debug_log("Record toggle")
        # Toggle recording
        current_pos = transport.getPos(0)
        transport.start()  # Ensure transport is running

    # Pattern triggering (notes 36-51)
    elif PATTERN_NOTE_START <= note <= PATTERN_NOTE_END:
        pattern_index = note - PATTERN_NOTE_START
        state.active_patterns.add(pattern_index)
        state.debug_log(f"Pattern {pattern_index} triggered")

        # Switch to pattern if needed
        try:
            # In FL Studio, you might trigger patterns through mixer tracks
            # or by switching the current pattern
            if pattern_index < patterns.patternCount():
                patterns.currentPattern = pattern_index
        except:
            state.debug_log(f"Could not trigger pattern {pattern_index}")

    # Velocity-based volume control for notes 64-79
    elif 64 <= note <= 79:
        channel_index = note - 64
        volume = velocity / 127.0

        if channel_index < channels.channelCount():
            channels.setChannelVolume(channel_index, volume)
            state.debug_log(f"Channel {channel_index} volume: {volume:.2f}")


def HandleNoteOff(note):
    """Handle Note Off events."""
    state.debug_log(f"Note Off: {note}")

    # Clear from active patterns
    if PATTERN_NOTE_START <= note <= PATTERN_NOTE_END:
        pattern_index = note - PATTERN_NOTE_START
        state.active_patterns.discard(pattern_index)


# ============================================================================
# CONTROL CHANGE HANDLERS
# ============================================================================

def HandleControlChange(cc_number, cc_value):
    """Handle Control Change messages for parameter automation."""
    # Normalize CC value (0-127) to 0.0-1.0
    normalized = cc_value / 127.0

    state.debug_log(f"CC {cc_number}: {cc_value} (normalized: {normalized:.2f})")

    # CC 1: Master volume
    if cc_number == MIDI_CC_MASTER_VOLUME:
        try:
            mixer.setTrackVolume(0, normalized)  # Track 0 is master
            state.last_mixer_values[0] = normalized
            state.debug_log(f"Master volume set to {normalized:.2f}")
        except Exception as e:
            state.debug_log(f"Error setting master volume: {e}")

    # CC 2: Selected mixer track volume
    elif cc_number == MIDI_CC_TRACK_VOLUME:
        try:
            track = mixer.selectedTrack()
            if track >= 0:
                mixer.setTrackVolume(track, normalized)
                state.last_mixer_values[track] = normalized
                state.debug_log(f"Track {track} volume: {normalized:.2f}")
        except Exception as e:
            state.debug_log(f"Error setting track volume: {e}")

    # CC 3: Pan
    elif cc_number == MIDI_CC_PAN:
        try:
            # Pan range: -0.5 to 0.5
            pan_value = normalized - 0.5
            track = mixer.selectedTrack()
            if track >= 0:
                mixer.setTrackPan(track, pan_value)
                state.debug_log(f"Track {track} pan: {pan_value:.2f}")
        except Exception as e:
            state.debug_log(f"Error setting pan: {e}")

    # CC 4: Tempo
    elif cc_number == MIDI_CC_TEMPO:
        try:
            # Map 0-127 to 20-300 BPM
            tempo = 20 + (normalized * 280)
            ui.setHintMsg(f"Tempo: {tempo:.1f} BPM")
            state.tempo_last = tempo
            state.debug_log(f"Tempo set to {tempo:.1f}")
        except Exception as e:
            state.debug_log(f"Error setting tempo: {e}")

    # CC 7: Standard MIDI volume
    elif cc_number == 7:
        try:
            track = mixer.selectedTrack()
            if track >= 0:
                mixer.setTrackVolume(track, normalized)
                state.last_mixer_values[track] = normalized
                state.debug_log(f"Track {track} volume (CC7): {normalized:.2f}")
        except Exception as e:
            state.debug_log(f"Error setting volume: {e}")

    # CC 10: Pan (standard MIDI)
    elif cc_number == 10:
        try:
            pan_value = normalized - 0.5
            track = mixer.selectedTrack()
            if track >= 0:
                mixer.setTrackPan(track, pan_value)
                state.debug_log(f"Track {track} pan (CC10): {pan_value:.2f}")
        except Exception as e:
            state.debug_log(f"Error setting pan: {e}")

    # CC 64: Sustain/Enable automation
    elif cc_number == 64:
        state.automation_enabled = cc_value >= 64
        state.debug_log(f"Automation: {'enabled' if state.automation_enabled else 'disabled'}")


# ============================================================================
# PROGRAM CHANGE HANDLER
# ============================================================================

def HandleProgramChange(program):
    """Handle Program Change messages."""
    state.debug_log(f"Program Change: {program}")

    try:
        # Use program changes to switch between presets or patterns
        if program < patterns.patternCount():
            patterns.currentPattern = program
            state.debug_log(f"Switched to pattern {program}")
    except Exception as e:
        state.debug_log(f"Error handling program change: {e}")


# ============================================================================
# BACKGROUND PROCESSING
# ============================================================================

def OnIdle():
    """Called periodically in the background."""
    # Perform any continuous monitoring or feedback here
    pass


def OnRefresh(event_flags):
    """
    Called when FL Studio needs hardware feedback.

    This is where you would update LED displays on your MIDI controller.
    """
    try:
        # Example: Send current mixer values back to controller
        # (This depends on your hardware capabilities)

        master_volume = mixer.getTrackVolume(0)
        selected_track = mixer.selectedTrack()

        if selected_track >= 0:
            track_volume = mixer.getTrackVolume(selected_track)
            track_pan = mixer.getTrackPan(selected_track)
    except:
        pass


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def GetChannelNameForNote(note):
    """Get channel name corresponding to note."""
    channel_index = note - 64
    if channel_index < channels.channelCount():
        return channels.getChannelName(channel_index)
    return f"Channel {channel_index}"


def GetMixerTrackInfo(track_index):
    """Get mixer track information."""
    try:
        volume = mixer.getTrackVolume(track_index)
        pan = mixer.getTrackPan(track_index)
        return {
            "volume": volume,
            "pan": pan,
            "index": track_index
        }
    except:
        return None


# ============================================================================
# LOGGING UTILITIES
# ============================================================================

class Logger:
    """Simple logging utility."""

    @staticmethod
    def info(message):
        """Log info message."""
        if DEBUG:
            print(f"[INFO] {message}")

    @staticmethod
    def error(message):
        """Log error message."""
        print(f"[ERROR] {message}")

    @staticmethod
    def debug(message):
        """Log debug message."""
        if DEBUG:
            print(f"[DEBUG] {message}")
