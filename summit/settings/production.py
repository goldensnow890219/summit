import json
import os
import dj_database_url

from .base import *

DEBUG = False

DATABASES['default'] = dj_database_url.config()  # noqa F405

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']

env = os.environ.copy()
SECRET_KEY = env['SECRET_KEY']

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

COMPRESS_OFFLINE = True
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter',
]
COMPRESS_CSS_HASHING_METHOD = 'content'

AWS_ACCESS_KEY_ID = env['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = env['AWS_SECRET_ACCESS_KEY']
AWS_STORAGE_BUCKET_NAME = env['AWS_STORAGE_BUCKET_NAME']
AWS_S3_REGION_NAME = 'us-east-2'
AWS_FILE_OVERWRITE = False
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

MEDIA_URL = "https://%s/" % AWS_S3_CUSTOM_DOMAIN
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

ROLLBAR['access_token'] = env['ROLLBAR_ACCESS_TOKEN']  # noqa F405

GOOGLE_SITE_VERIFICATION = env['GOOGLE_SITE_VERIFICATION']

GOOGLE_API_CLIENT_CONFIG = json.loads(env['GOOGLE_API_CLIENT_CONFIG'])

if 'EMAIL_HOST' in env:
    EMAIL_HOST = env['EMAIL_HOST']
    EMAIL_HOST_USER = env['EMAIL_HOST_USERNAME']
    EMAIL_HOST_PASSWORD = env['EMAIL_HOST_PASSWORD']
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
else:
    EMAIL_BACKEND = 'django_sendmail_backend.backends.EmailBackend'

DEFAULT_FROM_EMAIL = env['DEFAULT_FROM_EMAIL']

try:
    from .local import *
except ImportError:
    pass
