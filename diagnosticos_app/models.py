from django.db import models
from audio_app.models import AudioMedico

class Diagnostico(models.Model):
    """
    Modelo para almacenar diagnósticos basados en transcripciones de audio.
    Se relaciona uno a uno con AudioMedico.
    """
    
    # Definición de las opciones de estado del diagnóstico
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),      # El diagnóstico está pendiente de procesar
        ('procesando', 'Procesando'),    # El audio está siendo procesado
        ('completado', 'Completado'),    # El procesamiento se completó exitosamente
        ('error', 'Error'),              # Ocurrió un error durante el procesamiento
    ]
    
    # Relación uno a uno con el modelo AudioMedico
    audio = models.OneToOneField(
        AudioMedico,
        on_delete=models.CASCADE,        # Si se elimina el audio, se elimina el diagnóstico
        related_name='diagnostico',      # Permite acceder desde audio_medico.diagnostico
        verbose_name="Audio médico"
    )
    
    # Campo para almacenar la transcripción del audio
    transcripcion = models.TextField(
        blank=True,                      # Permite que el campo esté vacío en el formulario
        null=True,                       # Permite valores NULL en la base de datos
        help_text="Transcripción del audio usando Whisper",
        verbose_name="Transcripción"
    )
    
    # Estado actual del diagnóstico
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',             # Estado por defecto al crear un nuevo diagnóstico
        verbose_name="Estado"
    )
    
    # Campos de auditoría para seguimiento temporal
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,              # Se establece automáticamente al crear
        verbose_name="Fecha de creación"
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,                  # Se actualiza automáticamente en cada modificación
        verbose_name="Última actualización"
    )

    def __str__(self):
        """
        Representación en string del modelo
        Retorna: String con el formato "Diagnóstico #ID - Título del Audio"
        """
        return f"Diagnóstico #{self.id} - {self.audio.titulo}"

    class Meta:
        """
        Metaclase para definir características adicionales del modelo
        """
        verbose_name = "Diagnóstico"
        verbose_name_plural = "Diagnósticos"
        ordering = ['-fecha_creacion']   # Ordena por fecha de creación descendente
        
        # Índices para mejorar el rendimiento de las consultas
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['fecha_creacion']),
        ]