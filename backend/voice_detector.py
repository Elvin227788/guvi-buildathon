"""
Voice Detector Module
Classifies audio as AI-generated or human voice
"""

import numpy as np
from typing import Dict, Any, Optional
import os
import pickle


class VoiceDetector:
    """
    AI Voice Detection classifier.
    
    Uses audio features to determine if a voice sample is AI-generated or human.
    Features analyzed:
    - Pitch variance (AI tends to have more uniform pitch)
    - Spectral flatness (AI often has cleaner spectral content)
    - Natural pauses (humans have irregular pause patterns)
    - Speech rate consistency
    - Emotional variance
    - Background noise patterns
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the voice detector.
        
        Args:
            model_path: Optional path to a trained model file
        """
        self.model = None
        self.model_loaded = False
        
        # Try to load trained model
        if model_path and os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                self.model_loaded = True
            except Exception:
                pass
        
        # Feature weights for rule-based detection
        # (used when no trained model is available)
        self.feature_weights = {
            "pitch_variance": -0.25,      # Lower variance = more likely AI
            "spectral_flatness": 0.20,    # Higher flatness = more likely AI
            "natural_pauses": -0.20,      # Presence of natural pauses = more likely human
            "speech_rate": 0.10,          # Very consistent rate = more likely AI
            "emotion_variance": -0.20,    # Lower emotional variance = more likely AI
            "background_noise": -0.05     # Clean audio = slightly more likely AI
        }
        
        # Thresholds for AI detection indicators
        self.ai_indicators = {
            "low_pitch_variance": 0.15,
            "high_spectral_flatness": 0.4,
            "uniform_speech_rate": 0.1,
            "low_emotion_variance": 0.15
        }
    
    def is_model_loaded(self) -> bool:
        """Check if a trained model is loaded"""
        return self.model_loaded
    
    def detect(self, features: Dict[str, Any], language: str) -> Dict[str, Any]:
        """
        Detect if audio is AI-generated or human.
        
        Args:
            features: Dictionary of extracted audio features
            language: Detected or specified language
            
        Returns:
            Dictionary with classification, confidence, and explanation
        """
        if self.model_loaded and self.model is not None:
            return self._model_based_detection(features, language)
        else:
            return self._rule_based_detection(features, language)
    
    def _model_based_detection(self, features: Dict[str, Any], language: str) -> Dict[str, Any]:
        """Use trained ML model for detection"""
        try:
            # Prepare feature vector
            feature_vector = self._prepare_feature_vector(features)
            
            # Get prediction
            prediction = self.model.predict([feature_vector])[0]
            confidence = max(self.model.predict_proba([feature_vector])[0])
            
            classification = "AI_GENERATED" if prediction == 1 else "HUMAN"
            explanation = self._generate_explanation(features, classification, confidence, language)
            
            return {
                "classification": classification,
                "confidence": float(confidence),
                "explanation": explanation
            }
        except Exception:
            # Fallback to rule-based
            return self._rule_based_detection(features, language)
    
    def _rule_based_detection(self, features: Dict[str, Any], language: str) -> Dict[str, Any]:
        """
        Rule-based detection using feature analysis.
        Used when no trained model is available.
        """
        # Calculate AI score based on feature analysis
        ai_score = 0.5  # Start neutral
        ai_indicators = []
        human_indicators = []
        
        # Analyze pitch variance
        pitch_var = features.get("pitch_variance", 0.5)
        if pitch_var < self.ai_indicators["low_pitch_variance"]:
            ai_score += 0.15
            ai_indicators.append("uniform pitch patterns")
        elif pitch_var > 0.4:
            ai_score -= 0.15
            human_indicators.append("natural pitch variations")
        
        # Analyze spectral flatness
        spectral_flat = features.get("spectral_flatness", 0.5)
        if spectral_flat > self.ai_indicators["high_spectral_flatness"]:
            ai_score += 0.12
            ai_indicators.append("synthetic spectral characteristics")
        elif spectral_flat < 0.2:
            ai_score -= 0.10
            human_indicators.append("natural spectral content")
        
        # Analyze natural pauses
        has_natural_pauses = features.get("natural_pauses", True)
        if not has_natural_pauses:
            ai_score += 0.15
            ai_indicators.append("lack of natural speech pauses")
        else:
            ai_score -= 0.12
            human_indicators.append("natural pause patterns")
        
        # Analyze speech rate
        speech_rate = features.get("speech_rate", 0.5)
        # Very consistent speech rate is suspicious
        temporal = features.get("temporal_features", {})
        rms_std = temporal.get("rms_std", 0.1) if isinstance(temporal, dict) else 0.1
        if rms_std < 0.02:
            ai_score += 0.10
            ai_indicators.append("unusually consistent speech rhythm")
        
        # Analyze emotional variance
        emotion_var = features.get("emotion_variance", 0.3)
        if emotion_var < self.ai_indicators["low_emotion_variance"]:
            ai_score += 0.12
            ai_indicators.append("limited emotional expression")
        elif emotion_var > 0.4:
            ai_score -= 0.10
            human_indicators.append("dynamic emotional expression")
        
        # Analyze background noise
        bg_noise = features.get("background_noise", 0.1)
        if bg_noise < 0.02:
            ai_score += 0.05
            ai_indicators.append("unusually clean audio")
        elif bg_noise > 0.15:
            ai_score -= 0.05
            human_indicators.append("natural ambient sound")
        
        # Analyze MFCC patterns (if available)
        mfcc = features.get("mfcc_features", [])
        if mfcc and len(mfcc) >= 13:
            mfcc_variance = np.var(mfcc)
            if mfcc_variance < 50:
                ai_score += 0.08
            elif mfcc_variance > 200:
                ai_score -= 0.08
        
        # Clamp score to valid range
        ai_score = max(0.0, min(1.0, ai_score))
        
        # Determine classification
        if ai_score >= 0.55:
            classification = "AI_GENERATED"
            confidence = ai_score
        else:
            classification = "HUMAN"
            confidence = 1.0 - ai_score
        
        # Generate explanation
        explanation = self._generate_detailed_explanation(
            classification, 
            confidence, 
            ai_indicators, 
            human_indicators, 
            language
        )
        
        return {
            "classification": classification,
            "confidence": float(round(confidence, 4)),
            "explanation": explanation
        }
    
    def _prepare_feature_vector(self, features: Dict[str, Any]) -> list:
        """Prepare feature vector for ML model"""
        vector = [
            features.get("pitch_variance", 0.5),
            features.get("spectral_flatness", 0.5),
            1.0 if features.get("natural_pauses", True) else 0.0,
            features.get("speech_rate", 0.5),
            features.get("emotion_variance", 0.3),
            features.get("background_noise", 0.1)
        ]
        
        # Add MFCC features
        mfcc = features.get("mfcc_features", [0.0] * 13)
        vector.extend(mfcc[:13])
        
        # Add spectral features
        spectral = features.get("spectral_features", {})
        vector.extend([
            spectral.get("centroid", 0) / 10000,  # Normalize
            spectral.get("bandwidth", 0) / 5000,
            spectral.get("rolloff", 0) / 20000,
            spectral.get("contrast", 0) / 100
        ])
        
        return vector
    
    def _generate_explanation(self, features: Dict[str, Any], classification: str, 
                             confidence: float, language: str) -> str:
        """Generate explanation for model-based detection"""
        if classification == "AI_GENERATED":
            return (
                f"The {language} audio sample is classified as AI-generated with "
                f"{confidence*100:.1f}% confidence. The analysis detected patterns "
                "typically associated with synthetic speech synthesis."
            )
        else:
            return (
                f"The {language} audio sample is classified as human voice with "
                f"{confidence*100:.1f}% confidence. The analysis detected natural "
                "speech patterns and variations consistent with human speakers."
            )
    
    def _generate_detailed_explanation(self, classification: str, confidence: float,
                                       ai_indicators: list, human_indicators: list,
                                       language: str) -> str:
        """Generate detailed explanation for rule-based detection"""
        
        confidence_pct = confidence * 100
        
        if classification == "AI_GENERATED":
            explanation = f"The {language} audio sample appears to be AI-generated "
            explanation += f"(confidence: {confidence_pct:.1f}%). "
            
            if ai_indicators:
                explanation += "Key indicators include: "
                explanation += ", ".join(ai_indicators[:3])
                explanation += ". "
            
            explanation += "AI-generated voices often exhibit mechanical precision "
            explanation += "and lack the subtle imperfections found in human speech."
            
        else:
            explanation = f"The {language} audio sample appears to be human voice "
            explanation += f"(confidence: {confidence_pct:.1f}%). "
            
            if human_indicators:
                explanation += "Natural characteristics detected: "
                explanation += ", ".join(human_indicators[:3])
                explanation += ". "
            
            explanation += "Human voices typically display natural variations in "
            explanation += "pitch, rhythm, and emotional expression."
        
        return explanation


class VoiceDetectorTrainer:
    """Helper class to train custom voice detection models"""
    
    def __init__(self):
        self.model = None
    
    def train(self, X: np.ndarray, y: np.ndarray, model_type: str = "random_forest"):
        """
        Train a voice detection model.
        
        Args:
            X: Feature matrix
            y: Labels (0 = human, 1 = AI)
            model_type: Type of model to train
        """
        from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
        from sklearn.svm import SVC
        from sklearn.model_selection import cross_val_score
        
        models = {
            "random_forest": RandomForestClassifier(n_estimators=100, random_state=42),
            "gradient_boosting": GradientBoostingClassifier(n_estimators=100, random_state=42),
            "svm": SVC(kernel='rbf', probability=True, random_state=42)
        }
        
        if model_type not in models:
            model_type = "random_forest"
        
        self.model = models[model_type]
        
        # Cross-validation
        scores = cross_val_score(self.model, X, y, cv=5)
        print(f"Cross-validation accuracy: {scores.mean():.3f} (+/- {scores.std()*2:.3f})")
        
        # Train final model
        self.model.fit(X, y)
        
        return self.model
    
    def save(self, path: str):
        """Save trained model to file"""
        if self.model is not None:
            with open(path, 'wb') as f:
                pickle.dump(self.model, f)
    
    def load(self, path: str):
        """Load trained model from file"""
        with open(path, 'rb') as f:
            self.model = pickle.load(f)
        return self.model
