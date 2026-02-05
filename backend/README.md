# VoiceVerify AI - Backend API

AI-Generated Voice Detection API supporting Tamil, English, Hindi, Malayalam, and Telugu.

**Team 404 Found** - GUVI Buildathon 2026

## Features

- **Multi-language Support**: Detects AI voices in 5 Indian languages
- **Audio Feature Extraction**: Uses librosa for comprehensive audio analysis
- **Rule-based + ML Detection**: Works out-of-the-box with rule-based detection, supports custom ML models
- **REST API**: FastAPI-based with automatic OpenAPI documentation

## Project Structure

```
backend/
├── main.py              # FastAPI application
├── audio_processor.py   # Audio feature extraction
├── voice_detector.py    # AI voice classification
├── language_detector.py # Multi-language detection
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Quick Start

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg (Optional, for better audio support)

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html

### 4. Run the Server

```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
```
GET /health
```

### Detect Voice
```
POST /detect-voice
Content-Type: application/json

{
  "audio_base64": "base64_encoded_audio_data",
  "language": "auto"  // or: en, ta, hi, ml, te
}
```

**Response:**
```json
{
  "classification": "AI_GENERATED",
  "confidence": 0.87,
  "language": "English",
  "explanation": "The English audio sample appears to be AI-generated...",
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

### API Documentation
```
GET /docs      # Swagger UI
GET /redoc     # ReDoc
```

## Audio Features Analyzed

| Feature | Description | AI Indicator |
|---------|-------------|--------------|
| Pitch Variance | Variation in fundamental frequency | Low = AI |
| Spectral Flatness | Tonal vs. noise-like quality | High = AI |
| Natural Pauses | Presence of speech pauses | Absent = AI |
| Speech Rate | Syllables per second | Uniform = AI |
| Emotion Variance | Dynamic expression | Low = AI |
| Background Noise | Ambient sound level | Absent = AI |

## Training Custom Models

```python
from voice_detector import VoiceDetectorTrainer
from audio_processor import AudioProcessor
import numpy as np

# Prepare training data
processor = AudioProcessor()
X = []  # Feature vectors
y = []  # Labels (0=human, 1=AI)

for audio_path, label in training_data:
    features = processor.extract_features(audio_path)
    X.append(extract_feature_vector(features))
    y.append(label)

# Train model
trainer = VoiceDetectorTrainer()
model = trainer.train(np.array(X), np.array(y), model_type="random_forest")
trainer.save("models/voice_detector.pkl")
```

## Supported Audio Formats

- MP3
- WAV
- OGG
- M4A
- FLAC

Maximum file size: 10MB

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8000 | Server port |
| `HOST` | 0.0.0.0 | Server host |
| `MODEL_PATH` | None | Path to trained model |

## Testing

```bash
# Test with curl
curl -X POST http://localhost:8000/detect-voice \
  -H "Content-Type: application/json" \
  -d '{"audio_base64": "YOUR_BASE64_AUDIO", "language": "auto"}'
```

## License

MIT License
