# 🎵 Neural Music Generation

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.13+-orange?logo=tensorflow&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.3+-green?logo=flask&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?logo=bootstrap&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

**AI-Powered Music Composition using LSTM, GRU, and BiLSTM Neural Networks**

[Live Demo](#) • [Documentation](#-how-it-works) • [Getting Started](#-getting-started)

</div>

---

## 📸 Screenshots

<div align="center">
<img src="docs/screenshot-main.png" alt="Main Interface" width="800">
<p><em>Interactive piano keyboard with real-time music generation</em></p>
</div>

---

## ✨ Features

- 🎹 **Interactive Virtual Piano** - Play notes directly in the browser with keyboard support
- 🤖 **Three Neural Network Models** - LSTM, GRU, and BiLSTM architectures
- 🎼 **Pre-built Sample Sequences** - Start with famous melodies or create your own
- 🎛️ **Adjustable Parameters** - Control temperature and generation length
- 🎵 **MIDI Export** - Download generated music as MIDI files
- 🔊 **In-Browser Playback** - Listen to your creations using Tone.js
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile

---

## 🧠 Model Architectures

| Model | Type | Parameters | Can Generate | Use Case |
|-------|------|------------|:------------:|----------|
| **Stacked LSTM** | Unidirectional | ~1.1M | ✅ Yes | Best for melodic sequences |
| **Stacked GRU** | Unidirectional | ~850K | ✅ Yes | Faster, comparable quality |
| **BiLSTM** | Bidirectional | ~2.1M | ⚠️ Limited | Classifier demonstration |

### Architecture Details

```
Input(32) → Embedding(89, 64) 
    → LSTM/GRU(256, return_sequences=True)
    → Dropout(0.3)
    → LSTM/GRU(256)
    → Dropout(0.3)
    → Dense(89, softmax)
```

> ⚠️ **Note on BiLSTM**: Bidirectional models cannot truly generate music autoregressively because they require future context during inference, which doesn't exist during generation.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/neural-music-generation.git
   cd neural-music-generation
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r webapp/requirements.txt
   ```

4. **Run the application**
   ```bash
   cd webapp
   python app.py
   ```

5. **Open in browser**
   ```
   http://localhost:5000
   ```

---

## 🔧 How It Works

### 1. Data Preprocessing
MIDI files are parsed using `music21`. Each note is converted to a **pitch token**:
- Tokens `0-87` → MIDI pitches 21-108 (full piano range A0 to C8)
- Token `88` → REST (silence)

### 2. Sequence Construction
Using a **sliding window** approach with `SEQ_LEN=32`:
```
Input:  [note₁, note₂, ..., note₃₂]
Target: note₃₃
```

### 3. Autoregressive Generation
```
1. Start with 32-note seed sequence
2. Model predicts next note probabilities
3. Sample using temperature scaling
4. Append prediction, slide window
5. Repeat for N notes
```

### Temperature Parameter
| Temperature | Effect | Result |
|-------------|--------|--------|
| `0.5` | Conservative | More repetitive, stays in key |
| `0.8` | Balanced | Recommended setting |
| `1.0` | Standard | More variety |
| `1.2+` | Creative | Surprising, less tonal |

---

## 📁 Project Structure

```
neural-music-generation/
├── music_rnn/                 # Trained models
│   ├── lstm/
│   │   ├── lstm.keras
│   │   └── ...
│   ├── gru/
│   ├── bilstm/
│   ├── config.json
│   └── *_best.keras
│
├── webapp/                    # Flask web application
│   ├── app.py                 # Main Flask app
│   ├── requirements.txt
│   ├── utils/
│   │   ├── model_utils.py     # Model loading & generation
│   │   └── midi_utils.py      # MIDI file creation
│   ├── templates/
│   │   ├── index.html
│   │   ├── about.html
│   │   └── *.html
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/
│   │       ├── piano.js       # Virtual piano
│   │       └── app.js         # Main app logic
│   └── output/                # Generated MIDI files
│
├── notebook/                  # Training notebook
│   └── DINRAJ_MusicGeneration_RNN_Trained.ipynb
│
└── README.md
```

---

## 🎹 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main application page |
| `/about` | GET | About page with documentation |
| `/api/models` | GET | Get available models info |
| `/api/samples` | GET | Get pre-built sample sequences |
| `/api/generate` | POST | Generate music from input |
| `/api/download/<filename>` | GET | Download MIDI file |

### Generate Music API

```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "notes": ["C4", "E4", "G4", ...],  // 32+ notes
    "model": "lstm",                    // lstm | gru | bilstm
    "temperature": 0.8,                 // 0.1 - 2.0
    "length": 100                       // 50 - 500
  }'
```

---

## 🛠️ Tech Stack

- **Backend**: Flask, TensorFlow/Keras
- **Frontend**: Bootstrap 5, Vanilla JS
- **Audio**: Tone.js (Web Audio API)
- **MIDI**: pretty_midi, midiutil
- **Training**: Google Colab (T4 GPU)

---

## 📊 Training Data

Models were trained on the **music21 corpus**:
- 370+ Bach chorales
- 20 Mozart pieces
- 20 Schubert pieces

Total: ~150,000+ note tokens

---

## 🚧 Future Improvements

- [ ] Add duration tokens for expressive timing
- [ ] Implement Transformer architecture
- [ ] Add multi-instrument support
- [ ] Real-time collaboration mode
- [ ] Export to music notation (MusicXML)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**DINRAJ K DINESH**

- Portfolio: [dinrajkdinesh.vercel.app](https://dinrajkdinesh.vercel.app)
- GitHub: [@dinrajkdinesh](https://github.com/dinrajkdinesh)
- LinkedIn: [DINRAJ K DINESH](https://linkedin.com/in/dinrajkdinesh)

---

## 🙏 Acknowledgments

- [music21](http://web.mit.edu/music21/) for MIDI parsing
- [Tone.js](https://tonejs.github.io/) for web audio
- [Bootstrap](https://getbootstrap.com/) for UI components
- TensorFlow/Keras team for the amazing deep learning framework

---

<div align="center">

**⭐ Star this repo if you found it helpful!**

Made with ❤️ and 🎵

</div>
