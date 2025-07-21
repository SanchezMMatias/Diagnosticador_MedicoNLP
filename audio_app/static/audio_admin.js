// JavaScript para mejorar la funcionalidad del admin de AudioMedico

document.addEventListener('DOMContentLoaded', function() {
    console.log('🎵 AudioMedico Admin JS cargado');
    
    // Inicializar todas las funcionalidades
    initAudioPlayers();
    initActionButtons();
    initFormEnhancements();
    initProgressTracking();
    initKeyboardShortcuts();
    initTooltips();
});

// Funcionalidad para los reproductores de audio
function initAudioPlayers() {
    const audioPlayers = document.querySelectorAll('audio');
    
    audioPlayers.forEach((audio, index) => {
        // Añadir controles personalizados
        setupAudioControls(audio);
        
        // Event listeners para el audio
        audio.addEventListener('loadstart', function() {
            showLoadingIndicator(this);
        });
        
        audio.addEventListener('canplay', function() {
            hideLoadingIndicator(this);
        });
        
        audio.addEventListener('error', function() {
            handleAudioError(this);
        });
        
        audio.addEventListener('play', function() {
            pauseOtherAudios(this);
        });
        
        // Añadir información de tiempo
        audio.addEventListener('timeupdate', function() {
            updateTimeDisplay(this);
        });
    });
}

function setupAudioControls(audio) {
    // Crear contenedor para controles personalizados
    const container = document.createElement('div');
    container.className = 'audio-controls-container';
    
    // Crear display de tiempo
    const timeDisplay = document.createElement('span');
    timeDisplay.className = 'audio-time-display';
    timeDisplay.textContent = '00:00 / 00:00';
    
    audio.parentNode.insertBefore(container, audio.nextSibling);
    container.appendChild(timeDisplay);
}

function showLoadingIndicator(audio) {
    const indicator = document.createElement('div');
    indicator.className = 'audio-loading';
    indicator.innerHTML = '⏳ Cargando audio...';
    audio.parentNode.insertBefore(indicator, audio.nextSibling);
}

function hideLoadingIndicator(audio) {
    const loading = audio.parentNode.querySelector('.audio-loading');
    if (loading) {
        loading.remove();
    }
}

function handleAudioError(audio) {
    const errorMsg = document.createElement('div');
    errorMsg.className = 'audio-error';
    errorMsg.innerHTML = '❌ Error al cargar el audio';
    errorMsg.style.color = '#dc3545';
    errorMsg.style.fontSize = '12px';
    errorMsg.style.marginTop = '5px';
    
    audio.parentNode.insertBefore(errorMsg, audio.nextSibling);
}

function pauseOtherAudios(currentAudio) {
    document.querySelectorAll('audio').forEach(audio => {
        if (audio !== currentAudio && !audio.paused) {
            audio.pause();
        }
    });
}

function updateTimeDisplay(audio) {
    const timeDisplay = audio.parentNode.querySelector('.audio-time-display');
    if (timeDisplay) {
        const current = formatTime(audio.currentTime);
        const duration = formatTime(audio.duration);
        timeDisplay.textContent = `${current} / ${duration}`;
    }
}

function formatTime(seconds) {
    if (isNaN(seconds)) return '00:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

// Funcionalidad para los botones de acción
function initActionButtons() {
    // Botones de descarga
    document.querySelectorAll('a[title="Descargar"]').forEach(button => {
        button.addEventListener('click', function(e) {
            showDownloadProgress(this);
        });
    });
    
    // Botones de procesamiento
    document.querySelectorAll('.action-btn-process').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            startProcessing(this);
        });
    });
}

function showDownloadProgress(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '⬇️ Descargando...';
    button.style.pointerEvents = 'none';
    
    setTimeout(() => {
        button.innerHTML = originalText;
        button.style.pointerEvents = 'auto';
        showNotification('Descarga iniciada', 'success');
    }, 2000);
}

function startProcessing(button) {
    const row = button.closest('tr');
    const statusCell = row.querySelector('.estado-badge');
    
    if (statusCell) {
        statusCell.textContent = 'PROCESANDO';
        statusCell.className = 'estado-badge estado-procesando';
        
        // Añadir spinner
        const spinner = document.createElement('span');
        spinner.className = 'processing-spinner';
        statusCell.appendChild(spinner);
    }
    
    showNotification('Procesamiento iniciado', 'info');
}

// Mejoras para el formulario
function initFormEnhancements() {
    // Auto-guardar borrador cada 30 segundos
    setInterval(autoSaveDraft, 30000);
    
    // Validación en tiempo real
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            validateTextarea(this);
        });
    });
    
    // Previsualización de archivos
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            previewFile(this);
        });
    });
}

function autoSaveDraft() {
    const form = document.querySelector('form');
    if (form) {
        const formData = new FormData(form);
        // Aquí podrías enviar los datos al servidor para guardar como borrador
        console.log('💾 Borrador guardado automáticamente');
    }
}

function validateTextarea(textarea) {
    const maxLength = textarea.getAttribute('maxlength');
    if (maxLength) {
        const remaining = maxLength - textarea.value.length;
        let counter = textarea.parentNode.querySelector('.char-counter');
        
        if (!counter) {
            counter = document.createElement('div');
            counter.className = 'char-counter';
            counter.style.fontSize = '12px';
            counter.style.color = '#6c757d';
            counter.style.textAlign = 'right';
            textarea.parentNode.appendChild(counter);
        }
        
        counter.textContent = `${remaining} caracteres restantes`;
        counter.style.color = remaining < 50 ? '#dc3545' : '#6c757d';
    }
}

function previewFile(input) {
    const file = input.files[0];
    if (file && file.type.startsWith('audio/')) {
        const preview = document.createElement('div');
        preview.className = 'file-preview';
        preview.innerHTML = `
            <div style="background: #e9ecef; padding: 10px; border-radius: 5px; margin-top: 10px;">
                <strong>📁 Archivo seleccionado:</strong> ${file.name}<br>
                <strong>📏 Tamaño:</strong> ${formatFileSize(file.size)}<br>
                <strong>🎵 Tipo:</strong> ${file.type}
            </div>
        `;
        
        // Remover preview anterior
        const oldPreview = input.parentNode.querySelector('.file-preview');
        if (oldPreview) {
            oldPreview.remove();
        }
        
        input.parentNode.insertBefore(preview, input.nextSibling);
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Seguimiento de progreso para operaciones largas
function initProgressTracking() {
    // Detectar operaciones de procesamiento
    const processingElements = document.querySelectorAll('.estado-procesando');
    processingElements.forEach(element => {
        pollProcessingStatus(element);
    });
}

function pollProcessingStatus(element) {
    // Simular consulta de estado cada 5 segundos
    const interval = setInterval(() => {
        // Aquí harías una consulta AJAX real al servidor
        const random = Math.random();
        if (random > 0.7) { // 30% chance de completar
            element.textContent = 'COMPLETADO';
            element.className = 'estado-badge estado-completado';
            clearInterval(interval);
            showNotification('Procesamiento completado', 'success');
        }
    }, 5000);
}

// Atajos de teclado
function initKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl + S para guardar
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            const saveButton = document.querySelector('input[value="Guardar"]');
            if (saveButton) {
                saveButton.click();
            }
        }
        
        // Ctrl + E para editar rápido
        if (e.ctrlKey && e.key === 'e') {
            e.preventDefault();
            const editButton = document.querySelector('.addlink');
            if (editButton) {
                editButton.click();
            }
        }
        
        // Espacio para play/pause del primer audio
        if (e.code === 'Space' && e.target.tagName !== 'TEXTAREA' && e.target.tagName !== 'INPUT') {
            e.preventDefault();
            const firstAudio = document.querySelector('audio');
            if (firstAudio) {
                firstAudio.paused ? firstAudio.play() : firstAudio.pause();
            }
        }
    });
}

// Tooltips mejorados
function initTooltips() {
    const elementsWithTooltip = document.querySelectorAll('[title]');
    elementsWithTooltip.forEach(element => {
        element.addEventListener('mouseenter', function(e) {
            showTooltip(e.target, e.target.getAttribute('title'));
        });
        
        element.addEventListener('mouseleave', function() {
            hideTooltip();
        });
    });
}

function showTooltip(element, text) {
    hideTooltip(); // Limpiar tooltip anterior
    
    const tooltip = document.createElement('div');
    tooltip.className = 'custom-tooltip';
    tooltip.textContent = text;
    tooltip.style.cssText = `
        position: absolute;
        background: #333;
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 12px;
        z-index: 10000;
        max-width: 200px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        pointer-events: none;
    `;
    
    document.body.appendChild(tooltip);
    
    // Posicionar tooltip
    const rect = element.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
    
    // Eliminar atributo title para evitar tooltip nativo
    element.setAttribute('data-original-title', text);
    element.removeAttribute('title');
}

function hideTooltip() {
    const tooltip = document.querySelector('.custom-tooltip');
    if (tooltip) {
        tooltip.remove();
    }
    
    // Restaurar títulos originales
    document.querySelectorAll('[data-original-title]').forEach(element => {
        element.setAttribute('title', element.getAttribute('data-original-title'));
        element.removeAttribute('data-original-title');
    });
}

// Sistema de notificaciones
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentNode.remove()" style="background:none; border:none; color:inherit; cursor:pointer; float:right;">×</button>
    `;
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 6px;
        color: white;
        z-index: 10001;
        min-width: 300px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        animation: slideInRight 0.3s ease;
    `;
    
    // Colores según tipo
    const colors = {
        'success': '#28a745',
        'error': '#dc3545',
        'info': '#17a2b8',
        'warning': '#ffc107'
    };
    
    notification.style.background = colors[type] || colors.info;
    
    document.body.appendChild(notification);
    
    // Auto-remove después de 5 segundos
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
}

// Animaciones CSS en JS
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .audio-time-display {
        font-size: 11px;
        color: #6c757d;
        margin-left: 10px;
        font-family: monospace;
    }
    
    .char-counter {
        transition: color 0.3s ease;
    }
`;
document.head.appendChild(style);

// Funciones utilitarias
window.AudioAdminUtils = {
    formatTime,
    formatFileSize,
    showNotification,
    pauseOtherAudios
};

console.log('✅ AudioMedico Admin JS inicializado completamente');