"""
VoiceVerify AI - Backend API
AI-Generated Voice Detection for Multi-Language Audio

Team 404 Found - GUVI Buildathon 2026
"""

import base64
import tempfile
import os
import time
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from voice_detector import VoiceDetector
from audio_processor import AudioProcessor
from language_detector import LanguageDetector

# ===== FastAPI App =====
app = FastAPI(
    title="VoiceVerify AI",
    description="AI-Generated Voice Detection API supporting Tamil, English, Hindi, Malayalam, and Telugu",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ===== CORS Configuration =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Initialize Components =====
voice_detector = VoiceDetector()
audio_processor = AudioProcessor()
language_detector = LanguageDetector()


# ===== Request/Response Models =====
class VoiceDetectionRequest(BaseModel):
    """Request model for voice detection"""
    audio_base64: str
    language: Optional[str] = "auto"  # auto, en, ta, hi, ml, te
    
    class Config:
        json_schema_extra = {
            "example": {
                "audio_base64": "base64_encoded_audio_data",
                "language": "auto"
            }
        }


class AudioCharacteristics(BaseModel):
    """Audio characteristics from analysis"""
    pitch_variance: float
    spectral_flatness: float
    natural_pauses: bool
    speech_rate: float
    emotion_variance: float
    background_noise: float


class VoiceDetectionResponse(BaseModel):
    """Response model for voice detection"""
    classification: str  # AI_GENERATED or HUMAN
    confidence: float
    language: str
    explanation: str
    characteristics: AudioCharacteristics
    
    class Config:
        json_schema_extra = {
            "example": {
                "classification": "AI_GENERATED",
                "confidence": 0.95,
                "language": "English",
                "explanation": "The audio exhibits uniform pitch patterns and lacks natural speech variations.",
                "characteristics": {
                    "pitch_variance": 0.15,
                    "spectral_flatness": 0.72,
                    "natural_pauses": False,
                    "speech_rate": 0.45,
                    "emotion_variance": 0.12,
                    "background_noise": 0.05
                }
            }
        }


# ===== API Endpoints =====
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "VoiceVerify AI",
        "version": "1.0.0",
        "description": "AI-Generated Voice Detection API",
        "supported_languages": ["English", "Tamil", "Hindi", "Malayalam", "Telugu"],
        "endpoints": {
            "detect": "POST /detect-voice",
            "health": "GET /health",
            "docs": "GET /docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": voice_detector.is_model_loaded(),
        "timestamp": time.time()
    }


@app.post("/detect-voice", response_model=VoiceDetectionResponse)
async def detect_voice(request: VoiceDetectionRequest):
    """
    Detect if a voice sample is AI-generated or human.
    
    - **audio_base64**: Base64 encoded audio file (MP3, WAV, OGG, M4A)
    - **language**: Optional language hint (auto, en, ta, hi, ml, te)
    
    Returns classification, confidence score, and detailed analysis.
    """
    try:
        # Decode base64 audio
        try:
            audio_bytes = base64.b64decode(request.audio_base64)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid base64 encoding: {str(e)}")
        
        # Validate audio size (max 10MB)
        if len(audio_bytes) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Audio file exceeds 10MB limit")
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name
        
        try:
            # Process audio
            audio_features = audio_processor.extract_features(temp_path)
            
            # Detect language if auto
            if request.language == "auto":
                detected_language = language_detector.detect(temp_path, audio_features)
            else:
                detected_language = language_detector.code_to_name(request.language)
            
            # Run voice detection
            detection_result = voice_detector.detect(audio_features, detected_language)
            
            # Build response
            response = VoiceDetectionResponse(
                classification=detection_result["classification"],
                confidence=detection_result["confidence"],
                language=detected_language,
                explanation=detection_result["explanation"],
                characteristics=AudioCharacteristics(
                    pitch_variance=audio_features["pitch_variance"],
                    spectral_flatness=audio_features["spectral_flatness"],
                    natural_pauses=audio_features["natural_pauses"],
                    speech_rate=audio_features["speech_rate"],
                    emotion_variance=audio_features["emotion_variance"],
                    background_noise=audio_features["background_noise"]
                )
            )
            
            return response
            
        finally:
            # Cleanup temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


# ===== Run Server =====
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
