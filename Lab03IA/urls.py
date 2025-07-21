# Lab03IA/urls.py (principal del proyecto)
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from audio_app.views import subir_audio_view

urlpatterns = [
    path('admin/', admin.site.urls),  # ← ADMIN PRIMERO
    path('', subir_audio_view, name='home'),
    path('audio/', include('audio_app.urls')),
]

# Configuración de archivos estáticos y media - AL FINAL
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)