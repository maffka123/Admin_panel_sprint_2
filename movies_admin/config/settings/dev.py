from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'options': '-c search_path=content'
        },
        'NAME': os.environ.get('PS_NAME'),
        'USER': os.environ.get('PS_USER'),
        'PASSWORD': os.environ.get('PS_PASSWORD'),
        'HOST': 'localhost',
        'PORT': os.environ.get('PS_PORT'),
    }
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'movies',
    'django_extensions',
    'debug_toolbar',
]