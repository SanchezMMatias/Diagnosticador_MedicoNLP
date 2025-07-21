# forms.py
from django import forms
from .models import AudioMedico

class AudioMedicoForm(forms.ModelForm):
    class Meta:
        model = AudioMedico
        fields = ['titulo', 'archivo_audio', 'doctor', 'paciente_id', 'tipo_consulta']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Paciente 001 - Consulta inicial - Dr. González',
                'id': 'titulo'
            }),
            'archivo_audio': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'audio/*',
                'id': 'audioFile'
            }),
            'doctor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del doctor'
            }),
            'paciente_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ID o código del paciente'
            }),
            'tipo_consulta': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tipo de consulta médica'
            })
        }
        
    def clean_archivo_audio(self):
        archivo = self.cleaned_data.get('archivo_audio')
        if archivo:
            # Validar tamaño (100MB máximo)
            if archivo.size > 100 * 1024 * 1024:
                raise forms.ValidationError('El archivo es demasiado grande. Máximo 100MB.')
            
            # Validar tipo de archivo
            tipos_permitidos = ['.mp3', '.wav', '.ogg', '.m4a', '.aac']
            nombre = archivo.name.lower()
            if not any(nombre.endswith(ext) for ext in tipos_permitidos):
                raise forms.ValidationError('Formato no soportado. Use MP3, WAV, OGG, M4A o AAC.')
        
        return archivo