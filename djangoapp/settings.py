import os
from pathlib import Path

# Завантаження .env тільки для локальної розробки
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Завантаження секретів з Azure Key Vault (тільки в Azure)
if os.environ.get('WEBSITE_SITE_NAME') and os.environ.get('BUILDING', 'false').lower() != 'true':
    try:
        from djangoapp.key_vault import load_secrets_to_env
        load_secrets_to_env()
    except Exception as e:
        print(f'Key Vault warning: {e}')

# Базова директорія
BASE_DIR = Path(__file__).resolve().parent.parent

# ===== БЕЗПЕКА =====
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-dev-key-change-in-production'
)

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# ✅ Виправлено: очищення пробілів
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get(
        'ALLOWED_HOSTS',
        'localhost,127.0.0.1'
    ).split(',')
    if host.strip()
]

# Azure internal health check
if os.environ.get('WEBSITE_SITE_NAME'):
    # Azure internal health check IPs (169.254.x.x range)
    import socket
    ALLOWED_HOSTS.append(socket.gethostname())
    ALLOWED_HOSTS += [f'169.254.130.{i}' for i in range(1, 10)]

# ===== ДОДАТКИ =====
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'auth_app',
]

# ===== MIDDLEWARE =====
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'auth_app.middleware.TokenRefreshMiddleware',
]

ROOT_URLCONF = 'djangoapp.urls'

# ===== ШАБЛОНИ =====
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

WSGI_APPLICATION = 'djangoapp.wsgi.application'

# ===== БАЗА ДАНИХ =====
# ✅ Виправлено: persistent storage для Azure
# PostgreSQL в Azure, SQLite локально
if os.environ.get('DB_HOST'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'HOST': os.environ.get('DB_HOST'),
            'NAME': os.environ.get('DB_NAME', 'djangodb'),
            'USER': os.environ.get('DB_USER', 'djangoadmin'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'PORT': '5432',
            'OPTIONS': {'sslmode': 'require'},
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ===== ВАЛІДАЦІЯ ПАРОЛІВ =====
AUTHENTICATION_BACKENDS = [
    'auth_app.backends.EntraIDBackend',
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ===== ІНТЕРНАЦІОНАЛІЗАЦІЯ =====
LANGUAGE_CODE = 'uk'
TIME_ZONE = 'Europe/Kyiv'
USE_I18N = True
USE_TZ = True

# ===== СТАТИЧНІ ФАЙЛИ =====
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ✅ Виправлено: новий синтаксис для Django 6.0
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ===== МЕДІАФАЙЛИ =====
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ===== БЕЗПЕКА ДЛЯ ПРОДАКШЕНУ =====
# Azure сам обробляє HTTPS — не дублюємо redirect!
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Session — завжди cookie-based (не потребує БД)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 3600
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

# ===== ПЕРВИННИЙ КЛЮЧ =====
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ===== ЛОГУВАННЯ =====
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
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}

# ===== MICROSOFT ENTRA ID / MSAL =====
AZURE_CLIENT_ID = os.environ.get('AZURE_CLIENT_ID')
AZURE_TENANT_ID = os.environ.get('AZURE_TENANT_ID')
AZURE_CLIENT_SECRET = os.environ.get('AZURE_CLIENT_SECRET')

AZURE_REDIRECT_URI = os.environ.get(
    'AZURE_REDIRECT_URI',
    'http://localhost:8000/auth/callback/' if DEBUG
    else 'https://mydjango1772289446.azurewebsites.net/auth/callback/'
)

AZURE_AUTHORITY = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}"

# Дозволи які запитує додаток у Microsoft Graph
AZURE_SCOPE = ['User.Read', 'email']

# Перевірка наявності обов'язкових змінних (тільки в production)
BUILDING = os.environ.get('BUILDING', 'false').lower() == 'true'
if not DEBUG and not BUILDING:
    _missing = [
        var for var in ['AZURE_CLIENT_ID', 'AZURE_TENANT_ID', 'AZURE_CLIENT_SECRET']
        if not os.environ.get(var)
    ]
    if _missing:
        raise ValueError(
            f"Відсутні обов'язкові змінні середовища для Entra ID: {', '.join(_missing)}"
        )
# PostgreSQL configuration
