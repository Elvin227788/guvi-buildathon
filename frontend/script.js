// ===== Configuration =====
const API_BASE_URL = 'http://127.0.0.1:8000'; // Change this to your API endpoint
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

// ===== DOM Elements =====
const dropZone = document.getElementById('dropZone');
const audioFileInput = document.getElementById('audioFile');
const audioPreview = document.getElementById('audioPreview');
const audioPlayer = document.getElementById('audioPlayer');
const fileName = document.getElementById('fileName');
const removeFileBtn = document.getElementById('removeFile');
const analyzeBtn = document.getElementById('analyzeBtn');
const languageSelect = document.getElementById('languageSelect');
const resultsSection = document.getElementById('resultsSection');
const loadingOverlay = document.getElementById('loadingOverlay');
const newAnalysisBtn = document.getElementById('newAnalysisBtn');
const recordBtn = document.getElementById('recordBtn');
const recordStatus = document.getElementById('recordStatus');
const recordTimer = document.getElementById('recordTimer');
const audioCanvas = document.getElementById('audioCanvas');

// ===== State =====
let currentAudioBlob = null;
let currentAudioBase64 = null;
let isRecording = false;
let mediaRecorder = null;
let audioChunks = [];
let recordingStartTime = null;
let timerInterval = null;
let audioContext = null;
let analyser = null;
let animationId = null;

// ===== Tab Switching =====
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tabId = btn.dataset.tab;
        
        // Update active tab button
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Update active tab content
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
        document.getElementById(`${tabId}-tab`).classList.add('active');
    });
});

// ===== Drag and Drop =====
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

dropZone.addEventListener('click', () => {
    audioFileInput.click();
});

// ===== File Input =====
audioFileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

// ===== File Handling =====
function handleFileSelect(file) {
    // Validate file type
    const validTypes = ['audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/ogg', 'audio/x-m4a', 'audio/mp4'];
    if (!validTypes.includes(file.type) && !file.name.match(/\.(mp3|wav|ogg|m4a)$/i)) {
        showError('Please select a valid audio file (MP3, WAV, OGG, M4A)');
        return;
    }
    
    // Validate file size
    if (file.size > MAX_FILE_SIZE) {
        showError('File size exceeds 10MB limit');
        return;
    }
    
    // Set current audio
    currentAudioBlob = file;
    
    // Show preview
    fileName.textContent = file.name;
    audioPlayer.src = URL.createObjectURL(file);
    audioPreview.classList.remove('hidden');
    
    // Convert to base64
    const reader = new FileReader();
    reader.onload = () => {
        currentAudioBase64 = reader.result.split(',')[1];
        analyzeBtn.disabled = false;
    };
    reader.readAsDataURL(file);
}

// ===== Remove File =====
removeFileBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    resetAudio();
});

function resetAudio() {
    currentAudioBlob = null;
    currentAudioBase64 = null;
    audioFileInput.value = '';
    audioPlayer.src = '';
    audioPreview.classList.add('hidden');
    analyzeBtn.disabled = true;
    resultsSection.classList.add('hidden');
}

// ===== Audio Recording =====
recordBtn.addEventListener('click', async () => {
    if (isRecording) {
        stopRecording();
    } else {
        await startRecording();
    }
});

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        // Set up audio context for visualization
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        analyser = audioContext.createAnalyser();
        const source = audioContext.createMediaStreamSource(stream);
        source.connect(analyser);
        analyser.fftSize = 256;
        
        // Start visualizer
        visualize();
        
        // Set up media recorder
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        
        mediaRecorder.ondataavailable = (e) => {
            audioChunks.push(e.data);
        };
        
        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            handleRecordedAudio(audioBlob);
            stream.getTracks().forEach(track => track.stop());
        };
        
        // Start recording
        mediaRecorder.start();
        isRecording = true;
        recordingStartTime = Date.now();
        
        // Update UI
        recordBtn.classList.add('recording');
        recordBtn.innerHTML = '<i class="fas fa-stop"></i>';
        recordStatus.textContent = 'Recording...';
        recordTimer.classList.remove('hidden');
        
        // Start timer
        timerInterval = setInterval(updateTimer, 1000);
        
    } catch (err) {
        showError('Could not access microphone. Please grant permission.');
        console.error('Recording error:', err);
    }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
    }
    
    isRecording = false;
    
    // Stop visualizer
    if (animationId) {
        cancelAnimationFrame(animationId);
    }
    
    // Clear timer
    clearInterval(timerInterval);
    
    // Update UI
    recordBtn.classList.remove('recording');
    recordBtn.innerHTML = '<i class="fas fa-microphone"></i>';
    recordStatus.textContent = 'Click to start recording';
    recordTimer.classList.add('hidden');
}

function updateTimer() {
    const elapsed = Math.floor((Date.now() - recordingStartTime) / 1000);
    const minutes = Math.floor(elapsed / 60).toString().padStart(2, '0');
    const seconds = (elapsed % 60).toString().padStart(2, '0');
    recordTimer.textContent = `${minutes}:${seconds}`;
}

function handleRecordedAudio(blob) {
    currentAudioBlob = blob;
    
    // Show preview
    fileName.textContent = 'recorded-audio.wav';
    audioPlayer.src = URL.createObjectURL(blob);
    audioPreview.classList.remove('hidden');
    
    // Convert to base64
    const reader = new FileReader();
    reader.onload = () => {
        currentAudioBase64 = reader.result.split(',')[1];
        analyzeBtn.disabled = false;
    };
    reader.readAsDataURL(blob);
}

// ===== Audio Visualizer =====
function visualize() {
    const canvas = audioCanvas;
    const ctx = canvas.getContext('2d');
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    
    function draw() {
        animationId = requestAnimationFrame(draw);
        
        analyser.getByteFrequencyData(dataArray);
        
        ctx.fillStyle = '#020617';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        const barWidth = (canvas.width / bufferLength) * 2.5;
        let x = 0;
        
        for (let i = 0; i < bufferLength; i++) {
            const barHeight = (dataArray[i] / 255) * canvas.height;
            
            const gradient = ctx.createLinearGradient(0, canvas.height, 0, canvas.height - barHeight);
            gradient.addColorStop(0, '#6366f1');
            gradient.addColorStop(1, '#06b6d4');
            
            ctx.fillStyle = gradient;
            ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
            
            x += barWidth + 1;
        }
    }
    
    draw();
}

// ===== Analyze Audio =====
analyzeBtn.addEventListener('click', analyzeAudio);

async function analyzeAudio() {
    if (!currentAudioBase64) {
        showError('Please upload or record an audio file first');
        return;
    }
    
    const startTime = Date.now();
    
    // Show loading
    loadingOverlay.classList.remove('hidden');
    analyzeBtn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE_URL}/detect-voice`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                audio_base64: currentAudioBase64,
                language: languageSelect.value
            })
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        const processingTime = ((Date.now() - startTime) / 1000).toFixed(2);
        
        displayResults(data, processingTime);
        
    } catch (error) {
        console.error('Analysis error:', error);
        showError('Failed to analyze audio. Please check if the API server is running.');
    } finally {
        loadingOverlay.classList.add('hidden');
        analyzeBtn.disabled = false;
    }
}

// ===== Display Results =====
function displayResults(data, processingTime) {
    // Show results section
    resultsSection.classList.remove('hidden');
    
    // Classification badge
    const badge = document.getElementById('classificationBadge');
    const icon = document.getElementById('classificationIcon');
    const text = document.getElementById('classificationText');
    
    const isAI = data.classification === 'AI_GENERATED' || data.classification === 'AI Generated';
    
    badge.className = 'classification-badge ' + (isAI ? 'ai-generated' : 'human');
    icon.className = isAI ? 'fas fa-robot' : 'fas fa-user';
    text.textContent = isAI ? 'AI Generated' : 'Human Voice';
    
    // Confidence
    const confidence = typeof data.confidence === 'number' 
        ? (data.confidence > 1 ? data.confidence : data.confidence * 100)
        : parseFloat(data.confidence);
    
    document.getElementById('confidenceValue').textContent = `${confidence.toFixed(1)}%`;
    
    const confidenceFill = document.getElementById('confidenceFill');
    confidenceFill.style.width = `${confidence}%`;
    confidenceFill.className = 'confidence-fill ' + getConfidenceLevel(confidence);
    
    // Language and processing time
    document.getElementById('detectedLanguage').textContent = data.language || 'Unknown';
    document.getElementById('processingTime').textContent = `${processingTime}s`;
    
    // Explanation
    document.getElementById('explanationText').textContent = data.explanation || 'No explanation available.';
    
    // Characteristics
    const characteristicsGrid = document.getElementById('characteristicsGrid');
    characteristicsGrid.innerHTML = '';
    
    if (data.characteristics) {
        const characteristics = [
            { key: 'pitch_variance', label: 'Pitch Variance', icon: 'fas fa-wave-square' },
            { key: 'spectral_flatness', label: 'Spectral Flatness', icon: 'fas fa-chart-area' },
            { key: 'natural_pauses', label: 'Natural Pauses', icon: 'fas fa-pause-circle' },
            { key: 'speech_rate', label: 'Speech Rate', icon: 'fas fa-tachometer-alt' },
            { key: 'emotion_variance', label: 'Emotion Variance', icon: 'fas fa-theater-masks' },
            { key: 'background_noise', label: 'Background Noise', icon: 'fas fa-volume-up' }
        ];
        
        characteristics.forEach(char => {
            if (data.characteristics[char.key] !== undefined) {
                const value = data.characteristics[char.key];
                const displayValue = typeof value === 'boolean' 
                    ? (value ? 'Yes' : 'No')
                    : (typeof value === 'number' ? (value * 100).toFixed(0) + '%' : value);
                const barValue = typeof value === 'number' ? value * 100 : (value ? 100 : 0);
                
                characteristicsGrid.innerHTML += `
                    <div class="characteristic-item">
                        <span class="characteristic-label">${char.label}</span>
                        <span class="characteristic-value">${displayValue}</span>
                        <div class="characteristic-bar">
                            <div class="characteristic-fill" style="width: ${barValue}%"></div>
                        </div>
                    </div>
                `;
            }
        });
    }
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function getConfidenceLevel(confidence) {
    if (confidence >= 80) return 'high';
    if (confidence >= 50) return 'medium';
    return 'low';
}

// ===== New Analysis =====
newAnalysisBtn.addEventListener('click', () => {
    resetAudio();
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

// ===== Error Handling =====
function showError(message) {
    // Create error toast
    const toast = document.createElement('div');
    toast.className = 'error-toast';
    toast.innerHTML = `
        <i class="fas fa-exclamation-circle"></i>
        <span>${message}</span>
    `;
    
    // Add styles if not already present
    if (!document.getElementById('toast-styles')) {
        const style = document.createElement('style');
        style.id = 'toast-styles';
        style.textContent = `
            .error-toast {
                position: fixed;
                top: 20px;
                right: 20px;
                background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
                color: white;
                padding: 16px 24px;
                border-radius: 12px;
                display: flex;
                align-items: center;
                gap: 12px;
                font-weight: 500;
                z-index: 1000;
                animation: slideIn 0.3s ease, slideOut 0.3s ease 2.7s;
                box-shadow: 0 10px 25px rgba(239, 68, 68, 0.3);
            }
            
            .error-toast i {
                font-size: 1.2rem;
            }
            
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            @keyframes slideOut {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(100%);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(toast);
    
    // Remove after 3 seconds
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// ===== Smooth Scroll for Nav Links =====
document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', (e) => {
        const href = link.getAttribute('href');
        if (href.startsWith('#')) {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        }
    });
});

// ===== Initialize =====
document.addEventListener('DOMContentLoaded', () => {
    // Clear canvas on load
    const ctx = audioCanvas.getContext('2d');
    ctx.fillStyle = '#020617';
    ctx.fillRect(0, 0, audioCanvas.width, audioCanvas.height);
});
