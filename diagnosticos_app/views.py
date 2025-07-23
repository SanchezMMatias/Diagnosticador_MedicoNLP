import os
import json
import torch
import librosa
import traceback
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from transformers import WhisperProcessor, WhisperForConditionalGeneration
from safetensors.torch import load_file

from audio_app.models import AudioMedico
from .models import Diagnostico

import soundfile as sf
import numpy as np
from pydub import AudioSegment
from pydub.utils import which
import tempfile
import wave
import struct
from datetime import datetime

# Configurar FFmpeg para pydub
def setup_ffmpeg():
    """Configura FFmpeg para pydub."""
    try:
        # Tu ruta personalizada de FFmpeg
        custom_ffmpeg_path = r"C:\Users\adm97\Downloads\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe"
        
        # Verificar si existe tu ruta personalizada primero
        if os.path.exists(custom_ffmpeg_path):
            AudioSegment.converter = custom_ffmpeg_path
            print(f"✅ FFmpeg configurado con tu ruta personalizada: {custom_ffmpeg_path}")
            return True
        
        # Intentar encontrar FFmpeg en el sistema como fallback
        ffmpeg_path = which("ffmpeg")
        if ffmpeg_path:
            AudioSegment.converter = ffmpeg_path
            print(f"✅ FFmpeg encontrado en el sistema: {ffmpeg_path}")
            return True
        
        # Rutas comunes donde podría estar FFmpeg como último recurso
        possible_paths = [
            r"C:\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
            "/usr/bin/ffmpeg",
            "/usr/local/bin/ffmpeg",
            "/opt/homebrew/bin/ffmpeg"  # macOS con Homebrew
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                AudioSegment.converter = path
                print(f"✅ FFmpeg configurado en ruta común: {path}")
                return True
        
        print("⚠️ FFmpeg no encontrado en ninguna ruta")
        return False
    except Exception as e:
        print(f"⚠️ Error configurando FFmpeg: {e}")
        return False

# Llamar a la configuración al inicio
setup_ffmpeg()

# Rutas a los modelos
WHISPER_MODEL_PATH = r"D:\archivos Universidad\IA\Lab03IA\audio_app\models\model.safetensors"
CLINICAL_MODEL_PATH = r"D:\archivos Universidad\IA\Lab03IA\audio_app\models\clinical_bert_diagnostic_model_group.pth"

# Variables globales para los modelos
whisper_processor = None
whisper_model = None
clinical_tokenizer = None
clinical_model = None

def load_custom_whisper_model():
    """Carga el modelo Whisper personalizado."""
    global whisper_processor, whisper_model
    if whisper_processor is not None and whisper_model is not None:
        return

    print("--- 🚀 Iniciando carga del modelo Whisper PERSONALIZADO ---")
    
    if not os.path.exists(WHISPER_MODEL_PATH):
        error_msg = f"ERROR CRÍTICO: No se encontró el modelo Whisper en {WHISPER_MODEL_PATH}"
        print(f"❌ {error_msg}")
        raise FileNotFoundError(error_msg)

    try:
        # Cargar Whisper
        print("🔄 Cargando procesador de 'openai/whisper-small'...")
        whisper_processor = WhisperProcessor.from_pretrained("openai/whisper-small")
        print("✅ Procesador 'small' cargado.")

        print("🔄 Cargando arquitectura de 'openai/whisper-small'...")
        whisper_model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small")
        print("✅ Arquitectura 'small' cargada.")

        print(f"🔄 Cargando pesos personalizados desde: {WHISPER_MODEL_PATH}")
        state_dict = load_file(WHISPER_MODEL_PATH, device="cpu")
        whisper_model.load_state_dict(state_dict, strict=False)
        
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        whisper_model.to(device)
        whisper_model.eval()
        print(f"✅ Modelo Whisper listo en dispositivo '{device}'")
        print("--- ✨ Carga del modelo Whisper finalizada ---")

    except Exception as e:
        whisper_processor = None
        whisper_model = None
        print(f"❌ ERROR durante la carga de Whisper: {e}")
        raise e

def load_clinical_model():
    """Carga el modelo clínico BERT para diagnóstico."""
    global clinical_tokenizer, clinical_model
    if clinical_tokenizer is not None and clinical_model is not None:
        return

    print("--- 🚀 Iniciando carga del modelo clínico BERT ---")
    
    if not os.path.exists(CLINICAL_MODEL_PATH):
        error_msg = f"ERROR CRÍTICO: No se encontró el modelo clínico en {CLINICAL_MODEL_PATH}"
        print(f"❌ {error_msg}")
        raise FileNotFoundError(error_msg)

    try:
        # Cargar tokenizer y modelo base
        print("🔄 Cargando tokenizer clínico...")
        clinical_tokenizer = AutoTokenizer.from_pretrained("emilyalsentzer/Bio_ClinicalBERT")
        
        print("🔄 Cargando arquitectura del modelo...")
        clinical_model = AutoModelForSequenceClassification.from_pretrained(
            "emilyalsentzer/Bio_ClinicalBERT",
            num_labels=5  # Ajustar según tu modelo
        )
        
        # Cargar pesos personalizados
        print(f"🔄 Cargando pesos personalizados desde: {CLINICAL_MODEL_PATH}")
        # SOLUCIÓN: Añadir weights_only=True para seguridad en PyTorch >= 2.1
        state_dict = torch.load(CLINICAL_MODEL_PATH, map_location=torch.device('cpu'), weights_only=True)
        clinical_model.load_state_dict(state_dict)
        
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        clinical_model.to(device)
        clinical_model.eval()
        print(f"✅ Modelo clínico listo en dispositivo '{device}'")
        print("--- ✨ Carga del modelo clínico finalizada ---")

    except Exception as e:
        clinical_tokenizer = None
        clinical_model = None
        print(f"❌ ERROR durante la carga del modelo clínico: {e}")
        raise e

def validate_wav_file(file_path):
    """Valida y verifica un archivo WAV."""
    try:
        with wave.open(file_path, 'rb') as wav_file:
            # Verificar parámetros básicos
            frames = wav_file.getnframes()
            sample_width = wav_file.getsampwidth()
            framerate = wav_file.getframerate()
            channels = wav_file.getnchannels()
            
            print(f"📊 WAV Info - Frames: {frames}, Sample Width: {sample_width}, Rate: {framerate}, Channels: {channels}")
            
            if frames == 0:
                print("❌ Archivo WAV vacío")
                return False
                
            return True
    except Exception as e:
        print(f"❌ Error validando WAV: {e}")
        return False

def convert_to_standard_wav(input_path, output_path):
    """Convierte cualquier archivo de audio a WAV estándar."""
    try:
        print(f"🔄 Convirtiendo a WAV estándar: {input_path}")
        
        # Intentar diferentes métodos de carga con pydub
        audio_segment = None
        methods = [
            lambda: AudioSegment.from_wav(input_path),
            lambda: AudioSegment.from_file(input_path, format="wav"),
            lambda: AudioSegment.from_file(input_path),
        ]
        
        for i, method in enumerate(methods, 1):
            try:
                print(f"🔄 Intento {i} de carga...")
                audio_segment = method()
                break
            except Exception as e:
                print(f"❌ Método {i} falló: {e}")
                continue
        
        if audio_segment is None:
            print("❌ No se pudo cargar el archivo con pydub")
            return False
        
        # Normalizar formato
        audio_segment = audio_segment.set_frame_rate(16000)
        audio_segment = audio_segment.set_channels(1)
        audio_segment = audio_segment.set_sample_width(2)  # 16-bit
        
        # Exportar
        audio_segment.export(output_path, format="wav")
        print(f"✅ Archivo convertido exitosamente a: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error en conversión: {e}")
        return False

def read_audio_raw(file_path):
    """Lee un archivo de audio interpretándolo como datos raw."""
    try:
        print("🔄 Intentando lectura raw del archivo...")
        
        with open(file_path, 'rb') as f:
            # Saltar header WAV típico (44 bytes)
            f.seek(44)
            raw_data = f.read()
        
        if len(raw_data) == 0:
            print("❌ No hay datos después del header")
            return None, None
        
        # Interpretar como 16-bit PCM
        if len(raw_data) % 2 != 0:
            raw_data = raw_data[:-1]  # Quitar byte extra si existe
        
        # Convertir bytes a array numpy
        audio_array = np.frombuffer(raw_data, dtype=np.int16)
        
        # Normalizar a float32 entre -1 y 1
        audio_array = audio_array.astype(np.float32) / 32768.0
        
        print(f"✅ Lectura raw exitosa - Samples: {len(audio_array)}")
        return audio_array, 16000
        
    except Exception as e:
        print(f"❌ Error en lectura raw: {e}")
        return None, None

def procesar_audio_con_whisper(audio_path, language="es"):
    """Transcribe un archivo de audio usando Whisper con múltiples fallbacks mejorados."""
    try:
        print(f"🔍 Verificando archivo de audio: {audio_path}")
        
        if not os.path.exists(audio_path) or os.path.getsize(audio_path) < 100:
            print(f"❌ Archivo de audio no encontrado o inválido: {audio_path}")
            return None
        
        print(f"📏 Tamaño del archivo: {os.path.getsize(audio_path)} bytes")
        
        audio_array, sample_rate = None, 16000
        
        # --- LÓGICA DE CARGA DE AUDIO RESTAURADA ---
        # Método 1: Validar WAV y cargar con soundfile
        if audio_path.lower().endswith('.wav'):
            if validate_wav_file(audio_path):
                try:
                    print("🔄 Método 1: Cargando WAV validado con soundfile...")
                    audio_array, sample_rate = sf.read(audio_path)
                    if audio_array.ndim > 1:
                        audio_array = audio_array.mean(axis=1)
                    print("✅ Cargado con soundfile")
                except Exception as e:
                    print(f"❌ Fallo soundfile con WAV validado: {e}")
        
        # Método 2: Intentar con pydub directamente (simplificado)
        if audio_array is None:
            try:
                print("🔄 Método 2: Cargando con pydub...")
                seg = AudioSegment.from_file(audio_path).set_channels(1).set_frame_rate(16000)
                samples = np.array(seg.get_array_of_samples()).astype(np.float32) / 32768.0
                if samples.size > 0:
                    audio_array = samples
                    sample_rate = 16000
                    print("✅ Cargado con pydub")
            except Exception as e:
                print(f"❌ Fallo pydub: {e}")
        
        # Método 3: Conversión a WAV estándar
        if audio_array is None:
            try:
                print("🔄 Método 3: Convirtiendo a WAV estándar...")
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                    temp_path = temp_file.name
                if convert_to_standard_wav(audio_path, temp_path):
                    audio_array, sample_rate = sf.read(temp_path)
                    if audio_array.ndim > 1:
                        audio_array = audio_array.mean(axis=1)
                    os.unlink(temp_path)
                    print("✅ Cargado después de conversión estándar")
            except Exception as e:
                print(f"❌ Fallo conversión estándar: {e}")
                if 'temp_path' in locals() and os.path.exists(temp_path):
                    os.unlink(temp_path)
        
        # Método 4: Lectura raw de datos (el que te funcionaba)
        if audio_array is None:
            audio_array, sample_rate = read_audio_raw(audio_path)
        
        # Método 5: Librosa como último recurso
        if audio_array is None:
            try:
                print("🔄 Método 5: Librosa como último recurso...")
                audio_array, sample_rate = librosa.load(audio_path, sr=16000, mono=True)
                print("✅ Cargado con librosa")
            except Exception as e:
                print(f"❌ Fallo librosa: {e}")
        # --- FIN DE LA LÓGICA DE CARGA ---

        if audio_array is None or len(audio_array) == 0:
            print("❌ No se pudo cargar el archivo de audio con ningún método")
            return None
        
        # Verificar y limpiar el audio
        if np.any(np.isnan(audio_array)) or np.any(np.isinf(audio_array)):
            print("⚠️ Limpiando valores inválidos en el audio...")
            audio_array = np.nan_to_num(audio_array)
        
        max_val = np.max(np.abs(audio_array))
        if max_val > 1.0:
            audio_array = audio_array / max_val
        elif max_val == 0.0:
            print("❌ El audio no contiene señal (silencio completo)")
            return "El audio parece estar en silencio."
        
        duration = len(audio_array) / sample_rate
        print(f"✅ Audio procesado exitosamente (duración: {duration:.2f}s)")
        if duration < 0.1:
            print("❌ El audio es demasiado corto para procesar")
            return "El audio es demasiado corto."
        
        # Procesar con Whisper
        print("🔄 Procesando con Whisper...")
        input_features = whisper_processor(
            audio_array, 
            sampling_rate=sample_rate, 
            return_tensors="pt"
        ).input_features.to(whisper_model.device)

        # SOLUCIÓN: Forzar el idioma para evitar transcripciones incorrectas
        print(f"🗣️ Forzando idioma de transcripción a: '{language}'")
        forced_decoder_ids = whisper_processor.get_decoder_prompt_ids(language=language, task="transcribe")

        with torch.no_grad():
            print("🔄 Generando transcripción...")
            predicted_ids = whisper_model.generate(
                input_features, 
                forced_decoder_ids=forced_decoder_ids, # <-- CAMBIO CLAVE
                max_length=448
            )
            transcripcion = whisper_processor.batch_decode(
                predicted_ids, 
                skip_special_tokens=True
            )[0]
        
        transcripcion_limpia = transcripcion.strip()
        print(f"✅ Transcripción generada: '{transcripcion_limpia[:100]}...'")
        
        if not transcripcion_limpia:
            print("⚠️ Transcripción vacía o inválida")
            return "No se pudo generar transcripción del audio."
        
        return transcripcion_limpia

    except Exception as e:
        print(f"❌ Error crítico al transcribir el audio: {e}")
        print(f"📋 Traceback completo: {traceback.format_exc()}")
        return None

def generar_diagnostico_clinico(sintomas, historial):
    """Genera un diagnóstico basado en síntomas e historial médico."""
    try:
        load_clinical_model()
        
        if not sintomas or not sintomas.strip():
            sintomas = "Síntomas no especificados"
        if not historial or not historial.strip():
            historial = "Historial médico no disponible"
        
        input_text = f"{sintomas.strip()} [SEP] {historial.strip()}"
        
        print(f"🔄 Tokenizando texto para diagnóstico clínico: '{input_text[:100]}...'")
        inputs = clinical_tokenizer(
            input_text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        ).to(clinical_model.device)
        
        print("🔄 Generando diagnóstico...")
        with torch.no_grad():
            outputs = clinical_model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=1)
            confidence, predicted_class = torch.max(probabilities, dim=1)
            predicted_class = predicted_class.item()
            confidence = confidence.item()
        
        diagnosticos = {
            0: "Common cold", 1: "Pneumonia", 2: "Bronchitis",
            3: "Asthma exacerbation", 4: "Chronic obstructive pulmonary disease (COPD)"
        }
        diagnostico_en = diagnosticos.get(predicted_class, "Unknown condition")
        print(f"✅ Diagnóstico generado: {diagnostico_en} (confianza: {confidence:.2f})")
        
        traducciones = {
            "Common cold": "Resfriado común", "Pneumonia": "Neumonía",
            "Bronchitis": "Bronquitis", "Asthma exacerbation": "Exacerbación de asma",
            "Chronic obstructive pulmonary disease (COPD)": "Enfermedad pulmonar obstructiva crónica (EPOC)",
            "Unknown condition": "Condición desconocida"
        }
        diagnostico_es = traducciones.get(diagnostico_en, "Condición desconocida")
        
        if confidence < 0.5:
            diagnostico_es += f" (Confianza baja: {confidence:.1%})"
            diagnostico_en += f" (Low confidence: {confidence:.1%})"
        
        return diagnostico_en, diagnostico_es

    except Exception as e:
        print(f"❌ Error al generar diagnóstico: {e}")
        print(f"📋 Traceback: {traceback.format_exc()}")
        return "Error generating diagnosis", "Error generando diagnóstico"

def analizar_audio_view(request, audio_id):
    """Vista para mostrar la página de análisis de un audio específico."""
    try:
        audio = get_object_or_404(AudioMedico, id=audio_id)
        diagnostico = Diagnostico.objects.filter(audio=audio).first()
        context = {'audio': audio, 'diagnostico': diagnostico}
        return render(request, 'analizar_audio.html', context)
    except Exception as e:
        print(f"❌ Error en vista de análisis: {e}")
        return render(request, 'error.html', {'error': 'No se pudo cargar el audio'})

@csrf_exempt
@require_http_methods(["POST"])
def procesar_audio_ajax_view(request):
    """Vista AJAX para procesar un audio y generar diagnóstico."""
    try:
        data = json.loads(request.body)
        audio_id = data.get('audio_id')
        language = data.get('language', 'es') # Permite seleccionar idioma desde el frontend, por defecto 'es'

        if not audio_id:
            return JsonResponse({'success': False, 'error': 'ID de audio no proporcionado'}, status=400)

        load_custom_whisper_model()
        audio = get_object_or_404(AudioMedico, id=audio_id)
        audio_path = audio.archivo_audio.path
        print(f"🎤 Procesando audio ID {audio_id} desde: {audio_path}")

        transcripcion = procesar_audio_con_whisper(audio_path, language=language)
        if transcripcion is None:
            return JsonResponse({'success': False, 'error': 'No se pudo transcribir el audio. Verifique el formato y calidad del archivo.'}, status=500)

        sintomas = transcripcion
        historial = "Historial no especificado"
        
        diagnostico_en, diagnostico_es = generar_diagnostico_clinico(sintomas, historial)
        
        return JsonResponse({
            'success': True,
            'transcripcion': transcripcion,
            'diagnostico_en': diagnostico_en,
            'diagnostico_es': diagnostico_es
        })

    except FileNotFoundError as e:
        error_msg = f"Error de configuración: {str(e)}"
        print(f"❌ {error_msg}")
        return JsonResponse({'success': False, 'error': error_msg}, status=500)
    except Exception as e:
        error_msg = f"Error inesperado: {str(e)}"
        print(f"❌ {error_msg}")
        print(f"📋 Traceback: {traceback.format_exc()}")
        return JsonResponse({'success': False, 'error': error_msg}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def guardar_resultados_ajax_view(request):
    """Guarda la transcripción y diagnóstico en la base de datos."""
    try:
        data = json.loads(request.body)
        audio_id = data.get('audio_id')
        transcripcion = data.get('transcripcion')
        diagnostico_en = data.get('diagnostico_en')
        diagnostico_es = data.get('diagnostico_es')

        if not all([audio_id, transcripcion, diagnostico_en, diagnostico_es]):
            return JsonResponse({'success': False, 'error': 'Datos incompletos'}, status=400)

        audio = get_object_or_404(AudioMedico, id=audio_id)

        contenido_diagnostico = f"""TRANSCRIPCIÓN:
{transcripcion}

DIAGNÓSTICO:
• Español: {diagnostico_es}
• English: {diagnostico_en}

FECHA DE PROCESAMIENTO: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

        diagnostico, created = Diagnostico.objects.update_or_create(
            audio=audio,
            defaults={
                'transcripcion': contenido_diagnostico,
                'estado': 'completado'
            }
        )
        
        action = "creado" if created else "actualizado"
        print(f"💾 Diagnóstico para audio ID {audio_id} {action} correctamente.")

        return JsonResponse({
            'success': True, 
            'message': f'Diagnóstico {action} con éxito.',
            'diagnostico_id': diagnostico.id
        })
        
    except Exception as e:
        error_msg = f"Error al guardar: {str(e)}"
        print(f"❌ {error_msg}")
        print(f"📋 Traceback: {traceback.format_exc()}")
        return JsonResponse({'success': False, 'error': error_msg}, status=500)
