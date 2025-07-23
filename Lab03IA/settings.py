from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'tu-secret-key-aqui'  

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'jazzmin',  # ← IMPORTANTE: Debe ir ANTES de django.contrib.admin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'audio_app',
    'diagnosticos_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Lab03IA.urls'  # Cambia por el nombre de tu proyecto

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Aquí usamos BASE_DIR
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Lab03IA.wsgi.application'  # Cambia por el nombre de tu proyecto

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # Aquí también usamos BASE_DIR
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ===============================================
# CONFIGURACIÓN DE ARCHIVOS ESTÁTICOS Y MEDIA
# ===============================================

# Archivos estáticos (CSS, JS, imágenes del proyecto)
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'audio_app', 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Archivos media (subidos por usuarios) - ¡ESTO FALTABA!
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Crear directorios si no existen
os.makedirs(MEDIA_ROOT, exist_ok=True)
os.makedirs(STATIC_ROOT, exist_ok=True)

# ===============================================
# CONFIGURACIÓN ESPECÍFICA PARA ARCHIVOS DE AUDIO
# ===============================================

FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024   # 10MB
FILE_UPLOAD_PERMISSIONS = 0o644

# ===============================================
# CONFIGURACIÓN DE JAZZMIN
# ===============================================

JAZZMIN_SETTINGS = {
    # título del sitio admin
    "site_title": "Admin Lab03IA",
    
    # título en la página de login
    "site_header": "Lab03IA",
    
    # título en el navegador
    "site_brand": "Lab03IA Admin",
    
    # texto de bienvenida en el index del admin
    "welcome_sign": "Bienvenido al panel de administración",
    
    # texto de copyright
    "copyright": "Lab03IA",
    
    # buscar en el navbar superior
    "search_model": ["auth.User", "auth.Group"],
    
    # iconos para las apps
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "audio_app": "fas fa-headphones",  # icono para tu app de audio
    },
    
    # iconos por defecto para modelos
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    
    # links adicionales en el user menu
    "usermenu_links": [
        {"name": "Ver sitio", "url": "/", "new_window": True},
    ],
    
    # mostrar sidebar en pantallas pequeñas
    "show_sidebar": True,
    
    # navegación en sidebar expandida por defecto
    "navigation_expanded": True,
    
    # ocultar estas apps
    "hide_apps": [],
    
    # ocultar estos modelos
    "hide_models": [],
    
    # tema de colores (light, dark, auto)
    "theme": "flatly",  # otros: cerulean, cosmo, cyborg, darkly, flatly, journal, litera, lumen, lux, materia, minty, pulse, sandstone, simplex, sketchy, slate, solar, spacelab, superhero, united, yeti
    
    # tema oscuro
    "dark_mode_theme": "darkly",
    
    # botón para cambiar tema
    "show_ui_builder": True,
    
    # personalizar el orden de las apps
    "order_with_respect_to": ["auth", "audio_app"],
}

# UI Tweaks de Jazzmin
JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-primary navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "flatly",
    "dark_mode_theme": "darkly",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}