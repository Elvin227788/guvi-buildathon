"""
Audio Processor Module
Extracts audio features for voice detection analysis
"""

import numpy as np
import librosa
import warnings

warnings.filterwarnings("ignore")


class AudioProcessor:
    """Process audio files and extract features for AI voice detection"""
    
    def __init__(self, sample_rate: int = 22050):
        self.sample_rate = sample_rate
    
    def extract_features(self, audio_path: str) -> dict:
        """
        Extract comprehensive audio features from an audio file.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Dictionary containing extracted features
        """
        try:
            # Load audio file
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Extract features
            features = {
                "pitch_variance": self._calculate_pitch_variance(y, sr),
                "spectral_flatness": self._calculate_spectral_flatness(y),
                "natural_pauses": self._detect_natural_pauses(y, sr),
                "speech_rate": self._calculate_speech_rate(y, sr),
                "emotion_variance": self._calculate_emotion_variance(y, sr),
                "background_noise": self._calculate_background_noise(y),
                "mfcc_features": self._extract_mfcc(y, sr),
                "spectral_features": self._extract_spectral_features(y, sr),
                "temporal_features": self._extract_temporal_features(y, sr),
                "duration": len(y) / sr
            }
            
            return features
            
        except Exception as e:
            raise RuntimeError(f"Failed to process audio: {str(e)}")
    
    def _calculate_pitch_variance(self, y: np.ndarray, sr: int) -> float:
        """Calculate variance in pitch/fundamental frequency"""
        try:
            # Extract pitch using piptrack
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            
            # Get pitches with significant magnitude
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            if len(pitch_values) < 2:
                return 0.5  # Default for insufficient data
            
            # Normalize variance to 0-1 range
            variance = np.var(pitch_values)
            normalized_variance = min(1.0, variance / 10000)  # Normalize
            
            return float(normalized_variance)
            
        except Exception:
            return 0.5
    
    def _calculate_spectral_flatness(self, y: np.ndarray) -> float:
        """Calculate spectral flatness (tonality coefficient)"""
        try:
            flatness = librosa.feature.spectral_flatness(y=y)
            mean_flatness = float(np.mean(flatness))
            return min(1.0, max(0.0, mean_flatness))
        except Exception:
            return 0.5
    
    def _detect_natural_pauses(self, y: np.ndarray, sr: int) -> bool:
        """Detect if audio has natural speech pauses"""
        try:
            # Calculate RMS energy
            rms = librosa.feature.rms(y=y)[0]
            
            # Find silent/quiet regions
            threshold = np.mean(rms) * 0.3
            silent_frames = rms < threshold
            
            # Count pause regions (consecutive silent frames)
            pause_count = 0
            in_pause = False
            pause_lengths = []
            current_pause = 0
            
            for is_silent in silent_frames:
                if is_silent:
                    if not in_pause:
                        in_pause = True
                        current_pause = 1
                    else:
                        current_pause += 1
                else:
                    if in_pause:
                        pause_lengths.append(current_pause)
                        pause_count += 1
                        in_pause = False
                        current_pause = 0
            
            # Natural speech typically has varied pause lengths
            if len(pause_lengths) < 2:
                return False
            
            pause_variance = np.var(pause_lengths)
            return pause_variance > 5 and pause_count >= 2
            
        except Exception:
            return True
    
    def _calculate_speech_rate(self, y: np.ndarray, sr: int) -> float:
        """Calculate speech rate (syllables per second estimate)"""
        try:
            # Onset detection for syllable estimation
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)
            
            duration = len(y) / sr
            if duration < 0.5:
                return 0.5
            
            # Estimate syllables per second
            syllable_rate = len(onsets) / duration
            
            # Normalize to 0-1 (typical speech is 3-6 syllables/sec)
            normalized_rate = min(1.0, max(0.0, syllable_rate / 8.0))
            
            return float(normalized_rate)
            
        except Exception:
            return 0.5
    
    def _calculate_emotion_variance(self, y: np.ndarray, sr: int) -> float:
        """Calculate emotional variance based on energy and pitch dynamics"""
        try:
            # RMS energy variation
            rms = librosa.feature.rms(y=y)[0]
            energy_variance = np.var(rms)
            
            # Spectral centroid variation (brightness)
            centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            centroid_variance = np.var(centroid)
            
            # Combine metrics
            combined_variance = (energy_variance * 100 + centroid_variance / 1000) / 2
            normalized = min(1.0, max(0.0, combined_variance))
            
            return float(normalized)
            
        except Exception:
            return 0.3
    
    def _calculate_background_noise(self, y: np.ndarray) -> float:
        """Estimate background noise level"""
        try:
            # Sort frames by energy
            rms = librosa.feature.rms(y=y)[0]
            sorted_rms = np.sort(rms)
            
            # Estimate noise floor from lowest 10% of frames
            noise_floor = np.mean(sorted_rms[:max(1, len(sorted_rms) // 10)])
            signal_level = np.mean(sorted_rms[-len(sorted_rms) // 2:])
            
            if signal_level == 0:
                return 0.5
            
            # SNR-based noise estimate
            noise_ratio = noise_floor / signal_level
            
            return float(min(1.0, max(0.0, noise_ratio)))
            
        except Exception:
            return 0.1
    
    def _extract_mfcc(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Extract MFCC features"""
        try:
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            return np.mean(mfccs, axis=1).tolist()
        except Exception:
            return [0.0] * 13
    
    def _extract_spectral_features(self, y: np.ndarray, sr: int) -> dict:
        """Extract spectral features"""
        try:
            return {
                "centroid": float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))),
                "bandwidth": float(np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))),
                "rolloff": float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))),
                "contrast": float(np.mean(librosa.feature.spectral_contrast(y=y, sr=sr)))
            }
        except Exception:
            return {"centroid": 0, "bandwidth": 0, "rolloff": 0, "contrast": 0}
    
    def _extract_temporal_features(self, y: np.ndarray, sr: int) -> dict:
        """Extract temporal features"""
        try:
            return {
                "zero_crossing_rate": float(np.mean(librosa.feature.zero_crossing_rate(y))),
                "tempo": float(librosa.beat.beat_track(y=y, sr=sr)[0]),
                "rms_mean": float(np.mean(librosa.feature.rms(y=y))),
                "rms_std": float(np.std(librosa.feature.rms(y=y)))
            }
        except Exception:
            return {"zero_crossing_rate": 0, "tempo": 0, "rms_mean": 0, "rms_std": 0}
