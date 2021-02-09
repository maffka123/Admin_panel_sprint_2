"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

from django.core.wsgi import get_wsgi_application
import os

application = get_wsgi_application()

env = os.getenv('DJANGO_SETTINGS_MODULE')
if env is None:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')


