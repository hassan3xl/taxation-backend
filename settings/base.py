from datetime import timedelta
from pathlib import Path
import sys

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
AUTH_USER_MODEL = 'users.User'
import os
from dotenv import load_dotenv

load_dotenv()

from decouple import config
import cloudinary
import cloudinary.uploader
import cloudinary.api
from datetime import timedelta
from decouple import config

# Application definition

sys.path.insert(0, str(BASE_DIR))

INSTALLED_APPS = [

    'cloudinary',
    'cloudinary_storage',


    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken', # Required by dj-rest-auth
    'rest_framework_simplejwt',
    
    # 'rest_framework_simplejwt.token_blacklist', # For logout to work properly
    
    'dj_rest_auth',
    'corsheaders',

    "apps.core.apps.CoreConfig",
    "apps.users.apps.UsersConfig",
]
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET')
}

cloudinary.config(
    cloud_name=CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key=CLOUDINARY_STORAGE['API_KEY'],
    api_secret=CLOUDINARY_STORAGE['API_SECRET'],
    secure=True
)

STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    
    # Static: Stays local (or use WhiteNoise in production)
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]

ROOT_URLCONF = 'src.urls'
SITE_ID = 1

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # "rest_framework.authentication.TokenAuthentication",  # Basic static token auth
        # "rest_framework.authentication.SessionAuthentication",  # Django admin & templates
        "rest_framework_simplejwt.authentication.JWTAuthentication",  # SPA & mobile apps

    ],

    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',  # For guests (not logged in)
        'rest_framework.throttling.UserRateThrottle'   # For logged-in users
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '10/minute',  # Guests get 10 requests per min
        'user': '1000/day',    # Users get 1000 requests per day
        'sensitive_action': '5/minute', # <--- NEW SCOPE
    }
}


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True, # Important: Issue new refresh token on use
    'BLACKLIST_AFTER_ROTATION': True, # Important: Old refresh token becomes invalid
    'AUTH_HEADER_TYPES': ('Bearer',),
    "UPDATE_LAST_LOGIN": True,                       

}

REST_USE_JWT = True

REST_AUTH = {
    'USE_JWT': True,
    'JWT_AUTH_COOKIE': None,         
    'JWT_AUTH_REFRESH_COOKIE': None,  # <--- Must be explicitly None
    'JWT_AUTH_HTTPONLY': False,       # Optional, but good to be explicit
    "REGISTER_SERIALIZER": "users.api.serializers.auth_serializers.CustomRegisterSerializer",

}

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]




# ACCOUNT_USER_MODEL_USERNAME_FIELD = None  
# ACCOUNT_EMAIL_VERIFICATION = "none"
# ACCOUNT_LOGIN_METHODS = {"email"}
# ACCOUNT_UNIQUE_EMAIL = True

# ACCOUNT_SIGNUP_FIELDS = {
#     "email": {"required": True},
#     "password1": {"required": True},
#     "password2": {"required": True},
# }




TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'src.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
