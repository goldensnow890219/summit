from django.conf import settings as django_settings


def settings(request):
    return {
        'GOOGLE_SITE_VERIFICATION': django_settings.GOOGLE_SITE_VERIFICATION,
    }
