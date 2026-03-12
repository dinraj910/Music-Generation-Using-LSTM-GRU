"""
MIDI Utilities for Neural Music Generation
==========================================
Handles MIDI file creation and audio conversion.
"""

import os


class MIDIGenerator:
    """
    Converts token sequences to MIDI files.
    """
    
    def __init__(self, config):
        """
        Initialize MIDI generator.
        
        Args:
            config: Configuration dictionary with MIDI_MIN, REST_TOKEN, etc.
        """
        self.config = config
        self.midi_min = config.get('MIDI_MIN', 21)
        self.midi_max = config.get('MIDI_MAX', 108)
        self.rest_token = config.get('REST_TOKEN', 88)
        
        # Try to import pretty_midi, use fallback if not available
        try:
            import pretty_midi
            self.pretty_midi = pretty_midi
            self.use_pretty_midi = True
            print("✅ pretty_midi available for MIDI generation")
        except ImportError:
            self.use_pretty_midi = False
            print("⚠️  pretty_midi not available, using midiutil fallback")
            try:
                from midiutil import MIDIFile
                self.MIDIFile = MIDIFile
            except ImportError:
                raise ImportError("Neither pretty_midi nor midiutil is installed. "
                                "Install with: pip install pretty_midi or pip install midiutil")
    
    def token_to_pitch(self, token):
        """Convert token to MIDI pitch."""
        if token == self.rest_token:
            return None
        return token + self.midi_min
    
    def tokens_to_midi(self, tokens, output_path, tempo_bpm=120, note_duration=0.25):
        """
        Convert token sequence to MIDI file.
        
        Args:
            tokens: List of token indices
            output_path: Path to save .mid file
            tempo_bpm: Beats per minute
            note_duration: Duration of each note in seconds
        
        Returns:
            Duration of the piece in seconds
        """
        if self.use_pretty_midi:
            return self._tokens_to_midi_pretty(tokens, output_path, tempo_bpm, note_duration)
        else:
            return self._tokens_to_midi_midiutil(tokens, output_path, tempo_bpm, note_duration)
    
    def _tokens_to_midi_pretty(self, tokens, output_path, tempo_bpm=120, note_duration=0.25):
        """Create MIDI using pretty_midi library."""
        midi = self.pretty_midi.PrettyMIDI(initial_tempo=tempo_bpm)
        piano = self.pretty_midi.Instrument(
            program=self.pretty_midi.instrument_name_to_program('Acoustic Grand Piano')
        )
        
        current_time = 0.0
        
        for token in tokens:
            if token == self.rest_token:
                # REST: advance time without adding note
                current_time += note_duration
            else:
                midi_pitch = self.token_to_pitch(token)
                if midi_pitch is None:
                    current_time += note_duration
                    continue
                
                # Clip to valid MIDI range
                midi_pitch = max(0, min(127, midi_pitch))
                
                note_on = current_time
                note_off = current_time + note_duration * 0.9  # Small gap between notes
                
                note_obj = self.pretty_midi.Note(
                    velocity=80,
                    pitch=midi_pitch,
                    start=note_on,
                    end=note_off
                )
                piano.notes.append(note_obj)
                current_time += note_duration
        
        midi.instruments.append(piano)
        midi.write(output_path)
        
        return current_time
    
    def _tokens_to_midi_midiutil(self, tokens, output_path, tempo_bpm=120, note_duration=0.25):
        """Create MIDI using midiutil library (fallback)."""
        midi = self.MIDIFile(1)  # One track
        track = 0
        channel = 0
        time = 0
        volume = 80
        
        midi.addTempo(track, 0, tempo_bpm)
        midi.addProgramChange(track, channel, 0, 0)  # Piano
        
        # Convert note_duration from seconds to beats
        beats_per_second = tempo_bpm / 60
        duration_beats = note_duration * beats_per_second
        
        current_beat = 0
        
        for token in tokens:
            if token == self.rest_token:
                current_beat += duration_beats
            else:
                midi_pitch = self.token_to_pitch(token)
                if midi_pitch is None:
                    current_beat += duration_beats
                    continue
                
                midi_pitch = max(0, min(127, midi_pitch))
                
                midi.addNote(
                    track=track,
                    channel=channel,
                    pitch=midi_pitch,
                    time=current_beat,
                    duration=duration_beats * 0.9,
                    volume=volume
                )
                current_beat += duration_beats
        
        with open(output_path, 'wb') as f:
            midi.writeFile(f)
        
        return current_beat / beats_per_second
    
    def notes_to_midi(self, notes, output_path, tempo_bpm=120, note_duration=0.25):
        """
        Convert note names directly to MIDI file.
        
        Args:
            notes: List of note names ['C4', 'E4', 'REST', ...]
            output_path: Path to save .mid file
            tempo_bpm: Beats per minute
            note_duration: Duration per note
        
        Returns:
            Duration in seconds
        """
        # Convert notes to tokens first
        tokens = []
        for note in notes:
            note = note.strip().upper()
            if note == 'REST':
                tokens.append(self.rest_token)
            else:
                midi_pitch = self._note_name_to_midi(note)
                if midi_pitch is not None:
                    tokens.append(midi_pitch - self.midi_min)
        
        return self.tokens_to_midi(tokens, output_path, tempo_bpm, note_duration)
    
    def _note_name_to_midi(self, note_name):
        """Convert note name to MIDI number."""
        NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        note_name = note_name.strip().upper()
        
        # Handle flats
        note_name = note_name.replace('DB', 'C#').replace('EB', 'D#')
        note_name = note_name.replace('GB', 'F#').replace('AB', 'G#')
        note_name = note_name.replace('BB', 'A#')
        
        try:
            if '#' in note_name:
                note = note_name[:2]
                octave = int(note_name[2:])
            else:
                note = note_name[0]
                octave = int(note_name[1:])
            
            note_idx = NOTE_NAMES.index(note)
            midi_pitch = (octave + 1) * 12 + note_idx
            return midi_pitch
        except (ValueError, IndexError):
            return None


# For testing
if __name__ == '__main__':
    config = {
        'MIDI_MIN': 21,
        'MIDI_MAX': 108,
        'REST_TOKEN': 88,
        'VOCAB_SIZE': 89
    }
    
    generator = MIDIGenerator(config)
    
    # Test token generation
    test_tokens = [39, 43, 46, 88, 39, 43, 46, 51]  # C4, E4, G4, REST, C4, E4, G4, C5
    duration = generator.tokens_to_midi(test_tokens, 'test_output.mid')
    print(f"Created test MIDI file, duration: {duration:.2f}s")
    
    # Test note name generation
    test_notes = ['C4', 'E4', 'G4', 'REST', 'C5', 'G4', 'E4', 'C4']
    duration = generator.notes_to_midi(test_notes, 'test_notes.mid')
    print(f"Created test notes MIDI file, duration: {duration:.2f}s")
    
    print("✅ MIDI generation tests passed")
