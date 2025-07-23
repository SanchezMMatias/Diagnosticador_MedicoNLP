let mediaRecorder;
let audioChunks = [];
let isRecording = false;
let recordingStartTime;
let timerInterval;
let recordedBlob;

const uploadArea = document.getElementById('uploadArea');
const audioFile = document.getElementById('audioFile');
const audioForm = document.getElementById('audioForm');
const fileInfo = document.getElementById('fileInfo');
const fileDetails = document.getElementById('fileDetails');
const loading = document.getElementById('loading');
const submitBtn = document.getElementById('submitBtn');
const btnText = document.getElementById('btnText');

const recordButton = document.getElementById('recordButton');
const recordIcon = document.getElementById('recordIcon');
const recordStatus = document.getElementById('recordStatus');
const timer = document.getElementById('timer');
const recordControls = document.getElementById('recordControls');
const stopButton = document.getElementById('stopButton');

document.addEventListener('DOMContentLoaded', function () {
    uploadArea.addEventListener('click', () => audioFile.click());
    uploadArea.addEventListener('dragover', (e) => e.preventDefault());
    uploadArea.addEventListener('drop', handleDrop);
    audioFile.addEventListener('change', handleFileSelect);
    audioForm.addEventListener('submit', handleSubmit);
    recordButton.addEventListener('click', toggleRecording);
    stopButton.addEventListener('click', stopRecording);
});

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

    mediaRecorder.ondataavailable = (event) => audioChunks.push(event.data);

    mediaRecorder.onstop = () => {
        recordedBlob = new Blob(audioChunks, { type: 'audio/wav' });
        const audioFileRecorded = new File([recordedBlob], 'grabacion_medica.wav', { type: 'audio/wav' });
        showFileInfo(audioFileRecorded, true);
        stream.getTracks().forEach(track => track.stop());
    };

    mediaRecorder.start();
    isRecording = true;
    recordingStartTime = Date.now();
    recordButton.classList.add('recording');
    recordIcon.textContent = '⏸️';
    recordStatus.textContent = 'Grabando...';
    recordControls.style.display = 'block';
    timerInterval = setInterval(updateTimer, 1000);
}

function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
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

function handleDrop(e) {
    e.preventDefault();
    const files = e.dataTransfer.files;
    if (files.length > 0 && files[0].type.startsWith('audio/')) {
        audioFile.files = files;
        showFileInfo(files[0]);
    } else {
        showAlert('Por favor selecciona un archivo de audio válido.', 'error');
    }
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) showFileInfo(file);
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

    uploadArea.innerHTML = `
        <span class="upload-icon">✅</span>
        <div class="upload-text">Audio seleccionado: ${file.name}</div>
        <div class="upload-subtext">${isRecorded ? 'Grabado con micrófono' : 'Haz clic para cambiar el archivo'}</div>
    `;

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
        showAlert('Por favor ingresa un título para el caso.', 'error');
        return;
    }

    if (!file && !recordedBlob) {
        showAlert('Por favor graba un audio o selecciona un archivo.', 'error');
        return;
    }

    uploadFile(titulo, file || recordedBlob);
}

function uploadFile(titulo, file) {
    const formData = new FormData();
    formData.append('titulo', titulo);
    formData.append('archivo_audio', file);

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    formData.append('csrfmiddlewaretoken', csrfToken);

    loading.style.display = 'block';
    submitBtn.disabled = true;
    btnText.textContent = '🔍 Subiendo...';

    fetch('/audio/subir_audio/', {
        method: 'POST',
        body: formData,
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => response.json())  // <-- CORRECCIÓN IMPORTANTE
    .then(data => {
        if (data.success) {
            showAlert('Audio subido correctamente', 'success');
            setTimeout(() => {
                window.location.href = data.url_analisis;  // Redirige a la página de análisis
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

function hideLoading() {
    loading.style.display = 'none';
    submitBtn.disabled = false;
    btnText.textContent = '🔍 Analizar Audio Médico';
}

function showAlert(message, type) {
    const existingAlert = document.querySelector('.alert');
    if (existingAlert) existingAlert.remove();

    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;

    document.querySelector('.main-section').insertBefore(alert, document.querySelector('form'));

    setTimeout(() => {
        if (alert.parentNode) alert.remove();
    }, 5000);
}
