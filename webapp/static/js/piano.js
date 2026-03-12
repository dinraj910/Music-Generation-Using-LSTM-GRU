/**
 * ═══════════════════════════════════════════════════════════════════════
 * VIRTUAL PIANO KEYBOARD
 * Interactive piano with playback using Tone.js
 * ═══════════════════════════════════════════════════════════════════════
 */

class VirtualPiano {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            startOctave: options.startOctave || 3,
            octaves: options.octaves || 3,
            showLabels: options.showLabels !== false,
            onNotePlay: options.onNotePlay || null,
            ...options
        };
        
        this.synth = null;
        this.audioInitialized = false;
        this.activeKeys = new Set();
        
        // Note names
        this.noteNames = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
        this.whiteNotes = ['C', 'D', 'E', 'F', 'G', 'A', 'B'];
        this.blackNotes = ['C#', 'D#', 'F#', 'G#', 'A#'];
        
        // Keyboard mapping (computer keyboard to piano notes)
        this.keyMap = {
            // White keys - bottom row
            'a': 'C', 's': 'D', 'd': 'E', 'f': 'F', 
            'g': 'G', 'h': 'A', 'j': 'B',
            // White keys - continued
            'k': 'C+', 'l': 'D+', ';': 'E+',
            // Black keys - top row
            'w': 'C#', 'e': 'D#', 't': 'F#', 'y': 'G#', 'u': 'A#',
            // Black keys - continued
            'o': 'C#+', 'p': 'D#+'
        };
        
        this.init();
    }
    
    async init() {
        this.render();
        this.attachEventListeners();
    }
    
    async initAudio() {
        if (this.audioInitialized) return;
        
        try {
            await Tone.start();
            
            // Create a polyphonic synth with piano-like sound
            this.synth = new Tone.PolySynth(Tone.Synth, {
                oscillator: {
                    type: 'triangle'
                },
                envelope: {
                    attack: 0.02,
                    decay: 0.3,
                    sustain: 0.2,
                    release: 1.0
                }
            }).toDestination();
            
            // Add reverb for richer sound
            const reverb = new Tone.Reverb({
                decay: 2,
                wet: 0.3
            }).toDestination();
            
            this.synth.connect(reverb);
            
            this.audioInitialized = true;
            console.log('✅ Audio initialized');
        } catch (error) {
            console.error('Failed to initialize audio:', error);
        }
    }
    
    render() {
        this.container.innerHTML = '';
        
        const startOctave = this.options.startOctave;
        const endOctave = startOctave + this.options.octaves;
        
        let whiteKeyIndex = 0;
        
        for (let octave = startOctave; octave < endOctave; octave++) {
            for (let i = 0; i < 12; i++) {
                const noteName = this.noteNames[i];
                const fullNote = `${noteName}${octave}`;
                const isBlack = noteName.includes('#');
                
                const key = document.createElement('div');
                key.className = `piano-key ${isBlack ? 'black' : 'white'}`;
                key.dataset.note = fullNote;
                key.dataset.midi = this.noteToMidi(fullNote);
                
                if (this.options.showLabels && !isBlack) {
                    const label = document.createElement('span');
                    label.className = 'key-label';
                    label.textContent = fullNote;
                    key.appendChild(label);
                }
                
                if (isBlack) {
                    // Position black keys
                    const whiteKeyWidth = 42; // 40px + 2px margin
                    const blackKeyWidth = 28;
                    const offset = (whiteKeyIndex * whiteKeyWidth) - (blackKeyWidth / 2);
                    key.style.left = `${offset + 16}px`; // +16 for container padding
                }
                
                this.container.appendChild(key);
                
                if (!isBlack) {
                    whiteKeyIndex++;
                }
            }
        }
    }
    
    attachEventListeners() {
        // Mouse/touch events on piano keys
        this.container.addEventListener('mousedown', (e) => this.handleKeyDown(e));
        this.container.addEventListener('mouseup', (e) => this.handleKeyUp(e));
        this.container.addEventListener('mouseleave', (e) => this.handleKeyUp(e));
        
        // Touch support
        this.container.addEventListener('touchstart', (e) => {
            e.preventDefault();
            this.handleKeyDown(e);
        });
        this.container.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.handleKeyUp(e);
        });
        
        // Keyboard events
        document.addEventListener('keydown', (e) => this.handleComputerKeyDown(e));
        document.addEventListener('keyup', (e) => this.handleComputerKeyUp(e));
    }
    
    async handleKeyDown(e) {
        const key = e.target.closest('.piano-key');
        if (!key) return;
        
        await this.initAudio();
        
        const note = key.dataset.note;
        this.playNote(note);
        key.classList.add('active');
    }
    
    handleKeyUp(e) {
        const key = e.target.closest('.piano-key');
        if (!key) return;
        
        const note = key.dataset.note;
        this.releaseNote(note);
        key.classList.remove('active');
    }
    
    async handleComputerKeyDown(e) {
        // Don't handle if typing in input
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
        if (e.repeat) return;
        
        const keyLower = e.key.toLowerCase();
        const noteBase = this.keyMap[keyLower];
        
        if (!noteBase) return;
        
        await this.initAudio();
        
        // Determine octave
        let octave = this.options.startOctave + 1;
        let noteName = noteBase;
        
        if (noteBase.endsWith('+')) {
            octave += 1;
            noteName = noteBase.slice(0, -1);
        }
        
        const fullNote = `${noteName}${octave}`;
        
        if (this.activeKeys.has(fullNote)) return;
        
        this.activeKeys.add(fullNote);
        this.playNote(fullNote);
        
        // Highlight key
        const keyEl = this.container.querySelector(`[data-note="${fullNote}"]`);
        if (keyEl) keyEl.classList.add('active');
    }
    
    handleComputerKeyUp(e) {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
        
        const keyLower = e.key.toLowerCase();
        const noteBase = this.keyMap[keyLower];
        
        if (!noteBase) return;
        
        let octave = this.options.startOctave + 1;
        let noteName = noteBase;
        
        if (noteBase.endsWith('+')) {
            octave += 1;
            noteName = noteBase.slice(0, -1);
        }
        
        const fullNote = `${noteName}${octave}`;
        
        this.activeKeys.delete(fullNote);
        this.releaseNote(fullNote);
        
        const keyEl = this.container.querySelector(`[data-note="${fullNote}"]`);
        if (keyEl) keyEl.classList.remove('active');
    }
    
    playNote(note) {
        if (this.synth) {
            this.synth.triggerAttack(note);
        }
        
        // Callback for external handling
        if (this.options.onNotePlay) {
            this.options.onNotePlay(note);
        }
        
        // Visual feedback
        const keyEl = this.container.querySelector(`[data-note="${note}"]`);
        if (keyEl) {
            keyEl.classList.add('played');
            setTimeout(() => keyEl.classList.remove('played'), 200);
        }
    }
    
    releaseNote(note) {
        if (this.synth) {
            this.synth.triggerRelease(note);
        }
    }
    
    noteToMidi(note) {
        const match = note.match(/^([A-G]#?)(\d+)$/);
        if (!match) return null;
        
        const [, noteName, octave] = match;
        const noteIndex = this.noteNames.indexOf(noteName);
        return (parseInt(octave) + 1) * 12 + noteIndex;
    }
    
    midiToNote(midi) {
        const octave = Math.floor(midi / 12) - 1;
        const noteIndex = midi % 12;
        return `${this.noteNames[noteIndex]}${octave}`;
    }
    
    // Play a sequence of notes
    async playSequence(notes, tempo = 200) {
        await this.initAudio();
        
        const now = Tone.now();
        const noteDuration = 60 / tempo; // Convert BPM to seconds per beat
        
        notes.forEach((note, index) => {
            if (note === 'REST') return;
            
            const time = now + (index * noteDuration * 0.5);
            
            // Schedule note
            Tone.Transport.schedule((t) => {
                this.synth.triggerAttackRelease(note, noteDuration * 0.4, t);
                
                // Visual feedback
                const keyEl = this.container.querySelector(`[data-note="${note}"]`);
                if (keyEl) {
                    keyEl.classList.add('played');
                    setTimeout(() => keyEl.classList.remove('played'), noteDuration * 400);
                }
            }, time);
        });
        
        Tone.Transport.start();
        
        // Stop transport after sequence
        setTimeout(() => {
            Tone.Transport.stop();
            Tone.Transport.cancel();
        }, notes.length * noteDuration * 500 + 1000);
    }
    
    // Highlight a specific note (for visualization)
    highlightNote(note, duration = 300) {
        const keyEl = this.container.querySelector(`[data-note="${note}"]`);
        if (keyEl) {
            keyEl.classList.add('played');
            setTimeout(() => keyEl.classList.remove('played'), duration);
        }
    }
    
    // Clear all highlights
    clearHighlights() {
        this.container.querySelectorAll('.played, .active').forEach(el => {
            el.classList.remove('played', 'active');
        });
    }
}

// Export for use in other modules
window.VirtualPiano = VirtualPiano;
