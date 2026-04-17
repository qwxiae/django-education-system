from pathlib import Path
from decouple import config
import sys
import os

ENVIRONMENT = config("ENVIRONMENT", default="development")

def get_secret(name, env_var, default=None, cast=str):
    secret_path = f"/run/secrets/{name}"
    if os.path.exists(secret_path):
        with open(secret_path) as f:
            return f.read().strip()

    return config(env_var, default=default, cast=cast)


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = get_secret("django_secret_jey", "SECRET_KEY")
DEBUG = get_secret("debug", "DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = get_secret(
    "allowed_hosts", "ALLOWED_HOSTS", default="localhost,127.0.0.1"
).split(",")


PROJECT_APPS = [
    "apps.users",
    "apps.courses",
    "apps.lessons",
    "apps.submissions",
    "apps.core",
    "apps.analytics",
]

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "tinymce",
    "django_celery_results",
] + PROJECT_APPS

MIDDLEWARE = [
    "apps.core.middleware.RequestLogMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# whitenoise used in production
if ENVIRONMENT == "production":
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
else:
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # templates are at same level as base app
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# SECURITY WARNING: use postgres in production, store data in env
if ENVIRONMENT == "production":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "HOST": get_secret("postgres_host", "POSTGRES_HOST"),
            "NAME": get_secret("postgres_name", "POSTGRES_DB"),
            "USER": get_secret("postgres_user", "POSTGRES_USER"),
            "PASSWORD": get_secret("db_password", "POSTGRES_PASSWORD"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# === Set static and media folders ===
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# === Change auth model ===
AUTH_USER_MODEL = "users.User"
AUTHENTICATION_BACKENDS = ["apps.users.backends.EmailBackend"]


if ENVIRONMENT == "production":
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": get_secret(
                "redis_url", "REDIS_URL", default="redis://redis:6379/0"
            ),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "local-cache",
        }
    }

# === Auth ===
EMAIL_HOST = get_secret("email_host", "EMAIL_HOST", default="localhost")
LOGIN_URL = "users:login"


# Debugtoolbar does not start in tests
# Needed for debugtoolbar
TESTING = "test" in sys.argv or "PYTEST_VERSION" in os.environ

if not TESTING and DEBUG:
    import socket

    INTERNAL_IPS = [
        "127.0.0.1",
    ]
    if ENVIRONMENT == "production":
        hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
        INTERNAL_IPS += [ip[:-1] + "1" for ip in ips]

    INSTALLED_APPS = [
        *INSTALLED_APPS,
        "debug_toolbar",
    ]
    MIDDLEWARE = [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
        *MIDDLEWARE,
    ]

# === Input widget for courses in admin ===
TINYMCE_DEFAULT_CONFIG = {
    "height": 400,
    "menubar": False,
    "plugins": "lists link image media code codesample",
    "toolbar": "undo redo | formatselect | bold italic | "
    "bullist numlist | link image media codesample | code",
    "images_upload_url": "/tinymce/upload/",
    "automatic_uploads": True,
    "file_picker_types": "image media",
}

# === UI change in admin ===
JAZZMIN_SETTINGS = {
    "site_title": "EduPlatform Admin",
    "site_header": "EduPlatform",
    "site_brand": "EduPlatform",
    "show_ui_builder": False,
    "custom_css": "css/admin_custom.css",
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": False,
    "accent": "accent-primary",
    "navbar": "navbar-white navbar-light",
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
    "theme": "pulse",
    "default_theme_mode": "dark",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}


# === Celery ===
CELERY_BROKER_URL = get_secret(
    "rabbitmq_url",
    "RABBITMQ_URL",
    default="amqp://guest:guest@localhost:5672//"
)

# stores results in postgres
CELERY_RESULT_BACKEND = "django-db"
CELERY_CACHE_BACKEND = "django-cache"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"


# === LOGGING ====
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "verbose": {
            "format": "[{levelname}] {asctime} {name}: {message}",
            "style": "{",
        },
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },

    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },

    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

# === SANDBOX ===
PISTON_URL = get_secret("piston_url", "PISTON_URL", default="http://piston:2000")
