# VoiceVerify AI 🎙️

**AI-Generated Voice Detection System (Multi-Language)**

Built by **Team 404 Found** for GUVI Buildathon 2026

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Overview

VoiceVerify AI is an API-based system that determines whether a given voice sample is **AI-generated** or **human-generated**. The system supports voice samples in five languages:

- 🇬🇧 **English**
- 🇮🇳 **Tamil**
- 🇮🇳 **Hindi**
- 🇮🇳 **Malayalam**
- 🇮🇳 **Telugu**

## ✨ Features

- **Multi-language Detection**: Automatically detects language and analyzes voice patterns
- **Base64 Audio Input**: Accepts audio as Base64-encoded MP3
- **Confidence Scoring**: Returns probability score for classification
- **Detailed Explanations**: Provides analysis of why a voice is classified as AI/Human
- **Audio Characteristics**: Returns pitch variance, spectral flatness, pause patterns, etc.

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│    Frontend     │────▶│   Backend API   │────▶│  Voice Detector │
│   (HTML/JS)     │     │   (FastAPI)     │     │    (ML/Rules)   │
│                 │◀────│                 │◀────│                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                      │                       │
         │                      │                       │
    Drag & Drop            Process Audio          Analyze Features
    Record Audio           Extract Features       Classify Voice
    Display Results        Detect Language        Generate Explanation
```

## 📁 Project Structure

```
guvi-buildathon/
├── frontend/                 # Web UI
│   ├── index.html           # Main page
│   ├── style.css            # Styling
│   ├── script.js            # JavaScript logic
│   └── README.md            # Frontend docs
│
├── backend/                  # API Server
│   ├── main.py              # FastAPI app
│   ├── audio_processor.py   # Feature extraction
│   ├── voice_detector.py    # Classification logic
│   ├── language_detector.py # Language detection
│   ├── requirements.txt     # Dependencies
│   └── README.md            # Backend docs
│
└── README.md                # This file
```

## 🚀 Quick Start

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

API will be available at `http://localhost:8000`

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Serve with Python
python -m http.server 3000

# Or use any static file server
npx http-server -p 3000
```

Open `http://localhost:3000` in your browser.

## 📡 API Usage

### Endpoint

```
POST /detect-voice
```

### Request

```json
{
  "audio_base64": "SGVsbG8gV29ybGQh...",
  "language": "auto"
}
```

### Response

```json
{
  "classification": "AI_GENERATED",
  "confidence": 0.87,
  "language": "English",
  "explanation": "The audio exhibits uniform pitch patterns...",
  "characteristics": {
    "pitch_variance": 0.12,
    "spectral_flatness": 0.65,
    "natural_pauses": false,
    "speech_rate": 0.45,
    "emotion_variance": 0.18,
    "background_noise": 0.03
  }
}
```

## 🔬 Detection Methodology

The system analyzes multiple audio characteristics:

| Feature | Human Voice | AI Voice |
|---------|-------------|----------|
| Pitch Variance | High (natural variation) | Low (uniform) |
| Spectral Flatness | Low (tonal) | High (synthetic) |
| Natural Pauses | Present (irregular) | Absent/Regular |
| Speech Rate | Variable | Consistent |
| Emotion Variance | Dynamic | Limited |
| Background Noise | Present | Clean/Absent |

## 🛠️ Tech Stack

**Backend:**
- Python 3.9+
- FastAPI
- librosa (audio analysis)
- NumPy/SciPy
- scikit-learn (optional ML models)

**Frontend:**
- HTML5 / CSS3
- Vanilla JavaScript
- Web Audio API
- MediaRecorder API

## 📊 Supported Formats

- MP3
- WAV
- OGG
- M4A
- FLAC

Maximum file size: **10MB**

## 🤝 Team

**Team 404 Found**
- GUVI Buildathon 2026

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

<p align="center">
  Made with ❤️ for GUVI Buildathon 2026
</p>
