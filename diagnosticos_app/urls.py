# diagnosticos_app/urls.py
from django.urls import path
from . import views

app_name = 'diagnosticos_app'

urlpatterns = [
    # URL que tu código está buscando
    path('analizar/<int:audio_id>/', views.analizar_audio_view, name='analizar_audio'),
    
    # URLs para tus vistas AJAX existentes
    path('procesar-audio/', views.procesar_audio_ajax_view, name='procesar_audio_ajax'),
    path('guardar-resultados/', views.guardar_resultados_ajax_view, name='guardar_resultados_ajax'),
]