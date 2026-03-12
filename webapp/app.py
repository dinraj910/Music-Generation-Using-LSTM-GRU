"""
🎵 Neural Music Generation - Flask Web Application
==================================================
A portfolio-ready web app showcasing LSTM, GRU, and BiLSTM models
for AI-powered music composition.

Author: DINRAJ K DINESH
"""

import os
import json
import uuid
import numpy as np
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename

# Import our custom modules
from utils.model_utils import ModelManager
from utils.midi_utils import MIDIGenerator

# ═══════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, '..', 'music_rnn')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, 'midi'), exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════
# Load Configuration & Models
# ═══════════════════════════════════════════════════════════════════════

# Load config
config_path = os.path.join(MODEL_DIR, 'config.json')
with open(config_path, 'r') as f:
    CONFIG = json.load(f)

# Initialize model manager (lazy loading)
model_manager = ModelManager(MODEL_DIR, CONFIG)

# Initialize MIDI generator
midi_generator = MIDIGenerator(CONFIG)

# ═══════════════════════════════════════════════════════════════════════
# Sample Sequences - Musical phrases to start generation
# ═══════════════════════════════════════════════════════════════════════

SAMPLE_SEQUENCES = {
    'c_major_scale': {
        'name': 'C Major Scale',
        'description': 'Classic ascending C major scale',
        'notes': ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5',
                  'C5', 'B4', 'A4', 'G4', 'F4', 'E4', 'D4', 'C4',
                  'C4', 'E4', 'G4', 'C5', 'G4', 'E4', 'C4', 'REST',
                  'C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5']
    },
    'twinkle_twinkle': {
        'name': 'Twinkle Twinkle',
        'description': 'Famous nursery rhyme melody',
        'notes': ['C4', 'C4', 'G4', 'G4', 'A4', 'A4', 'G4', 'REST',
                  'F4', 'F4', 'E4', 'E4', 'D4', 'D4', 'C4', 'REST',
                  'G4', 'G4', 'F4', 'F4', 'E4', 'E4', 'D4', 'REST',
                  'G4', 'G4', 'F4', 'F4', 'E4', 'E4', 'D4', 'REST']
    },
    'ode_to_joy': {
        'name': 'Ode to Joy',
        'description': 'Beethoven\'s Symphony No. 9 theme',
        'notes': ['E4', 'E4', 'F4', 'G4', 'G4', 'F4', 'E4', 'D4',
                  'C4', 'C4', 'D4', 'E4', 'E4', 'D4', 'D4', 'REST',
                  'E4', 'E4', 'F4', 'G4', 'G4', 'F4', 'E4', 'D4',
                  'C4', 'C4', 'D4', 'E4', 'D4', 'C4', 'C4', 'REST']
    },
    'fur_elise': {
        'name': 'Für Elise',
        'description': 'Beethoven\'s famous piano piece',
        'notes': ['E5', 'D#5', 'E5', 'D#5', 'E5', 'B4', 'D5', 'C5',
                  'A4', 'REST', 'C4', 'E4', 'A4', 'B4', 'REST', 'E4',
                  'G#4', 'B4', 'C5', 'REST', 'E4', 'E5', 'D#5', 'E5',
                  'D#5', 'E5', 'B4', 'D5', 'C5', 'A4', 'REST', 'C4']
    },
    'bach_prelude': {
        'name': 'Bach Prelude Pattern',
        'description': 'Arpeggiated pattern in Bach style',
        'notes': ['C4', 'E4', 'G4', 'C5', 'E5', 'G4', 'C5', 'E5',
                  'C4', 'E4', 'G4', 'C5', 'E5', 'G4', 'C5', 'E5',
                  'C4', 'D4', 'A4', 'D5', 'F5', 'A4', 'D5', 'F5',
                  'C4', 'D4', 'A4', 'D5', 'F5', 'A4', 'D5', 'F5']
    },
    'chromatic': {
        'name': 'Chromatic Ascent',
        'description': 'Half-step chromatic progression',
        'notes': ['C4', 'C#4', 'D4', 'D#4', 'E4', 'F4', 'F#4', 'G4',
                  'G#4', 'A4', 'A#4', 'B4', 'C5', 'C#5', 'D5', 'D#5',
                  'E5', 'F5', 'F#5', 'G5', 'G#5', 'A5', 'A#5', 'B5',
                  'C6', 'B5', 'A#5', 'A5', 'G#5', 'G5', 'F#5', 'F5']
    },
    'minor_mood': {
        'name': 'A Minor Mood',
        'description': 'Melancholic minor key pattern',
        'notes': ['A4', 'B4', 'C5', 'D5', 'E5', 'D5', 'C5', 'B4',
                  'A4', 'REST', 'E4', 'A4', 'C5', 'E5', 'REST', 'D5',
                  'C5', 'B4', 'A4', 'G#4', 'A4', 'REST', 'C5', 'B4',
                  'A4', 'G#4', 'A4', 'B4', 'C5', 'D5', 'E5', 'REST']
    },
    'jazz_walk': {
        'name': 'Jazz Walking Bass',
        'description': 'Jazz-style walking bass line',
        'notes': ['C3', 'E3', 'G3', 'A3', 'B3', 'A3', 'G3', 'E3',
                  'F3', 'A3', 'C4', 'D4', 'E4', 'D4', 'C4', 'A3',
                  'G3', 'B3', 'D4', 'F4', 'E4', 'D4', 'B3', 'G3',
                  'C4', 'E4', 'G4', 'A4', 'G4', 'E4', 'C4', 'REST']
    }
}

# ═══════════════════════════════════════════════════════════════════════
# Routes
# ═══════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    """Main page with piano keyboard and controls."""
    return render_template('index.html', 
                         samples=SAMPLE_SEQUENCES,
                         config=CONFIG)


@app.route('/api/models', methods=['GET'])
def get_models():
    """Get available models and their info."""
    models_info = model_manager.get_models_info()
    return jsonify({
        'success': True,
        'models': models_info
    })


@app.route('/api/samples', methods=['GET'])
def get_samples():
    """Get available sample sequences."""
    return jsonify({
        'success': True,
        'samples': SAMPLE_SEQUENCES
    })


@app.route('/api/generate', methods=['POST'])
def generate_music():
    """
    Generate music from input sequence.
    
    Expected JSON:
    {
        "notes": ["C4", "E4", "G4", ...],  // At least 32 notes
        "model": "lstm" | "gru" | "bilstm",
        "temperature": 0.5-1.5,
        "length": 50-500
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        notes = data.get('notes', [])
        model_name = data.get('model', 'lstm')
        temperature = float(data.get('temperature', 0.8))
        gen_length = int(data.get('length', 100))
        
        # Validation checks
        if len(notes) < CONFIG['SEQ_LEN']:
            return jsonify({
                'success': False,
                'error': f'Need at least {CONFIG["SEQ_LEN"]} notes as seed. Got {len(notes)}.'
            }), 400
        
        if model_name not in ['lstm', 'gru', 'bilstm']:
            return jsonify({
                'success': False,
                'error': f'Invalid model: {model_name}. Use lstm, gru, or bilstm.'
            }), 400
        
        # Note: BiLSTM warning
        bilstm_warning = None
        if model_name == 'bilstm':
            bilstm_warning = ('⚠️ BiLSTM cannot truly generate music autoregressively. '
                            'It uses future context during training which doesn\'t exist during generation. '
                            'Results may be less coherent.')
        
        temperature = max(0.1, min(2.0, temperature))
        gen_length = max(50, min(500, gen_length))
        
        # Convert note names to tokens
        seed_tokens = model_manager.notes_to_tokens(notes[-CONFIG['SEQ_LEN']:])
        
        # Load model and generate
        model = model_manager.get_model(model_name)
        generated_tokens = model_manager.generate_sequence(
            model, seed_tokens, gen_length, temperature
        )
        
        # Convert tokens back to note names
        generated_notes = model_manager.tokens_to_notes(generated_tokens)
        
        # Create unique filename
        file_id = str(uuid.uuid4())[:8]
        midi_filename = f'{model_name}_{file_id}.mid'
        midi_path = os.path.join(OUTPUT_DIR, 'midi', midi_filename)
        
        # Generate MIDI file
        full_sequence = seed_tokens + generated_tokens
        duration = midi_generator.tokens_to_midi(full_sequence, midi_path)
        
        # Statistics
        rest_count = generated_tokens.count(CONFIG['REST_TOKEN'])
        rest_pct = 100 * rest_count / len(generated_tokens)
        unique_pitches = len(set(t for t in generated_tokens if t != CONFIG['REST_TOKEN']))
        
        response = {
            'success': True,
            'generated_notes': generated_notes,
            'seed_notes': model_manager.tokens_to_notes(seed_tokens),
            'midi_file': midi_filename,
            'stats': {
                'total_notes': len(generated_tokens),
                'rest_percentage': round(rest_pct, 1),
                'unique_pitches': unique_pitches,
                'duration_seconds': round(duration, 1),
                'model_used': model_name,
                'temperature': temperature
            }
        }
        
        if bilstm_warning:
            response['warning'] = bilstm_warning
        
        return jsonify(response)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/download/<filename>')
def download_midi(filename):
    """Download generated MIDI file."""
    filename = secure_filename(filename)
    file_path = os.path.join(OUTPUT_DIR, 'midi', filename)
    
    if not os.path.exists(file_path):
        return jsonify({'success': False, 'error': 'File not found'}), 404
    
    return send_file(
        file_path,
        mimetype='audio/midi',
        as_attachment=True,
        download_name=filename
    )


@app.route('/api/note-to-midi', methods=['POST'])
def note_to_midi_number():
    """Convert note name to MIDI number for piano display."""
    data = request.get_json()
    note_name = data.get('note', '')
    midi_num = model_manager.note_name_to_midi(note_name)
    return jsonify({'midi': midi_num})


@app.route('/about')
def about():
    """About page with project information."""
    return render_template('about.html', config=CONFIG)


# ═══════════════════════════════════════════════════════════════════════
# Error Handlers
# ═══════════════════════════════════════════════════════════════════════

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


# ═══════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎵 Neural Music Generation Web App")
    print("="*60)
    print(f"Model Directory: {MODEL_DIR}")
    print(f"Output Directory: {OUTPUT_DIR}")
    print(f"Available Models: LSTM, GRU, BiLSTM")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
