# Lab03IA/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('audio/', include('audio_app.urls')),
    path('diagnosticos/', include('diagnosticos_app.urls')),
    path('', include('audio_app.urls')),  # Página principal desde audio_app
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
