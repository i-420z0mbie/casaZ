
# settings.py

import os
from pathlib import Path
from dotenv import load_dotenv
from django.urls import reverse_lazy


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env', override=True)
SECRET_KEY='django-insecure-hc#sju3@5u)*c!tb-ewk92tt8u+10a07cao#g^=m)nb2_zzuev'
DEBUG = True
ALLOWED_HOSTS = ['*']


AWS_ACCESS_KEY_ID       = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY   = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME      = os.getenv("AWS_S3_REGION_NAME")
AWS_DEFAULT_ACL         = None
AWS_QUERYSTRING_AUTH    = False

# 2) Use your storage classes
DEFAULT_FILE_STORAGE   = "main.storages.MediaStorage"
STATICFILES_STORAGE    = "main.storages.StaticStorage"

# 3) Build your URLs
MEDIA_URL  = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/media/"
STATIC_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/static/"





# Installed apps
INSTALLED_APPS = [
    # Django
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'corsheaders',
    'rest_framework_simplejwt',
    'channels',
    'django_filters',
    'storages',
    'rest_framework',

    # Local apps
    'main',
    'core',
]

JAZZMIN_SETTINGS = {
    # Vibrant Branding with emojis
    "site_title": "🏠 z0mbie ReState",      
    "site_header": "👻 z0mbie Admin",    
    "site_brand": "ReState Dashboard",
    "welcome_sign": "✨ Welcome to Undead Real Estate Management ✨",
    "copyright": "© z0mbie's Inc. | Eternal Property Solutions",

    # UI Configuration
    "show_ui_builder": True,
    "navigation_expanded": True,
    "related_modal_active": True,
    
    # Modern Theme Configuration
    "themes": {
        "darkly": {"color": "#6f42c1", "dark": True},  # Purple accent
        "solar": {"color": "#ffd95b", "dark": False},
        "neon": {"color": "#0ff0fc", "dark": True},
    },
    "default_theme": "darkly",

    # Enhanced Icons with FA5 Pro
    "icons": {
        "auth.User": "fas fa-user-astronaut",
        "auth.Group": "fas fa-users-class",
        "main.CompleteUser": "fas fa-id-card-alt",
        "main.Property": "fas fa-building",
        "main.City": "fas fa-city",
        "main.Region": "fas fa-globe-americas",
        "main.Inquiry": "fas fa-comments-dollar",
        "main.Message": "fas fa-paper-plane",
        "main.PropertyImage": "fas fa-images",
        "main.PropertyFeature": "fas fa-toolbox",
        "main.SavedProperty": "fas fa-heart-circle-bolt",
        "main.Notification": "fas fa-bell-on",
    },

    # Custom Dashboard Elements
    "order_with_respect_to": ["auth", "main", "analytics"],
    "custom_links": {
        "main": [{
            "name": "🌍 Visit Site", 
            "url": "/", 
            "icon": "fas fa-rocket", 
            "new_window": True
        }]
    },

    # Advanced UI Features
    "changeform_format": "horizontal_tabs",
    "show_related_modal": True,
}

JAZZMIN_UI_TWEAKS = {
    # Dark Modern Theme
    "navbar_small_text": False,
    "footer_small_text": True,
    "body_small_text": False,
    "brand_colour": "bg-gradient-primary",
    "accent": "accent-info",
    "navbar": "navbar-dark bg-gradient-dark",
    "no_navbar_border": True,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-info",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_compact_style": True,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": True,
    "theme": "darkly",
    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    },
}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'freeClassifieds.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'freeClassifieds.wsgi.application'
ASGI_APPLICATION = 'freeClassifieds.asgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

# Custom user model
AUTH_USER_MODEL = 'main.CompleteUser'


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("localhost", 6379)],
        },
    },
}

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    'http://localhost:19006',
    'http://127.0.0.1:19006',
    'http://localhost:8081',
    'exp://127.0.0.1:19000',
    'http://192.168.14.75:8000',
]

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}


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


STATICFILES_DIRS = [
    BASE_DIR / "static",        # if you have a project-level /static/ folder
    # BASE_DIR / "node_modules/jazzmin/static",  # only if you installed Jazzmin via npm
]


STATIC_ROOT = BASE_DIR / "staticfiles"

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
