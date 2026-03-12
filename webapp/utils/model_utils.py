"""
Model Utilities for Neural Music Generation
============================================
Handles model loading, tokenization, and music generation.
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow import keras


class ModelManager:
    """
    Manages LSTM, GRU, and BiLSTM models for music generation.
    Implements lazy loading to save memory.
    """
    
    # Note name to MIDI mapping
    NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    # Alternative note names
    NOTE_ALIASES = {
        'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#',
        'C♯': 'C#', 'D♯': 'D#', 'F♯': 'F#', 'G♯': 'G#', 'A♯': 'A#',
        'D♭': 'C#', 'E♭': 'D#', 'G♭': 'F#', 'A♭': 'G#', 'B♭': 'A#'
    }
    
    def __init__(self, model_dir, config):
        """
        Initialize the model manager.
        
        Args:
            model_dir: Directory containing model files
            config: Configuration dictionary with MIDI_MIN, MIDI_MAX, etc.
        """
        self.model_dir = model_dir
        self.config = config
        self._models = {}  # Cache for loaded models
        
        # Config values
        self.midi_min = config.get('MIDI_MIN', 21)
        self.midi_max = config.get('MIDI_MAX', 108)
        self.rest_token = config.get('REST_TOKEN', 88)
        self.vocab_size = config.get('VOCAB_SIZE', 89)
        self.seq_len = config.get('SEQ_LEN', 32)
        
        print(f"ModelManager initialized:")
        print(f"  Model directory: {model_dir}")
        print(f"  MIDI range: {self.midi_min}-{self.midi_max}")
        print(f"  Vocab size: {self.vocab_size}")
        print(f"  Sequence length: {self.seq_len}")
    
    def get_model(self, model_name):
        """
        Get a model, loading it if necessary (lazy loading).
        
        Args:
            model_name: 'lstm', 'gru', or 'bilstm'
        
        Returns:
            Loaded Keras model
        """
        if model_name not in self._models:
            self._models[model_name] = self._load_model(model_name)
        return self._models[model_name]
    
    def _load_model(self, model_name):
        """
        Load a model from disk.
        
        Args:
            model_name: 'lstm', 'gru', or 'bilstm'
        
        Returns:
            Loaded Keras model
        """
        # Try different model file locations
        model_paths = [
            os.path.join(self.model_dir, f'{model_name}_best.keras'),
            os.path.join(self.model_dir, model_name, f'{model_name}.keras'),
            os.path.join(self.model_dir, model_name, f'{model_name}.h5'),
        ]
        
        for path in model_paths:
            if os.path.exists(path):
                print(f"Loading model from: {path}")
                try:
                    model = keras.models.load_model(path)
                    print(f"✅ Model '{model_name}' loaded successfully")
                    return model
                except Exception as e:
                    print(f"⚠️  Failed to load {path}: {e}")
                    continue
        
        raise FileNotFoundError(f"Could not find model file for '{model_name}'")
    
    def get_models_info(self):
        """
        Get information about available models.
        
        Returns:
            Dictionary with model information
        """
        return {
            'lstm': {
                'name': 'Stacked LSTM',
                'description': 'Two-layer LSTM with 256 hidden units. Best for melodic sequences.',
                'can_generate': True,
                'recommended': True,
                'color': '#2196F3'
            },
            'gru': {
                'name': 'Stacked GRU',
                'description': 'Two-layer GRU with 256 hidden units. Faster, comparable quality.',
                'can_generate': True,
                'recommended': False,
                'color': '#4CAF50'
            },
            'bilstm': {
                'name': 'Bidirectional LSTM',
                'description': 'BiLSTM classifier. Cannot truly generate (uses future context).',
                'can_generate': False,
                'recommended': False,
                'color': '#FF5722'
            }
        }
    
    def pitch_to_token(self, midi_pitch):
        """Convert MIDI pitch (21-108) to token (0-87)."""
        return int(midi_pitch) - self.midi_min
    
    def token_to_pitch(self, token):
        """Convert token (0-87) to MIDI pitch (21-108)."""
        if token == self.rest_token:
            return None
        return token + self.midi_min
    
    def token_to_note_name(self, token):
        """
        Convert token to human-readable note name.
        
        Args:
            token: Token index (0-88)
        
        Returns:
            Note name like 'C4' or 'REST'
        """
        if token == self.rest_token:
            return 'REST'
        
        midi_pitch = self.token_to_pitch(token)
        if midi_pitch is None:
            return 'REST'
        
        octave = (midi_pitch // 12) - 1
        note = self.NOTE_NAMES[midi_pitch % 12]
        return f'{note}{octave}'
    
    def note_name_to_token(self, note_name):
        """
        Convert note name to token.
        
        Args:
            note_name: Note name like 'C4', 'F#5', 'REST'
        
        Returns:
            Token index
        """
        note_name = note_name.strip().upper()
        
        if note_name == 'REST':
            return self.rest_token
        
        # Handle aliases (Db -> C#, etc.)
        for alias, canonical in self.NOTE_ALIASES.items():
            note_name = note_name.replace(alias.upper(), canonical)
        
        # Parse note name
        if len(note_name) < 2:
            raise ValueError(f"Invalid note name: {note_name}")
        
        # Handle sharps
        if '#' in note_name or '♯' in note_name:
            note = note_name[:2].replace('♯', '#')
            octave = int(note_name[2:])
        else:
            note = note_name[0]
            octave = int(note_name[1:])
        
        # Find note index
        try:
            note_idx = self.NOTE_NAMES.index(note)
        except ValueError:
            raise ValueError(f"Unknown note: {note}")
        
        # Calculate MIDI pitch: C4 = 60
        midi_pitch = (octave + 1) * 12 + note_idx
        
        # Validate range
        if midi_pitch < self.midi_min or midi_pitch > self.midi_max:
            raise ValueError(f"Note {note_name} (MIDI {midi_pitch}) out of range [{self.midi_min}, {self.midi_max}]")
        
        return self.pitch_to_token(midi_pitch)
    
    def note_name_to_midi(self, note_name):
        """
        Convert note name to MIDI number.
        
        Args:
            note_name: Note name like 'C4', 'F#5'
        
        Returns:
            MIDI number (21-127)
        """
        note_name = note_name.strip().upper()
        
        if note_name == 'REST':
            return None
        
        # Handle aliases
        for alias, canonical in self.NOTE_ALIASES.items():
            note_name = note_name.replace(alias.upper(), canonical)
        
        # Parse note name
        if '#' in note_name:
            note = note_name[:2]
            octave = int(note_name[2:])
        else:
            note = note_name[0]
            octave = int(note_name[1:])
        
        note_idx = self.NOTE_NAMES.index(note)
        midi_pitch = (octave + 1) * 12 + note_idx
        return midi_pitch
    
    def notes_to_tokens(self, notes):
        """
        Convert list of note names to tokens.
        
        Args:
            notes: List of note names ['C4', 'E4', 'G4', ...]
        
        Returns:
            List of token indices
        """
        tokens = []
        for note in notes:
            try:
                token = self.note_name_to_token(note)
                tokens.append(token)
            except ValueError as e:
                print(f"Warning: {e}, skipping note")
                continue
        return tokens
    
    def tokens_to_notes(self, tokens):
        """
        Convert list of tokens to note names.
        
        Args:
            tokens: List of token indices
        
        Returns:
            List of note names
        """
        return [self.token_to_note_name(t) for t in tokens]
    
    def sample_with_temperature(self, probs, temperature=0.8):
        """
        Apply temperature scaling and sample from probability distribution.
        
        Args:
            probs: Probability distribution from model output
            temperature: Controls randomness (0.5=conservative, 1.0=standard, 1.5=creative)
        
        Returns:
            Sampled token index
        """
        if temperature == 0:
            return int(np.argmax(probs))
        
        # Take log and scale by temperature
        logits = np.log(np.array(probs, dtype=np.float64) + 1e-10)
        logits = logits / temperature
        
        # Numerical stability
        logits = logits - np.max(logits)
        
        # Convert back to probabilities
        exp_logits = np.exp(logits)
        probs = exp_logits / np.sum(exp_logits)
        
        # Sample
        return int(np.random.choice(len(probs), p=probs))
    
    def generate_sequence(self, model, seed_tokens, length=100, temperature=0.8):
        """
        Autoregressively generate a sequence of notes.
        
        Args:
            model: Loaded Keras model
            seed_tokens: Initial sequence of tokens (must be SEQ_LEN long)
            length: Number of tokens to generate
            temperature: Sampling temperature
        
        Returns:
            List of generated token indices
        """
        generated = []
        window = list(seed_tokens[-self.seq_len:])
        
        # Pad if necessary
        while len(window) < self.seq_len:
            window.insert(0, self.rest_token)
        
        for step in range(length):
            # Prepare input
            x = np.array(window, dtype=np.int32).reshape(1, -1)
            
            # Get predictions
            probs = model.predict(x, verbose=0)[0]
            
            # Sample next token
            next_token = self.sample_with_temperature(probs, temperature)
            
            generated.append(next_token)
            
            # Slide window
            window.append(next_token)
            window.pop(0)
            
            if (step + 1) % 50 == 0:
                print(f"  Generated {step + 1}/{length} tokens...")
        
        print(f"✅ Generated {length} tokens")
        return generated


# For testing
if __name__ == '__main__':
    import json
    
    # Test configuration
    config = {
        'MIDI_MIN': 21,
        'MIDI_MAX': 108,
        'REST_TOKEN': 88,
        'VOCAB_SIZE': 89,
        'SEQ_LEN': 32
    }
    
    # Test conversions
    mm = ModelManager('.', config)
    
    test_notes = ['C4', 'D4', 'E4', 'F#4', 'G4', 'REST', 'A4', 'B4']
    print(f"Test notes: {test_notes}")
    
    tokens = mm.notes_to_tokens(test_notes)
    print(f"Tokens: {tokens}")
    
    notes_back = mm.tokens_to_notes(tokens)
    print(f"Notes back: {notes_back}")
    
    # Verify Middle C
    c4_token = mm.note_name_to_token('C4')
    print(f"C4 (Middle C) = Token {c4_token}")
    assert c4_token == 39, "C4 should be token 39"
    print("✅ All tests passed")
