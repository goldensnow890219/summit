import os
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^en&j4mcv-i!0f_$juz)r3+t+hofr73*77m@#+a^(=fijh%6x1'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*']

DATABASES['default']['NAME'] = os.path.join(BASE_DIR, 'db.test.sqlite3')  # noqa F405
