import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env', override=True)
SECRET_KEY='django-insecure-hc#sju3@5u)*c!tb-ewk92tt8u+10a07cao#g^=m)nb2_zzuev'
DEBUG = True
ALLOWED_HOSTS = ['*']


MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


PAYSTACK_PUBLIC_KEY = 'pk_test_9e045e55f0f33796dc48365b2a4fa0dcc8ea0e92'
PAYSTACK_SECRET_KEY	= 'sk_test_21573d264afc3cc181acbbbff1ced33c56e86adf'



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
    "site_title":         "z0mbie ReState",
    "site_header":        "z0mbie Admin",
    "welcome_sign":       "Manage your properties with style",
    "copyright":          "z0mbie's Inc.",

    "show_ui_builder":    True,
    "icons_visible":      True,
    "show_sidebar":       True,
    "navigation_expanded":True,

    # 1) hide the auth app completely
    "hide_apps": ["auth"],

    # 2) still only order your main app
    "order_with_respect_to": ["main"],

    "custom_css": [

        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css",

        "css/jazzmin-overrides.css",
    ],
    "custom_js": [
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/js/all.min.js",
    ],

    "custom_dashboard_link": "admin:dashboard",  

    "themes": {
        "default": {"color": "#3f51b5", "dark": False},
        "darkly":  {"color": "#2a3f54", "dark": True},
        "solar":   {"color": "#f2c037", "dark": False},
    },
    "default_theme": "darkly",

    "icons": {
        "main.CompleteUser":    "fas fa-id-badge",
        "main.Property":        "fas fa-home",
        "main.City":            "fas fa-city",
        "main.Region":          "fas fa-map-marked-alt",
        "main.Inquiry":         "fas fa-question-circle",
        "main.Message":         "fas fa-envelope",
        "main.PropertyImage":   "fas fa-image",
        "main.PropertyFeature": "fas fa-tools",
        "main.SavedProperty":   "fas fa-heart",
        "main.Notification":    "fas fa-bell",
    },

    "custom_links": {
        "main": [
            {"name": "View Site", "url": "/main", "icon": "fas fa-external-link-alt", "new_window": True},
        ]
    },
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": True,
    "brand_small_text": False,
    "brand_colour": "bg-gradient-primary",
    "accent": "accent-primary",
    "navbar": "navbar-primary navbar-dark",
    "no_navbar_border": True,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-warning",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": True,
    "theme": "darkly",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
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
    'whitenoise.middleware.WhiteNoiseMiddleware',
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
        'NAME': 'mineeer',
        'USER': 'postgres',
        'PASSWORD': 'Attackontitan420@',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


AUTH_USER_MODEL = 'main.CompleteUser'

REDIS_URL = "rediss://default:AcoyAAIjcDFjMTI2NjJhM2RiMDQ0OWE3YjM4YWU3OWUyZDEyYjhiMXAxMA@optimum-gar-51762.upstash.io:6379"



CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SSL": True,  
        }
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL]
        },
    },
}


# ADMIN_EMAIL = 'casazapp15@gmail.com'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.naomall.com'
EMAIL_PORT = 465
EMAIL_HOST_USER = 'support@naomall.com'
EMAIL_HOST_PASSWORD = 'Attackontitan420@'
EMAIL_USE_SSL = True
DEFAULT_FROM_EMAIL = '"The Casaz Team" <support@naomall.com>'
SUPPORT_EMAIL = 'support@naomall.com'

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    'http://localhost:19006',
    'http://127.0.0.1:19006',
    'http://localhost:8081',
    'exp://127.0.0.1:19000',
    'http://192.168.157.75:8000',

]

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

CSRF_TRUSTED_ORIGINS = [
    "https://casaz-2.onrender.com",
    'http://192.168.157.75:8000',
]

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'None'

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'None'


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

]


STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
