# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os

def audio_upload_path(instance, filename):
    """Genera la ruta donde se guardará el archivo de audio"""
    # Organiza los archivos por fecha: audio/2025/07/20/filename.mp3
    return f'audio/{timezone.now().strftime("%Y/%m/%d")}/{filename}'

class AudioMedico(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('completado', 'Completado'),
        ('error', 'Error'),
    ]
    
    FORMATO_CHOICES = [
        ('mp3', 'MP3'),
        ('wav', 'WAV'),
        ('ogg', 'OGG'),
        ('m4a', 'M4A'),
        ('aac', 'AAC'),
    ]
    
    # Información básica
    titulo = models.CharField(
        max_length=200, 
        verbose_name="Identificación del Caso",
        help_text="Ej: Paciente 001 - Consulta inicial - Dr. González"
    )
    
    # Archivo de audio
    archivo_audio = models.FileField(
        upload_to=audio_upload_path,
        verbose_name="Archivo de Audio",
        help_text="Formatos soportados: MP3, WAV, OGG, M4A, AAC"
    )
    
    # Metadatos del archivo
    nombre_original = models.CharField(max_length=255, verbose_name="Nombre Original")
    formato_audio = models.CharField(max_length=10, choices=FORMATO_CHOICES, verbose_name="Formato")
    duracion_segundos = models.IntegerField(null=True, blank=True, verbose_name="Duración (segundos)")
    tamaño_archivo = models.BigIntegerField(verbose_name="Tamaño (bytes)")
    
    # Información de procesamiento
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='pendiente',
        verbose_name="Estado del Procesamiento"
    )
    
    # Resultados del análisis (opcional)
    transcripcion = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Transcripción del Audio"
    )
    analisis_ia = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Análisis de IA"
    )
    
    # Metadatos de sistema
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        verbose_name="Usuario"
    )
    fecha_subida = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Subida")
    fecha_procesamiento = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name="Fecha de Procesamiento"
    )
    
    # Campos adicionales médicos
    doctor = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name="Doctor Responsable"
    )
    paciente_id = models.CharField(
        max_length=50, 
        blank=True, 
        verbose_name="ID del Paciente"
    )
    tipo_consulta = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name="Tipo de Consulta"
    )
    
    class Meta:
        verbose_name = "Audio Médico"
        verbose_name_plural = "Audios Médicos"
        ordering = ['-fecha_subida']
    
    def __str__(self):
        return f"{self.titulo} - {self.get_estado_display()}"
    
    def get_duracion_formateada(self):
        """Devuelve la duración en formato MM:SS"""
        if self.duracion_segundos:
            minutos = self.duracion_segundos // 60
            segundos = self.duracion_segundos % 60
            return f"{minutos:02d}:{segundos:02d}"
        return "00:00"
    
    def get_tamaño_formateado(self):
        """Devuelve el tamaño del archivo en formato legible"""
        if self.tamaño_archivo:
            if self.tamaño_archivo < 1024:
                return f"{self.tamaño_archivo} B"
            elif self.tamaño_archivo < 1024 * 1024:
                return f"{self.tamaño_archivo / 1024:.1f} KB"
            else:
                return f"{self.tamaño_archivo / (1024 * 1024):.1f} MB"
        return "0 B"
    
    def delete(self, *args, **kwargs):
        """Sobrescribe delete para eliminar el archivo físico también"""
        if self.archivo_audio:
            if os.path.isfile(self.archivo_audio.path):
                os.remove(self.archivo_audio.path)
        super().delete(*args, **kwargs)