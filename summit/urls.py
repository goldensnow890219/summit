from django.conf import settings
from django.urls import include, path
from django.contrib import admin
from django.views.generic import TemplateView

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from core import views as core_views
from home.views import StudioLeasingView
from locations import views as location_views

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('locations/webhook/', location_views.file_webhook, name='locations-webhook'),
    path('admin/google-api/auth/', core_views.google_api_auth, name='google-api-auth'),
    path('admin/google-api/files/', core_views.google_api_files, name='google-api-files'),
    path(
        'admin/google-api/pick-file/', core_views.google_api_pick_file, name='google-api-pick-file'
    ),
    path('admin/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),

    path('book-now/', location_views.book_now, name='book-now'),
    path('register/', location_views.register, name='register'),
    path('login/', location_views.login, name='login'),
    path('logout/', location_views.logout, name='logout'),
    path('account/', location_views.account, name='account'),
    path(
        'about-us/',
        TemplateView.as_view(
            template_name='home/about.html', extra_context={'title': 'About Us'}
        ),
        name='about',
    ),
    path(
        'studio-leasing/',
        StudioLeasingView.as_view(),
        name='studio-leasing'
    ),
    path('blog/', TemplateView.as_view(template_name='home/blog.html'), name='blog'),

]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = urlpatterns + [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", include(wagtail_urls)),

    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]
