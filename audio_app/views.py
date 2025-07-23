from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.conf import settings
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.core.files.base import ContentFile
from django.urls import reverse
from django.utils import timezone
from .models import AudioMedico
from .forms import AudioMedicoForm
import json
import os
import mimetypes
import soundfile as sf
import io
import numpy as np

def subir_audio_view(request):
    """Vista principal para subir audio"""
    if request.method == 'GET':
        form = AudioMedicoForm()
        return render(request, 'audio_app/subir_audio.html', {'form': form})
    
    elif request.method == 'POST':
        return procesar_audio_subida(request)

def procesar_audio_subida(request):
    """Procesa la subida de audio tanto de archivos como de grabaciones"""
    try:
        titulo = request.POST.get('titulo', '')
        if not titulo:
            return JsonResponse({
                'success': False, 
                'message': 'El título es requerido'
            }, status=400)
        
        archivo_audio = request.FILES.get('archivo_audio')
        if not archivo_audio:
            return JsonResponse({
                'success': False, 
                'message': 'No se encontró archivo de audio'
            }, status=400)
        
        # Validar y convertir el audio a WAV si es necesario
        try:
            # Leer el audio en memoria
            audio_data = archivo_audio.read()
            audio_io = io.BytesIO(audio_data)
            
            # Intentar leer con soundfile para validar
            try:
                data, samplerate = sf.read(audio_io)
                # Convertir a mono si es estéreo
                if len(data.shape) > 1:
                    data = np.mean(data, axis=1)
                
                # Crear nuevo archivo WAV en memoria
                output_io = io.BytesIO()
                sf.write(output_io, data, samplerate, format='WAV')
                output_io.seek(0)
                
                # Crear nuevo archivo para Django
                nuevo_nombre = f"{os.path.splitext(archivo_audio.name)[0]}.wav"
                archivo_audio = ContentFile(output_io.read(), name=nuevo_nombre)
                
            except Exception as e:
                print(f"Error al procesar audio: {e}")
                # Si falla, intentamos usar el archivo original
                archivo_audio.seek(0)
        
        except Exception as e:
            print(f"Error al leer archivo: {e}")
            return JsonResponse({
                'success': False,
                'message': 'Error al procesar el archivo de audio'
            }, status=400)
        
        # Validar tamaño
        max_size = 100 * 1024 * 1024  # 100MB
        if archivo_audio.size > max_size:
            return JsonResponse({
                'success': False, 
                'message': 'El archivo es demasiado grande. Máximo permitido: 100MB'
            }, status=400)
        
        # Crear y guardar el objeto AudioMedico
        audio_obj = AudioMedico()
        audio_obj.titulo = titulo
        audio_obj.archivo_audio = archivo_audio
        audio_obj.nombre_original = archivo_audio.name
        audio_obj.tamaño_archivo = archivo_audio.size
        audio_obj.formato_audio = 'wav'
        
        if request.user.is_authenticated:
            audio_obj.usuario = request.user
        
        # Procesar información del título
        if ' - ' in titulo:
            partes = titulo.split(' - ')
            if len(partes) >= 3:
                audio_obj.paciente_id = partes[0].strip()
                audio_obj.tipo_consulta = partes[1].strip()
                audio_obj.doctor = partes[2].strip()
        
        audio_obj.save()
        
        request.session['ultimo_audio_id'] = audio_obj.id
        
        return JsonResponse({
            'success': True,
            'message': 'Audio subido correctamente',
            'audio_id': audio_obj.id,
            'titulo': audio_obj.titulo,
            'tamaño': audio_obj.get_tamaño_formateado(),
            'formato': audio_obj.formato_audio,
            'url_admin': f'/admin/audio_app/audiomedico/{audio_obj.id}/change/',
            'url_analisis': reverse('diagnosticos_app:analizar_audio', kwargs={'audio_id': audio_obj.id})
        })
        
    except Exception as e:
        print(f"Error general: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error al procesar el audio: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def subir_grabacion_view(request):
    """Vista específica para subir grabaciones de audio desde el frontend"""
    try:
        if 'audio_blob' not in request.FILES:
            return JsonResponse({
                'success': False, 
                'message': 'No se encontró el archivo de audio grabado'
            }, status=400)
        
        audio_blob = request.FILES['audio_blob']
        titulo = request.POST.get('titulo', f'Grabación {timezone.now().strftime("%Y%m%d_%H%M%S")}')
        
        # Procesar el audio blob
        try:
            audio_data = audio_blob.read()
            audio_io = io.BytesIO(audio_data)
            
            # Intentar leer y convertir a WAV
            data, samplerate = sf.read(audio_io)
            if len(data.shape) > 1:
                data = np.mean(data, axis=1)
            
            output_io = io.BytesIO()
            sf.write(output_io, data, samplerate, format='WAV')
            output_io.seek(0)
            
            nuevo_nombre = f"grabacion_medica_{timezone.now().strftime('%Y%m%d_%H%M%S')}.wav"
            audio_blob = ContentFile(output_io.read(), name=nuevo_nombre)
            
        except Exception as e:
            print(f"Error al procesar grabación: {e}")
            audio_blob.seek(0)
        
        audio_obj = AudioMedico()
        audio_obj.titulo = titulo
        audio_obj.archivo_audio = audio_blob
        audio_obj.nombre_original = audio_blob.name
        audio_obj.tamaño_archivo = audio_blob.size
        audio_obj.formato_audio = 'wav'
        
        if request.user.is_authenticated:
            audio_obj.usuario = request.user
        
        audio_obj.save()
        
        request.session['ultimo_audio_id'] = audio_obj.id
        
        return JsonResponse({
            'success': True,
            'message': 'Grabación guardada correctamente',
            'audio_id': audio_obj.id,
            'titulo': audio_obj.titulo,
            'url_analisis': reverse('diagnosticos_app:analizar_audio', kwargs={'audio_id': audio_obj.id})
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al guardar la grabación: {str(e)}'
        }, status=500)

def lista_audios_view(request):
    """Vista para mostrar la lista de audios subidos"""
    audios = AudioMedico.objects.all().order_by('-fecha_subida')
    
    if request.user.is_authenticated and not request.user.is_staff:
        audios = audios.filter(usuario=request.user)
    
    context = {
        'audios': audios
    }
    return render(request, 'audio_app/lista_audios.html', context)

def detalle_audio_view(request, audio_id):
    """Vista para mostrar detalles de un audio específico"""
    try:
        audio = AudioMedico.objects.get(id=audio_id)
        
        if not request.user.is_staff and audio.usuario != request.user:
            messages.error(request, 'No tienes permisos para ver este audio.')
            return redirect('lista_audios')
        
        context = {
            'audio': audio
        }
        return render(request, 'audio_app/detalle_audio.html', context)
        
    except AudioMedico.DoesNotExist:
        messages.error(request, 'El audio solicitado no existe.')
        return redirect('lista_audios')

def eliminar_audio_view(request, audio_id):
    """Vista para eliminar un audio"""
    try:
        audio = AudioMedico.objects.get(id=audio_id)
        
        if not request.user.is_staff and audio.usuario != request.user:
            messages.error(request, 'No tienes permisos para eliminar este audio.')
            return redirect('lista_audios')
        
        if request.method == 'POST':
            titulo = audio.titulo
            audio.delete()
            messages.success(request, f'Audio "{titulo}" eliminado correctamente.')
            return redirect('lista_audios')
        
        context = {
            'audio': audio
        }
        return render(request, 'audio_app/confirmar_eliminar.html', context)
        
    except AudioMedico.DoesNotExist:
        messages.error(request, 'El audio solicitado no existe.')
        return redirect('lista_audios')