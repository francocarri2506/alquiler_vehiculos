from .settings import *

SECRET_KEY = 'clave-para-tests'
DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Para evitar el ruido del log en los tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
}

