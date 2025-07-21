# admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import AudioMedico
import os

@admin.register(AudioMedico)
class AudioMedicoAdmin(admin.ModelAdmin):
    list_display = [
        'titulo',
        'get_estado_badge',
        'doctor',
        'get_duracion_display',
        'get_tamaño_display',
        'formato_audio',
        'fecha_subida',
        'get_audio_player',
        'get_acciones'
    ]
    
    list_filter = [
        'estado',
        'formato_audio',
        'fecha_subida',
        'doctor',
    ]
    
    search_fields = [
        'titulo',
        'doctor',
        'paciente_id',
        'tipo_consulta',
        'nombre_original'
    ]
    
    readonly_fields = [
        'nombre_original',
        'formato_audio',
        'duracion_segundos',
        'tamaño_archivo',
        'fecha_subida',
        'fecha_procesamiento',
        'get_audio_info',
        'get_audio_player_admin'
    ]
    
    fieldsets = (
        ('Información del Caso', {
            'fields': (
                'titulo',
                'doctor',
                'paciente_id',
                'tipo_consulta',
                'usuario'
            )
        }),
        ('Archivo de Audio', {
            'fields': (
                'archivo_audio',
                'get_audio_player_admin',
                'get_audio_info'
            )
        }),
        ('Metadatos del Archivo', {
            'fields': (
                'nombre_original',
                'formato_audio',
                'duracion_segundos',
                'tamaño_archivo'
            ),
            'classes': ('collapse',)
        }),
        ('Procesamiento', {
            'fields': (
                'estado',
                'fecha_subida',
                'fecha_procesamiento'
            )
        }),
        ('Resultados del Análisis', {
            'fields': (
                'transcripcion',
                'analisis_ia'
            ),
            'classes': ('collapse',)
        })
    )
    
    actions = [
        'marcar_como_completado',
        'marcar_como_pendiente',
        'procesar_audio',
        'eliminar_archivos_seleccionados'
    ]
    
    def get_estado_badge(self, obj):
        """Muestra el estado como un badge colorido"""
        colors = {
            'pendiente': '#ffc107',    # Amarillo
            'procesando': '#007bff',   # Azul
            'completado': '#28a745',   # Verde
            'error': '#dc3545'         # Rojo
        }
        color = colors.get(obj.estado, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_estado_display()
        )
    get_estado_badge.short_description = 'Estado'
    
    def get_duracion_display(self, obj):
        """Muestra la duración formateada"""
        return obj.get_duracion_formateada()
    get_duracion_display.short_description = 'Duración'
    
    def get_tamaño_display(self, obj):
        """Muestra el tamaño formateado"""
        return obj.get_tamaño_formateado()
    get_tamaño_display.short_description = 'Tamaño'
    
    def get_audio_player(self, obj):
        """Reproductor de audio en la lista"""
        if obj.archivo_audio:
            return format_html(
                '<audio controls style="width: 200px; height: 30px;"><source src="{}" type="audio/mpeg">Tu navegador no soporta audio.</audio>',
                obj.archivo_audio.url
            )
        return "No hay audio"
    get_audio_player.short_description = 'Reproductor'
    
    def get_audio_player_admin(self, obj):
        """Reproductor de audio mejorado para el formulario de administración"""
        if obj.archivo_audio:
            return format_html(
                '''
                <div style="margin: 10px 0;">
                    <audio controls style="width: 100%; max-width: 500px;">
                        <source src="{}" type="audio/mpeg">
                        Tu navegador no soporta la reproducción de audio.
                    </audio>
                    <div style="margin-top: 10px; font-size: 12px; color: #666;">
                        <strong>Archivo:</strong> {} <br>
                        <strong>URL:</strong> <a href="{}" target="_blank">Descargar</a>
                    </div>
                </div>
                ''',
                obj.archivo_audio.url,
                obj.nombre_original or obj.archivo_audio.name,
                obj.archivo_audio.url
            )
        return "No se ha subido ningún archivo de audio"
    get_audio_player_admin.short_description = 'Reproductor de Audio'
    
    def get_audio_info(self, obj):
        """Información detallada del archivo de audio"""
        if obj.archivo_audio:
            info = f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <h4 style="margin: 0 0 10px 0; color: #495057;">📊 Información del Audio</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 13px;">
                    <div><strong>Nombre original:</strong> {obj.nombre_original or 'N/A'}</div>
                    <div><strong>Formato:</strong> {obj.formato_audio.upper() if obj.formato_audio else 'N/A'}</div>
                    <div><strong>Duración:</strong> {obj.get_duracion_formateada()}</div>
                    <div><strong>Tamaño:</strong> {obj.get_tamaño_formateado()}</div>
                    <div><strong>Fecha subida:</strong> {obj.fecha_subida.strftime('%d/%m/%Y %H:%M')}</div>
                    <div><strong>Estado:</strong> {obj.get_estado_display()}</div>
                </div>
            </div>
            """
            return mark_safe(info)
        return "No hay información de audio disponible"
    get_audio_info.short_description = 'Información del Archivo'
    
    def get_acciones(self, obj):
        """Botones de acción rápida"""
        acciones = []
        
        if obj.archivo_audio:
            acciones.append(f'<a href="{obj.archivo_audio.url}" target="_blank" title="Descargar" style="color: #007bff; text-decoration: none; margin-right: 10px;">⬇️</a>')
        
        if obj.estado == 'pendiente':
            acciones.append('<span title="Procesar" style="color: #ffc107; margin-right: 10px;">⚡</span>')
        elif obj.estado == 'completado':
            acciones.append('<span title="Completado" style="color: #28a745; margin-right: 10px;">✅</span>')
        elif obj.estado == 'error':
            acciones.append('<span title="Error" style="color: #dc3545; margin-right: 10px;">❌</span>')
            
        return format_html(''.join(acciones))
    get_acciones.short_description = 'Acciones'
    
    # Acciones del admin
    def marcar_como_completado(self, request, queryset):
        """Marca los audios seleccionados como completados"""
        updated = queryset.update(estado='completado')
        self.message_user(request, f'{updated} audios marcados como completados.')
    marcar_como_completado.short_description = "Marcar como completado"
    
    def marcar_como_pendiente(self, request, queryset):
        """Marca los audios seleccionados como pendientes"""
        updated = queryset.update(estado='pendiente')
        self.message_user(request, f'{updated} audios marcados como pendientes.')
    marcar_como_pendiente.short_description = "Marcar como pendiente"
    
    def procesar_audio(self, request, queryset):
        """Procesa los audios seleccionados (aquí puedes agregar tu lógica de IA)"""
        for audio in queryset:
            audio.estado = 'procesando'
            audio.save()
            # Aquí puedes agregar tu lógica de procesamiento de IA
        self.message_user(request, f'{queryset.count()} audios enviados a procesamiento.')
    procesar_audio.short_description = "Procesar con IA"
    
    def eliminar_archivos_seleccionados(self, request, queryset):
        """Elimina los archivos seleccionados y sus archivos físicos"""
        count = 0
        for audio in queryset:
            if audio.archivo_audio and os.path.isfile(audio.archivo_audio.path):
                os.remove(audio.archivo_audio.path)
            audio.delete()
            count += 1
        self.message_user(request, f'{count} archivos eliminados correctamente.')
    eliminar_archivos_seleccionados.short_description = "Eliminar archivos seleccionados"
    
    def save_model(self, request, obj, form, change):
        """Guarda información adicional del archivo al crear/actualizar"""
        if not change:  # Si es un nuevo objeto
            if not obj.usuario:
                obj.usuario = request.user
                
        # Extrae metadatos del archivo si existe
        if obj.archivo_audio:
            if not obj.nombre_original:
                obj.nombre_original = obj.archivo_audio.name
            
            if not obj.formato_audio:
                extension = os.path.splitext(obj.archivo_audio.name)[1].lower().replace('.', '')
                if extension in ['mp3', 'wav', 'ogg', 'm4a', 'aac']:
                    obj.formato_audio = extension
                    
            if not obj.tamaño_archivo:
                obj.tamaño_archivo = obj.archivo_audio.size
                
        super().save_model(request, obj, form, change)
    
    class Media:
        css = {
            'all': ('custom_audio_admin.css',)
        }
        js = ('audio_admin.js',)