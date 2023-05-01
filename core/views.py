from datetime import datetime, timezone
from functools import wraps

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from google.auth.transport.requests import Request
from wagtail.admin import messages

from core.gdrive import GDrive
from core.models import SystemVariable


@staff_member_required
@require_http_methods(['GET', 'POST'])
def google_api_auth(request):
    google_auth_state = request.GET.get('state')
    if google_auth_state:
        if request.session.get('google_auth_state') != google_auth_state:
            return HttpResponseBadRequest()
        credentials = GDrive.create_credentials(
            request.path, request.build_absolute_uri(), google_auth_state
        )
        # The SystemVariable google_api_token stores the user's access and refresh tokens,
        # and is created automatically when the authorization flow completes for the first
        # time.
        SystemVariable.set('google_api_token', (credentials, google_auth_state))
    else:
        authorization_url, state = GDrive.create_auth_url(request.path)
        request.session['google_auth_state'] = state
        return redirect(authorization_url)

    return redirect('google-api-files')


def require_google_credentials(view_func):
    @wraps(view_func)
    def wrapper_func(request, *args, **kwargs):
        # The SystemVariable google_api_token stores the user's access and refresh tokens,
        # and is created automatically when the authorization flow completes for the first
        # time.
        value = SystemVariable.get('google_api_token')
        if value:
            credentials, state = value
        else:
            return redirect(reverse('google-api-auth'))

        if request.session.get('google_auth_state') != state:
            return render(request, 'core/admin/google_api/reset_credentials_confirmation.html')

        if not credentials.valid:
            if credentials.expired and credentials.refresh_token:
                #credentials.refresh(Request())
                SystemVariable.set('google_api_token', (credentials, state))
            else:
                raise PermissionError("Invalid Google credentials state")
        setattr(request, 'google_credentials', credentials)
        return view_func(request, *args, **kwargs)

    return wrapper_func


@staff_member_required
@require_http_methods(['GET'])
@require_google_credentials
def google_api_files(request):
    gd = GDrive(request.google_credentials)
    page_token = request.GET.get('page_token')
    files, next_token = gd.list_files(page_token=page_token)
    current_file = SystemVariable.get('tenant_file_info')
    return render(
        request,
        'core/admin/google_api/list_files.html',
        context={'files': files, 'next_token': next_token, 'current_file': current_file},
    )


@staff_member_required
@require_http_methods(['POST'])
@require_google_credentials
def google_api_pick_file(request):
    file_id = request.POST.get('file_id')
    gd = GDrive(request.google_credentials)
    file = gd.get_file_meta(file_id)
    imported_time = datetime.utcfromtimestamp(0).replace(tzinfo=timezone.utc).isoformat()
    SystemVariable.set('tenant_file_info', {**file, 'importedTime': imported_time})
    messages.success(request, 'File registered successfully')
    return redirect('google-api-files')
