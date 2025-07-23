# audio_app/urls.py

from django.urls import path
from . import views

app_name = 'audio_app'  # 👈 esto es lo que faltaba

urlpatterns = [
    path('', views.subir_audio_view, name='subir_audio'),
    path('subir_audio/', views.subir_audio_view, name='subir_audio_alt'),
    path('subir_grabacion/', views.subir_grabacion_view, name='subir_grabacion'),
    path('lista/', views.lista_audios_view, name='lista_audios'),
    path('detalle/<int:audio_id>/', views.detalle_audio_view, name='detalle_audio'),
    path('eliminar/<int:audio_id>/', views.eliminar_audio_view, name='eliminar_audio'),
]
