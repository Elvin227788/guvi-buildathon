# AGENTS.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

VoiceVerify AI is an API-based system for detecting AI-generated voices in audio samples. It supports 5 languages: English, Tamil, Hindi, Malayalam, and Telugu.

## Build & Run Commands

### Backend (FastAPI)

```bash
# Setup
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run server (port 8000)
python main.py
# Or: uvicorn main:app --reload --host 0.0.0.0 --port 8000

# API docs available at http://localhost:8000/docs
```

### Frontend (Static)

```bash
cd frontend
python -m http.server 3000
# Access at http://localhost:3000
```

### System Dependencies

FFmpeg is required for full audio format support:
- macOS: `brew install ffmpeg`
- Ubuntu: `sudo apt-get install ffmpeg`

## Architecture

```
Frontend (Vanilla JS) --> Backend API (FastAPI) --> Detection Pipeline
     |                         |                         |
  Base64 encode           /detect-voice          AudioProcessor
  audio file              endpoint               VoiceDetector
                                                 LanguageDetector
```

### Backend Components

| Module | Purpose |
|--------|---------|
| `main.py` | FastAPI app, endpoints, request/response models |
| `audio_processor.py` | Feature extraction using librosa (pitch, spectral, pauses) |
| `voice_detector.py` | Classification logic (rule-based + optional ML model) |
| `language_detector.py` | Multi-language detection (speech recognition fallback to heuristics) |

### Detection Flow

1. Frontend sends Base64-encoded audio to `POST /detect-voice`
2. `AudioProcessor.extract_features()` extracts: pitch_variance, spectral_flatness, natural_pauses, speech_rate, emotion_variance, background_noise, MFCCs
3. `LanguageDetector.detect()` identifies language (if `language: "auto"`)
4. `VoiceDetector.detect()` classifies as `AI_GENERATED` or `HUMAN` with confidence score
5. Response includes classification, confidence, explanation, and audio characteristics

### API Contract

```
POST /detect-voice
Request:  { audio_base64: string, language?: "auto"|"en"|"ta"|"hi"|"ml"|"te" }
Response: { classification: "AI_GENERATED"|"HUMAN", confidence: float, language: string, explanation: string, characteristics: {...} }
```

### Frontend State

Key state variables in `script.js`:
- `currentAudioBase64` - Base64 audio data ready for API
- `isRecording` - Microphone recording state
- `mediaRecorder` - Web MediaRecorder instance

## Language Codes

| Code | Language |
|------|----------|
| en | English |
| ta | Tamil |
| hi | Hindi |
| ml | Malayalam |
| te | Telugu |

## Key Patterns

- Audio files are processed via temporary files (cleaned up after processing)
- Rule-based detection is used when no trained ML model is loaded
- Frontend uses vanilla JS with Web Audio API for recording visualization
- CORS is enabled for all origins (development mode)
