import json

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^en&j4mcv-i!0f_$juz)r3+t+hofr73*77m@#+a^(=fijh%6x1'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

ROLLBAR['environment'] = 'development'  # noqa F405

with open('client_id.json', 'r') as json_file:
    GOOGLE_API_CLIENT_CONFIG = json.load(json_file)

BASE_URL = 'http://localhost:8000'

try:
    from .local import *
except ImportError:
    pass
try:
    ROLLBAR['access_token'] = ROLLBAR_ACCESS_TOKEN  # noqa F405
except NameError:
    pass
