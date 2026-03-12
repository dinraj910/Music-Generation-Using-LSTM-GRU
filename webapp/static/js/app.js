/**
 * ═══════════════════════════════════════════════════════════════════════
 * NEURAL MUSIC GENERATION - Main Application
 * Handles UI, API calls, and music generation workflow
 * ═══════════════════════════════════════════════════════════════════════
 */

// ─── Global State ──────────────────────────────────────────────────────
const AppState = {
    selectedModel: 'lstm',
    temperature: 0.8,
    genLength: 100,
    inputSequence: [],
    generatedNotes: [],
    midiFilename: null,
    isGenerating: false,
    MIN_NOTES: 32
};

// ─── Sample Data ───────────────────────────────────────────────────────
let SAMPLES = {};
try {
    SAMPLES = JSON.parse(document.getElementById('sampleData').textContent);
} catch (e) {
    console.error('Failed to parse sample data:', e);
}

// ─── Piano Instance ────────────────────────────────────────────────────
let piano = null;

// ─── DOM Elements ──────────────────────────────────────────────────────
const elements = {
    pianoContainer: document.getElementById('pianoKeyboard'),
    sequenceDisplay: document.getElementById('sequenceDisplay'),
    noteCount: document.getElementById('noteCount'),
    generateBtn: document.getElementById('generateBtn'),
    generateSpinner: document.getElementById('generateSpinner'),
    outputCard: document.getElementById('outputCard'),
    generatedDisplay: document.getElementById('generatedDisplay'),
    bilstmWarning: document.getElementById('bilstmWarning'),
    playSequence: document.getElementById('playSequence'),
    playGenerated: document.getElementById('playGenerated'),
    downloadMidi: document.getElementById('downloadMidi'),
    tempValue: document.getElementById('tempValue'),
    lengthValue: document.getElementById('lengthValue'),
    temperatureSlider: document.getElementById('temperature'),
    genLengthSlider: document.getElementById('genLength'),
    clearPiano: document.getElementById('clearPiano'),
    undoNote: document.getElementById('undoNote'),
    addRest: document.getElementById('addRest'),
    toast: document.getElementById('liveToast'),
    toastMessage: document.getElementById('toastMessage'),
    // Stats
    statNotes: document.getElementById('statNotes'),
    statUnique: document.getElementById('statUnique'),
    statRest: document.getElementById('statRest'),
    statDuration: document.getElementById('statDuration')
};

// ─── Initialize Application ────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    initPiano();
    initModelSelection();
    initSliders();
    initSampleButtons();
    initControlButtons();
    initGenerateButton();
    initPlaybackButtons();
    
    console.log('✅ Neural Music Generation App initialized');
});

// ─── Piano Initialization ──────────────────────────────────────────────
function initPiano() {
    piano = new VirtualPiano('pianoKeyboard', {
        startOctave: 3,
        octaves: 3,
        showLabels: true,
        onNotePlay: (note) => {
            addNoteToSequence(note);
        }
    });
}

// ─── Model Selection ───────────────────────────────────────────────────
function initModelSelection() {
    const modelOptions = document.querySelectorAll('.model-option');
    
    modelOptions.forEach(option => {
        option.addEventListener('click', () => {
            // Update UI
            modelOptions.forEach(opt => opt.classList.remove('selected'));
            option.classList.add('selected');
            
            // Update radio
            const radio = option.querySelector('input[type="radio"]');
            radio.checked = true;
            
            // Update state
            AppState.selectedModel = radio.value;
            
            // Show/hide BiLSTM warning info
            if (radio.value === 'bilstm') {
                showToast('Note: BiLSTM has limited generation capability', 'warning');
            }
        });
    });
}

// ─── Sliders ───────────────────────────────────────────────────────────
function initSliders() {
    // Temperature slider
    elements.temperatureSlider.addEventListener('input', (e) => {
        AppState.temperature = parseFloat(e.target.value);
        elements.tempValue.textContent = AppState.temperature.toFixed(1);
    });
    
    // Generation length slider
    elements.genLengthSlider.addEventListener('input', (e) => {
        AppState.genLength = parseInt(e.target.value);
        elements.lengthValue.textContent = AppState.genLength;
    });
}

// ─── Sample Buttons ────────────────────────────────────────────────────
function initSampleButtons() {
    const sampleBtns = document.querySelectorAll('.sample-btn');
    
    sampleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const sampleKey = btn.dataset.sample;
            const sample = SAMPLES[sampleKey];
            
            if (sample && sample.notes) {
                loadSequence(sample.notes);
                showToast(`Loaded: ${sample.name}`, 'success');
            }
        });
    });
}

// ─── Control Buttons ───────────────────────────────────────────────────
function initControlButtons() {
    // Clear all
    elements.clearPiano.addEventListener('click', () => {
        clearSequence();
        showToast('Sequence cleared', 'info');
    });
    
    // Undo last note
    elements.undoNote.addEventListener('click', () => {
        if (AppState.inputSequence.length > 0) {
            AppState.inputSequence.pop();
            updateSequenceDisplay();
        }
    });
    
    // Add REST
    elements.addRest.addEventListener('click', () => {
        addNoteToSequence('REST');
    });
}

// ─── Generate Button ───────────────────────────────────────────────────
function initGenerateButton() {
    elements.generateBtn.addEventListener('click', generateMusic);
}

// ─── Playback Buttons ──────────────────────────────────────────────────
function initPlaybackButtons() {
    // Play input sequence
    elements.playSequence.addEventListener('click', async () => {
        if (AppState.inputSequence.length === 0) return;
        
        const notes = AppState.inputSequence.filter(n => n !== 'REST');
        await piano.playSequence(notes, 120);
    });
    
    // Play generated music
    elements.playGenerated.addEventListener('click', async () => {
        if (AppState.generatedNotes.length === 0) return;
        
        // Combine seed + generated, filter REST
        const allNotes = [...AppState.inputSequence.slice(-32), ...AppState.generatedNotes]
            .filter(n => n !== 'REST');
        
        await piano.playSequence(allNotes, 180);
    });
    
    // Download MIDI
    elements.downloadMidi.addEventListener('click', () => {
        if (AppState.midiFilename) {
            window.location.href = `/api/download/${AppState.midiFilename}`;
        }
    });
}

// ─── Sequence Management ───────────────────────────────────────────────
function addNoteToSequence(note) {
    AppState.inputSequence.push(note);
    updateSequenceDisplay();
}

function loadSequence(notes) {
    AppState.inputSequence = [...notes];
    updateSequenceDisplay();
}

function clearSequence() {
    AppState.inputSequence = [];
    updateSequenceDisplay();
    hideOutput();
}

function updateSequenceDisplay() {
    const display = elements.sequenceDisplay;
    const count = AppState.inputSequence.length;
    
    // Update counter
    elements.noteCount.textContent = `${count}/${AppState.MIN_NOTES}`;
    elements.noteCount.className = count >= AppState.MIN_NOTES 
        ? 'badge bg-success ms-2' 
        : 'badge bg-primary ms-2';
    
    // Enable/disable buttons
    elements.generateBtn.disabled = count < AppState.MIN_NOTES;
    elements.playSequence.disabled = count === 0;
    
    // Display notes
    if (count === 0) {
        display.innerHTML = `
            <span class="placeholder-text">
                <i class="bi bi-arrow-left me-2"></i>
                Click piano keys or select a sample to start
            </span>
        `;
        return;
    }
    
    display.innerHTML = AppState.inputSequence
        .map(note => {
            const isRest = note === 'REST';
            return `<span class="note-tag ${isRest ? 'rest' : ''}">${note}</span>`;
        })
        .join('');
    
    // Scroll to end
    display.scrollTop = display.scrollHeight;
}

// ─── Music Generation ──────────────────────────────────────────────────
async function generateMusic() {
    if (AppState.isGenerating) return;
    if (AppState.inputSequence.length < AppState.MIN_NOTES) {
        showToast(`Need at least ${AppState.MIN_NOTES} notes to generate`, 'warning');
        return;
    }
    
    AppState.isGenerating = true;
    elements.generateBtn.disabled = true;
    elements.generateSpinner.classList.remove('d-none');
    
    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                notes: AppState.inputSequence,
                model: AppState.selectedModel,
                temperature: AppState.temperature,
                length: AppState.genLength
            })
        });
        
        const data = await response.json();
        
        if (!response.ok || !data.success) {
            throw new Error(data.error || 'Generation failed');
        }
        
        // Store results
        AppState.generatedNotes = data.generated_notes;
        AppState.midiFilename = data.midi_file;
        
        // Show output
        displayGeneratedMusic(data);
        showToast('Music generated successfully!', 'success');
        
    } catch (error) {
        console.error('Generation error:', error);
        showToast(`Error: ${error.message}`, 'danger');
    } finally {
        AppState.isGenerating = false;
        elements.generateBtn.disabled = AppState.inputSequence.length < AppState.MIN_NOTES;
        elements.generateSpinner.classList.add('d-none');
    }
}

// ─── Display Generated Music ───────────────────────────────────────────
function displayGeneratedMusic(data) {
    // Show output card
    elements.outputCard.classList.remove('d-none');
    
    // Update stats
    elements.statNotes.textContent = data.stats.total_notes;
    elements.statUnique.textContent = data.stats.unique_pitches;
    elements.statRest.textContent = `${data.stats.rest_percentage}%`;
    elements.statDuration.textContent = `${data.stats.duration_seconds}s`;
    
    // Display seed notes
    const seedHtml = data.seed_notes
        .map(note => `<span class="note-tag seed">${note}</span>`)
        .join('');
    
    // Display generated notes
    const genHtml = data.generated_notes
        .map(note => {
            const isRest = note === 'REST';
            return `<span class="note-tag generated ${isRest ? 'rest' : ''}">${note}</span>`;
        })
        .join('');
    
    elements.generatedDisplay.innerHTML = `
        <div class="mb-2">
            <small class="text-muted">Seed:</small>
            ${seedHtml}
        </div>
        <div>
            <small class="text-muted">Generated:</small>
            ${genHtml}
        </div>
    `;
    
    // Show BiLSTM warning if applicable
    if (data.warning) {
        elements.bilstmWarning.classList.remove('d-none');
        elements.bilstmWarning.querySelector('.alert') || 
            (elements.bilstmWarning.textContent = data.warning);
    } else {
        elements.bilstmWarning.classList.add('d-none');
    }
    
    // Scroll to output
    elements.outputCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function hideOutput() {
    elements.outputCard.classList.add('d-none');
    AppState.generatedNotes = [];
    AppState.midiFilename = null;
}

// ─── Toast Notifications ───────────────────────────────────────────────
function showToast(message, type = 'info') {
    elements.toastMessage.textContent = message;
    
    // Update toast styling based on type
    const toast = elements.toast;
    toast.className = 'toast';
    
    const icon = toast.querySelector('i');
    icon.className = 'bi me-2';
    
    switch (type) {
        case 'success':
            icon.classList.add('bi-check-circle-fill', 'text-success');
            break;
        case 'warning':
            icon.classList.add('bi-exclamation-triangle-fill', 'text-warning');
            break;
        case 'danger':
            icon.classList.add('bi-x-circle-fill', 'text-danger');
            break;
        default:
            icon.classList.add('bi-info-circle-fill', 'text-primary');
    }
    
    const bsToast = new bootstrap.Toast(toast, { delay: 3000 });
    bsToast.show();
}

// ─── Utility Functions ─────────────────────────────────────────────────
function formatDuration(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
}

// Export for debugging
window.AppState = AppState;
window.piano = piano;
