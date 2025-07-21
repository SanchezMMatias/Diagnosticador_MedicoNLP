// Variables globales para grabación
let mediaRecorder;
let audioChunks = [];
let isRecording = false;
let recordingStartTime;
let timerInterval;
let recordedBlob;

// Referencias a elementos del DOM
const uploadArea = document.getElementById('uploadArea');
const audioFile = document.getElementById('audioFile');
const audioForm = document.getElementById('audioForm');
const fileInfo = document.getElementById('fileInfo');
const fileDetails = document.getElementById('fileDetails');
const loading = document.getElementById('loading');
const submitBtn = document.getElementById('submitBtn');
const btnText = document.getElementById('btnText');

// Elementos de grabación
const recordButton = document.getElementById('recordButton');
const recordIcon = document.getElementById('recordIcon');
const recordStatus = document.getElementById('recordStatus');
const timer = document.getElementById('timer');
const visualizer = document.getElementById('visualizer');
const wave = document.getElementById('wave');
const recordControls = document.getElementById('recordControls');
const stopButton = document.getElementById('stopButton');

// Configurar eventos cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    uploadArea.addEventListener('click', () => audioFile.click());
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    audioFile.addEventListener('change', handleFileSelect);
    audioForm.addEventListener('submit', handleSubmit);
    recordButton.addEventListener('click', toggleRecording);
    stopButton.addEventListener('click', stopRecording);
});

// Funcionalidad de grabación
async function toggleRecording() {
    if (!isRecording) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            startRecording(stream);
        } catch (error) {
            showAlert('Error al acceder al micrófono: ' + error.message, 'error');
        }
    } else {
        stopRecording();
    }
}

function startRecording(stream) {
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];
    
    mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
    };
    
    mediaRecorder.onstop = () => {
        recordedBlob = new Blob(audioChunks, { type: 'audio/wav' });
        const audioFile = new File([recordedBlob], 'grabacion_medica.wav', { type: 'audio/wav' });
        showFileInfo(audioFile, true);
        
        // Limpiar recursos
        stream.getTracks().forEach(track => track.stop());
    };
    
    mediaRecorder.start();
    isRecording = true;
    recordingStartTime = Date.now();
    
    // Actualizar UI
    recordButton.classList.add('recording');
    recordIcon.textContent = '⏸️';
    recordStatus.textContent = 'Grabando... (Haz clic para pausar)';
    visualizer.style.display = 'block';
    recordControls.style.display = 'block';
    
    // Iniciar timer
    timerInterval = setInterval(updateTimer, 1000);
    
    // Simular visualizador de audio
    simulateAudioVisualization();
}

function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        
        // Resetear UI
        recordButton.classList.remove('recording');
        recordIcon.textContent = '🎤';
        recordStatus.textContent = 'Grabación completada ✅';
        recordControls.style.display = 'none';
        
        clearInterval(timerInterval);
        
        showAlert('Grabación completada exitosamente', 'success');
    }
}

function updateTimer() {
    const elapsed = Math.floor((Date.now() - recordingStartTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    timer.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

function simulateAudioVisualization() {
    if (!isRecording) return;
    
    const randomWidth = Math.random() * 80 + 10;
    wave.style.width = randomWidth + '%';
    
    setTimeout(() => {
        if (isRecording) simulateAudioVisualization();
    }, 100);
}

// Funciones de drag and drop
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        const file = files[0];
        if (file.type.startsWith('audio/')) {
            audioFile.files = files;
            showFileInfo(file);
        } else {
            showAlert('Por favor selecciona un archivo de audio válido.', 'error');
        }
    }
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        showFileInfo(file);
    }
}

function showFileInfo(file, isRecorded = false) {
    const fileSize = (file.size / (1024 * 1024)).toFixed(2);
    const fileType = file.type || 'audio/wav';
    
    fileDetails.innerHTML = `
        <div><strong>Nombre:</strong> ${file.name}</div>
        <div><strong>Tamaño:</strong> ${fileSize} MB</div>
        <div><strong>Tipo:</strong> ${fileType}</div>
        <div><strong>Fuente:</strong> ${isRecorded ? 'Grabación directa' : 'Archivo cargado'}</div>
        <div><strong>Fecha:</strong> ${new Date().toLocaleDateString()}</div>
    `;
    
    fileInfo.style.display = 'block';
    
    // Actualizar el área de subida
    uploadArea.innerHTML = `
        <span class="upload-icon">✅</span>
        <div class="upload-text">Audio seleccionado: ${file.name}</div>
        <div class="upload-subtext">${isRecorded ? 'Grabado con micrófono' : 'Haz clic para cambiar el archivo'}</div>
    `;

    // Si es una grabación, simular que se ha "seleccionado" el archivo
    if (isRecorded && recordedBlob) {
        const dt = new DataTransfer();
        const audioFileObj = new File([recordedBlob], 'grabacion_medica.wav', { type: 'audio/wav' });
        dt.items.add(audioFileObj);
        audioFile.files = dt.files;
    }
}

function handleSubmit(e) {
    e.preventDefault();
    
    const titulo = document.getElementById('titulo').value.trim();
    const file = audioFile.files[0];
    
    if (!titulo) {
        showAlert('Por favor ingresa una identificación para el caso clínico.', 'error');
        return;
    }
    
    if (!file && !recordedBlob) {
        showAlert('Por favor graba un audio o selecciona un archivo.', 'error');
        return;
    }
    
    uploadFile(titulo, file || recordedBlob);
}

// Función uploadFile corregida
function uploadFile(titulo, file) {
    const formData = new FormData();
    formData.append('titulo', titulo);
    formData.append('archivo_audio', file);
    
    // Obtener CSRF token para Django
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    formData.append('csrfmiddlewaretoken', csrfToken);
    
    // Mostrar loading
    loading.style.display = 'block';
    submitBtn.disabled = true;
    btnText.textContent = '🔍 Analizando...';
    
    // CONEXIÓN REAL CON DJANGO - URL CORREGIDA
    fetch('/audio/subir_audio/', {  // ← URL corregida: /audio/subir_audio/
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',  // Para que Django sepa que es AJAX
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Audio subido y procesado exitosamente!', 'success');
            addAudioToList(data.titulo, new Date().toLocaleDateString(), (file.size / (1024 * 1024)).toFixed(2));
            resetForm();
            
            // Opcional: redirigir a la lista después de un tiempo
            setTimeout(() => {
                window.location.href = '/audio/lista/';  // Redirige a la lista de audios
            }, 2000);
        } else {
            showAlert('Error: ' + (data.message || JSON.stringify(data.errors)), 'error');
        }
        hideLoading();
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error al conectar con el servidor', 'error');
        hideLoading();
    });
}

function addAudioToList(titulo, fecha, tamaño) {
    const audioContainer = document.getElementById('audioContainer');
    const audioItem = document.createElement('div');
    audioItem.className = 'audio-item';
    audioItem.innerHTML = `
        <div class="audio-info">
            <div>
                <div class="audio-title">${titulo}</div>
                <div class="audio-meta">Subido: ${fecha} | Tamaño: ${tamaño} MB | Estado: Nuevo análisis</div>
            </div>
            <div class="diagnosis-status status-pending">⏳ Procesando IA</div>
        </div>
    `;
    audioContainer.insertBefore(audioItem, audioContainer.firstChild);
}

function resetForm() {
    audioForm.reset();
    fileInfo.style.display = 'none';
    visualizer.style.display = 'none';
    recordStatus.textContent = 'Presiona para comenzar grabación';
    timer.textContent = '00:00';
    recordedBlob = null;
    
    uploadArea.innerHTML = `
        <span class="upload-icon">🎵</span>
        <div class="upload-text">Arrastra tu archivo de audio médico aquí</div>
        <div class="upload-subtext">o haz clic para seleccionar (MP3, WAV, OGG, M4A, AAC)</div>
    `;
}

function hideLoading() {
    loading.style.display = 'none';
    submitBtn.disabled = false;
    btnText.textContent = '🔍 Analizar Audio Médico';
}

function showAlert(message, type) {
    const existingAlert = document.querySelector('.alert');
    if (existingAlert) {
        existingAlert.remove();
    }
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    
    document.querySelector('.main-section').insertBefore(alert, document.querySelector('form'));
    
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}