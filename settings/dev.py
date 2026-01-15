from .base import *
import os
import dj_database_url

DEBUG = True
import socket
hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS = [ip[:-1] + "1" for ip in ips] + ["127.0.0.1"]

# SECRET_KEY = os.environ["SECRET_KEY"]
SECRET_KEY="dasdaskdaskdjasds"


ALLOWED_HOSTS = [
    "localhost" ,
    "127.0.0.1"
    ]
DATABASES = {
    # use sqlite3 in development
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
    # "default": dj_database_url.config(default=os.getenv("NEON_DB"))

}

STORAGES = {
    # Media: Goes to Cloudinary
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    
    # Static: Stays local (or use WhiteNoise in production)
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}


# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": os.getenv("REDIS_URL", "redis://redis:6379/1"),
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#         },
#     }
# }

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"



# At the bottom of settings.py
if DEBUG:
    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": lambda request: True,
    }


# # Check if we are running pytest or standard django tests
# TESTING = 'pytest' in sys.modules or 'test' in sys.argv

# # ONLY load Debug Toolbar if we are NOT testing
# if not TESTING:
#     # 1. Add the App
#     INSTALLED_APPS += ['debug_toolbar']
    
#     # 2. Add the Middleware (Insert at the top is best)
#     MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    
#     # 3. Add the Config
#     DEBUG_TOOLBAR_CONFIG = {
#         "SHOW_TOOLBAR_CALLBACK": lambda request: True,
#     }
    
#     # 4. Internal IPs (Docker fix)
#     import socket
#     try:
#         hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
#         INTERNAL_IPS = [ip[:-1] + "1" for ip in ips] + ["127.0.0.1"]
#     except Exception:
#         INTERNAL_IPS = ["127.0.0.1"]