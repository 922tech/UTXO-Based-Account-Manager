from os import getenv, path
import sys
from datetime import timedelta

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

PROJECT_NAME = getenv("PROJECT_NAME", "testproject")

SECRET_KEY = getenv("DJANGO_SECRET_KEY", "this_is_secret!!")
# this key is used for encrypting private keys
CRYPTO_SECRET = getenv("CRYPTO_SECRET", "NmYeTVb3-5EcEQDRS1Gawkpvihcel5RqJjRufq7eAoo=")
ADMIN_ACCOUNT_UUID = getenv("ADMIN_ACCOUNT_UUID", "e9301353-cfda-4704-863d-9d93bf4e4ace")
COINBASE_REWARD = int(getenv("COINBASE_REWARD", "10000000"))

DEBUG = getenv("DJANGO_DEBUG", "1") == '1'
TEST = sys.argv[1:2] == ['test']

ALLOWED_HOSTS = getenv("DJANGO_ALLOWED_HOSTS", '*').split(",")

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',

    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'djoser',

    'apps.common',
    'apps.users',
    'apps.blockchain'
]
if DEBUG:
    INSTALLED_APPS += ['silk', 'django_extensions', 'drf_yasg', ]

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
if DEBUG:
    MIDDLEWARE.insert(0, 'silk.middleware.SilkyMiddleware')

ROOT_URLCONF = f'{PROJECT_NAME}.urls'
API_PREFIX = getenv('ATUOML_API_PREFIX', r'api/blockchain')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = f'{PROJECT_NAME}.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': getenv('POSTGRES_DB', 'testproject'),
        'USER': getenv('POSTGRES_USER', 'testproject'),
        'PASSWORD': getenv('POSTGRES_PASSWORD', 'testproject'),
        'HOST': getenv('POSTGRES_HOST', 'localhost'),
        'PORT': int(getenv('POSTGRES_PORT', '5432')),
        'CONN_MAX_AGE': 60,
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': getenv('REDIS_DEFAULT_CACHE',
                           'redis://localhost:6379/0') if not TEST else 'redis://localhost:6379/15',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 100,
                'retry_on_timeout': True,
            },
            'SENTINEL_KWARGS': {
                'socket_timeout': 0.1,
            },
        },
    }
}

#########

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

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

# Localization
USE_I18N = True
USE_L10N = True
USE_TZ = True
LANGUAGES = [
    ('en', 'English'),
    ('fa', 'Persian')
]
LOCALE_PATHS = [path.join(BASE_DIR, 'localization/locale')]
LANGUAGE_CODE = 'en'
TIME_ZONE = getenv('TIME_ZONE', 'Asia/Tehran')
###############################

STATIC_URL = f'{API_PREFIX}/static/'
STATIC_ROOT = path.join(BASE_DIR, "static")
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = path.join(BASE_DIR, "media")
DATASETS_ROOT = path.join(MEDIA_ROOT, 'datasets')
ARTIFACTS_ROOT = path.join(MEDIA_ROOT, 'artifacts')

# Cors
CORS_ORIGIN_ALLOW_ALL = bool(getenv('CORS_ORIGIN_ALLOW_ALL', 1))
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = [
    "http://localhost:3000",
]

SECURE_REFERRER_POLICY = 'same-origin'
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

renderers = [
    'rest_framework.renderers.JSONRenderer',
]
renderers.append('rest_framework.renderers.BrowsableAPIRenderer') if DEBUG else None

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': renderers,

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTStatelessUserAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny'
    ],

    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '300/second' if TEST else '10/second',
        'user': '300/second' if TEST else '10/second',
    },

    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_VERSION': 'v1',

    'DEFAULT_PAGINATION_CLASS': 'apps.common.pagination.SimplePagination',
}

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'TokenAuth': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': "Token-based authentication. Use 'Token <your_token>' format."
        }
    }
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=10),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'USER_ID_CLAIM': 'user_id',
}
# SESSION_COOKIE_SECURE = True
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = getenv('SESSION_COOKIE_AGE', 60 * 60 * 24)

################################################ celery
CELERY_BROKER_URL = getenv(
    "CELERY_BROKER_URL", default='redis://localhost:6379/1')
CELERY_RESULT_BACKEND = getenv(
    "CELERY_RESULT_BACKEND", default='redis://localhost:6379/2')
CELERY_ACCEPT_CONTENT = ['application/json', 'application/x-python-serialize']
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'pickle'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'visibility_timeout': 86400,   # 1 day
    'max_retries': 5
}
################################################ microservices
