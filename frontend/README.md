# VoiceVerify AI - AI-Generated Voice Detection

A multi-language AI-generated voice detection system built for GUVI Buildathon 2026 by **Team 404 Found**.

## Features

- **Multi-Language Support**: Detects AI-generated voices in 5 languages:
  - English
  - Tamil
  - Hindi  
  - Malayalam
  - Telugu

- **Multiple Input Methods**:
  - Drag & drop audio file upload
  - Click to browse files
  - Live microphone recording with real-time visualization

- **Supported Formats**: MP3, WAV, OGG, M4A (up to 10MB)

- **Detailed Results**:
  - AI/Human classification
  - Confidence score with visual meter
  - Detected language
  - Detailed explanation
  - Audio characteristics analysis

## Project Structure

```
frontend/
├── index.html      # Main HTML page
├── style.css       # Modern dark theme styling
├── script.js       # JavaScript functionality
└── README.md       # This file
```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Elvin227788/guvi-buildathon.git
cd guvi-buildathon/frontend
```

### 2. Configure API Endpoint

Edit `script.js` and update the `API_BASE_URL` to your backend API:

```javascript
const API_BASE_URL = 'http://your-api-server:port';
```

### 3. Run the Frontend

You can serve the frontend using any static file server:

**Using Python:**
```bash
python -m http.server 3000
```

**Using Node.js (http-server):**
```bash
npx http-server -p 3000
```

Open `http://localhost:3000` in your browser.

## API Integration

### Endpoint

```
POST /detect-voice
```

### Request Body

```json
{
  "audio_base64": "base64_encoded_audio_data",
  "language": "auto"
}
```

### Response

```json
{
  "classification": "AI_GENERATED" | "HUMAN",
  "confidence": 0.95,
  "language": "English",
  "explanation": "Analysis details...",
  "characteristics": {
    "pitch_variance": 0.85,
    "spectral_flatness": 0.72,
    "natural_pauses": false
  }
}
```

## Team

**Team 404 Found** - GUVI Buildathon 2026
