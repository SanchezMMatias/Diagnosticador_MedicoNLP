# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.conf import settings
from .models import AudioMedico
from .forms import AudioMedicoForm
import json
import os
import mimetypes
from django.utils import timezone

def subir_audio_view(request):
    """Vista principal para subir audio"""
    if request.method == 'GET':
        # Mostrar el formulario
        form = AudioMedicoForm()
        return render(request, 'audio_app/subir_audio.html', {'form': form})  # ← Cambia 'audio' por 'audio_app'
    
    elif request.method == 'POST':
        return procesar_audio_subida(request)

def procesar_audio_subida(request):
    """Procesa la subida de audio tanto de archivos como de grabaciones"""
    try:
        # Obtener datos del formulario
        titulo = request.POST.get('titulo', '')
        if not titulo:
            return JsonResponse({
                'success': False, 
                'message': 'El título es requerido'
            }, status=400)
        
        # Verificar si hay archivo de audio
        archivo_audio = request.FILES.get('archivo_audio')
        if not archivo_audio:
            return JsonResponse({
                'success': False, 
                'message': 'No se encontró archivo de audio'
            }, status=400)
        
        # Validar tipo de archivo
        tipos_permitidos = ['audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/mp4', 'audio/aac']
        tipo_mime = mimetypes.guess_type(archivo_audio.name)[0]
        
        if tipo_mime not in tipos_permitidos:
            return JsonResponse({
                'success': False, 
                'message': f'Tipo de archivo no soportado: {tipo_mime}. Usa MP3, WAV, OGG, M4A o AAC.'
            }, status=400)
        
        # Validar tamaño (máximo 100MB)
        max_size = 100 * 1024 * 1024  # 100MB
        if archivo_audio.size > max_size:
            return JsonResponse({
                'success': False, 
                'message': f'El archivo es demasiado grande. Máximo permitido: 100MB'
            }, status=400)
        
        # Crear objeto AudioMedico
        audio_obj = AudioMedico()
        audio_obj.titulo = titulo
        audio_obj.archivo_audio = archivo_audio
        audio_obj.nombre_original = archivo_audio.name
        audio_obj.tamaño_archivo = archivo_audio.size
        
        # Extraer formato del archivo
        extension = os.path.splitext(archivo_audio.name)[1].lower().replace('.', '')
        if extension in ['mp3', 'wav', 'ogg', 'm4a', 'aac']:
            audio_obj.formato_audio = extension
        
        # Asignar usuario si está autenticado
        if request.user.is_authenticated:
            audio_obj.usuario = request.user
        
        # Extraer información adicional del título si viene estructurada
        if ' - ' in titulo:
            partes = titulo.split(' - ')
            if len(partes) >= 3:
                audio_obj.paciente_id = partes[0].strip()
                audio_obj.tipo_consulta = partes[1].strip()
                audio_obj.doctor = partes[2].strip()
        
        # Guardar el objeto
        audio_obj.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Audio subido correctamente',
            'audio_id': audio_obj.id,
            'titulo': audio_obj.titulo,
            'tamaño': audio_obj.get_tamaño_formateado(),
            'formato': audio_obj.formato_audio,
            'url_admin': f'/admin/audio_app/audiomedico/{audio_obj.id}/change/'  # Cambia 'tu_app' por el nombre real
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al procesar el audio: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def subir_grabacion_view(request):
    """Vista específica para subir grabaciones de audio desde el frontend"""
    try:
        # Obtener el archivo de la grabación
        if 'audio_blob' not in request.FILES:
            return JsonResponse({
                'success': False, 
                'message': 'No se encontró el archivo de audio grabado'
            }, status=400)
        
        audio_blob = request.FILES['audio_blob']
        titulo = request.POST.get('titulo', f'Grabación {timezone.now().strftime("%Y%m%d_%H%M%S")}')
        
        # Crear objeto AudioMedico para la grabación
        audio_obj = AudioMedico()
        audio_obj.titulo = titulo
        audio_obj.archivo_audio = audio_blob
        audio_obj.nombre_original = f"grabacion_{timezone.now().strftime('%Y%m%d_%H%M%S')}.wav"
        audio_obj.tamaño_archivo = audio_blob.size
        audio_obj.formato_audio = 'wav'
        
        if request.user.is_authenticated:
            audio_obj.usuario = request.user
        
        audio_obj.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Grabación guardada correctamente',
            'audio_id': audio_obj.id,
            'titulo': audio_obj.titulo
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
        return render(request, 'audio_app/detalle_audio.html', context)  # ← audio_app/
        
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
        return render(request, 'audio_app/confirmar_eliminar.html', context)  # ← audio_app/
        
    except AudioMedico.DoesNotExist:
        messages.error(request, 'El audio solicitado no existe.')
        return redirect('lista_audios')