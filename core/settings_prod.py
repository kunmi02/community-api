"""
Production settings for the Django project.
"""

from .settings import *
import dj_database_url

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Security settings
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Add WhiteNoise middleware
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Allow Railway domain
ALLOWED_HOSTS = ['*', '.railway.app']

# Configure Database using Railway's environment variables
# Railway provides individual environment variables for MySQL
# MYSQL_URL = os.environ.get('MYSQLURL')
# DATABASE_URL = os.environ.get('DATABASE_URL')
MYSQL_HOST = os.environ.get('MYSQLHOST') or os.environ.get('MYSQL_HOST')
MYSQL_PORT = os.environ.get('MYSQLPORT') or os.environ.get('MYSQL_PORT')
MYSQL_USER = os.environ.get('MYSQLUSER') or os.environ.get('MYSQL_USER') or os.environ.get('MYSQL_USERNAME')
MYSQL_PASSWORD = os.environ.get('MYSQLPASSWORD') or os.environ.get('MYSQL_PASSWORD')
MYSQL_DATABASE = os.environ.get('MYSQLDATABASE') or os.environ.get('MYSQL_DATABASE') or os.environ.get('MYSQL_DB')

# Log database configuration for debugging
# print(f"Database configuration: URL={DATABASE_URL is not None}, MYSQL_URL={MYSQL_URL is not None}")
print(f"MySQL direct config: HOST={MYSQL_HOST}, DB={MYSQL_DATABASE}, USER={MYSQL_USER is not None}")

import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('MYSQL_DATABASE'),
        'USER': os.getenv('MYSQLUSER'),
        'PASSWORD': os.getenv('MYSQLPASSWORD'),
        'HOST': os.getenv('MYSQLHOST'),
        'PORT': os.getenv('MYSQLPORT'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'use_unicode': True,
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION'",
            'sql_mode': 'STRICT_TRANS_TABLES',
        },
        'TEST': {
            'CHARSET': 'utf8mb4',
            'COLLATION': 'utf8mb4_unicode_ci',
        }
    }
}

# Add MySQL-specific options if using MySQL
if 'default' in DATABASES and DATABASES['default'].get('ENGINE') == 'django.db.backends.mysql':
    DATABASES['default']['OPTIONS'] = {
        'charset': 'utf8mb4',
        'use_unicode': True,
    }

# Disable browsable API in production
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (
    'rest_framework.renderers.JSONRenderer',
)

# Increase JWT token security
SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'] = timedelta(minutes=15)
SIMPLE_JWT['ROTATE_REFRESH_TOKENS'] = True
SIMPLE_JWT['BLACKLIST_AFTER_ROTATION'] = True

# Email settings - using console backend for now to avoid SMTP errors
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Commented out SMTP settings until properly configured
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
# EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
# EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
# EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
# EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
# DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@example.com')

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/django.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Ensure logs directory exists
os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
