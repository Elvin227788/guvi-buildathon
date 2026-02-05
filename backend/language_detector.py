"""
Language Detector Module
Detects language from audio for multi-language voice analysis
Supports: Tamil, English, Hindi, Malayalam, Telugu
"""

import numpy as np
from typing import Dict, Any, Optional
import os

# Try to import speech recognition for language detection
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False


class LanguageDetector:
    """
    Language detection for multi-language voice samples.
    
    Supported languages:
    - English (en)
    - Tamil (ta)
    - Hindi (hi)
    - Malayalam (ml)
    - Telugu (te)
    """
    
    LANGUAGE_CODES = {
        "en": "English",
        "ta": "Tamil",
        "hi": "Hindi",
        "ml": "Malayalam",
        "te": "Telugu",
        "auto": "Auto"
    }
    
    LANGUAGE_NAMES = {v: k for k, v in LANGUAGE_CODES.items()}
    
    # Typical frequency ranges for different languages (approximate)
    # Used as fallback when speech recognition is unavailable
    LANGUAGE_CHARACTERISTICS = {
        "English": {
            "typical_pitch_range": (85, 255),
            "speech_rate_range": (0.35, 0.55),
            "pause_frequency": "medium"
        },
        "Tamil": {
            "typical_pitch_range": (100, 300),
            "speech_rate_range": (0.40, 0.60),
            "pause_frequency": "high"
        },
        "Hindi": {
            "typical_pitch_range": (90, 280),
            "speech_rate_range": (0.38, 0.58),
            "pause_frequency": "medium"
        },
        "Malayalam": {
            "typical_pitch_range": (95, 290),
            "speech_rate_range": (0.42, 0.62),
            "pause_frequency": "high"
        },
        "Telugu": {
            "typical_pitch_range": (95, 285),
            "speech_rate_range": (0.40, 0.58),
            "pause_frequency": "medium"
        }
    }
    
    def __init__(self):
        """Initialize the language detector"""
        self.recognizer = None
        if SPEECH_RECOGNITION_AVAILABLE:
            self.recognizer = sr.Recognizer()
    
    def code_to_name(self, code: str) -> str:
        """Convert language code to full name"""
        return self.LANGUAGE_CODES.get(code.lower(), "English")
    
    def name_to_code(self, name: str) -> str:
        """Convert language name to code"""
        return self.LANGUAGE_NAMES.get(name, "en")
    
    def detect(self, audio_path: str, features: Optional[Dict[str, Any]] = None) -> str:
        """
        Detect the language of an audio file.
        
        Args:
            audio_path: Path to the audio file
            features: Optional pre-extracted audio features
            
        Returns:
            Detected language name
        """
        # Try speech recognition-based detection first
        if SPEECH_RECOGNITION_AVAILABLE and self.recognizer:
            detected = self._detect_with_speech_recognition(audio_path)
            if detected:
                return detected
        
        # Fallback to feature-based heuristic detection
        if features:
            return self._detect_from_features(features)
        
        # Default to English if detection fails
        return "English"
    
    def _detect_with_speech_recognition(self, audio_path: str) -> Optional[str]:
        """
        Use speech recognition to detect language.
        Attempts recognition with different language models.
        """
        try:
            # Convert audio to WAV format for speech recognition
            import subprocess
            import tempfile
            
            # Create temp WAV file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = tmp.name
            
            # Convert to WAV using ffmpeg (if available)
            try:
                subprocess.run(
                    ["ffmpeg", "-i", audio_path, "-ar", "16000", "-ac", "1", 
                     "-y", tmp_path],
                    capture_output=True,
                    timeout=30
                )
            except (subprocess.TimeoutExpired, FileNotFoundError):
                # ffmpeg not available, try direct loading
                tmp_path = audio_path
            
            # Try recognition with each language
            with sr.AudioFile(tmp_path) as source:
                audio = self.recognizer.record(source, duration=10)  # First 10 seconds
            
            # Try each language and see which gives best result
            language_scores = {}
            
            # Language codes for Google Speech Recognition
            lang_codes = {
                "English": "en-US",
                "Tamil": "ta-IN",
                "Hindi": "hi-IN",
                "Malayalam": "ml-IN",
                "Telugu": "te-IN"
            }
            
            for lang_name, lang_code in lang_codes.items():
                try:
                    result = self.recognizer.recognize_google(
                        audio, 
                        language=lang_code,
                        show_all=True
                    )
                    if result and 'alternative' in result:
                        # Use confidence as score
                        confidence = result['alternative'][0].get('confidence', 0)
                        language_scores[lang_name] = confidence
                except Exception:
                    continue
            
            # Clean up temp file
            if tmp_path != audio_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
            
            # Return language with highest confidence
            if language_scores:
                return max(language_scores, key=language_scores.get)
            
            return None
            
        except Exception:
            return None
    
    def _detect_from_features(self, features: Dict[str, Any]) -> str:
        """
        Detect language from audio features using heuristics.
        This is a fallback method when speech recognition is unavailable.
        """
        scores = {lang: 0.0 for lang in self.LANGUAGE_CHARACTERISTICS.keys()}
        
        speech_rate = features.get("speech_rate", 0.5)
        pitch_var = features.get("pitch_variance", 0.3)
        has_pauses = features.get("natural_pauses", True)
        
        # Score based on speech rate
        for lang, chars in self.LANGUAGE_CHARACTERISTICS.items():
            rate_range = chars["speech_rate_range"]
            if rate_range[0] <= speech_rate <= rate_range[1]:
                scores[lang] += 0.3
            elif abs(speech_rate - sum(rate_range)/2) < 0.15:
                scores[lang] += 0.15
        
        # Score based on pause patterns
        for lang, chars in self.LANGUAGE_CHARACTERISTICS.items():
            pause_freq = chars["pause_frequency"]
            if pause_freq == "high" and has_pauses:
                scores[lang] += 0.2
            elif pause_freq == "medium":
                scores[lang] += 0.15
            elif pause_freq == "low" and not has_pauses:
                scores[lang] += 0.1
        
        # Analyze spectral features for language patterns
        spectral = features.get("spectral_features", {})
        if spectral:
            centroid = spectral.get("centroid", 1500)
            # Dravidian languages (Tamil, Malayalam, Telugu) tend to have
            # different spectral characteristics than Indo-European (Hindi, English)
            if centroid > 2000:
                scores["Tamil"] += 0.1
                scores["Malayalam"] += 0.1
                scores["Telugu"] += 0.1
            else:
                scores["English"] += 0.1
                scores["Hindi"] += 0.1
        
        # Add small random factor to break ties
        for lang in scores:
            scores[lang] += np.random.uniform(0, 0.05)
        
        # Return language with highest score
        detected = max(scores, key=scores.get)
        
        return detected
    
    def get_supported_languages(self) -> list:
        """Get list of supported languages"""
        return list(self.LANGUAGE_CHARACTERISTICS.keys())
    
    def get_language_info(self, language: str) -> Dict[str, Any]:
        """Get characteristics info for a language"""
        if language in self.LANGUAGE_CHARACTERISTICS:
            return self.LANGUAGE_CHARACTERISTICS[language]
        return self.LANGUAGE_CHARACTERISTICS.get("English", {})
