from .base import *
import mimetypes
mimetypes.add_type("text/css", ".css", True)

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'options': '-c search_path=content'
        },
        'NAME': os.environ.get('PS_NAME'),
        'USER': os.environ.get('PS_USER'),
        'PASSWORD': os.environ.get('PS_PASSWORD'),
        'HOST': os.environ.get('PS_HOST'),
        'PORT': os.environ.get('PS_PORT'),
    }
}