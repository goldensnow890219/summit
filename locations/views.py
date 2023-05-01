from functools import reduce

import rollbar
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.views.decorators.http import require_http_methods
from wagtail.search.backends import get_search_backend

from locations.models import Professional, Service, LocationPage
from locations.registerImporter import TenantImporter
import json
import urllib.parse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect
@csrf_exempt

def book_now(request):
    search_query = request.GET.get('query', '')
    search_results = Professional.objects.filter(page__live=True)
    if search_query:
        s = get_search_backend()
        search_results = s.search(search_query, search_results)
    service_ids = reduce(
        lambda base, result: base | set(result.services.values_list('id', flat=True)),
        search_results,
        set(),
    )
    services = Service.objects.filter(pk__in=service_ids)

    return TemplateResponse(request, 'locations/book_now.html', {
        'title': 'Book Now',
        'search_query': search_query,
        'search_results': search_results,
        'services': services,
    })

def account(request):


    if not request.session.get('tenantEmail'):
        return redirect('/login')

    session_email = ''
    session_location = ''
    if 'tenantEmail' in request.session:
        session_email = request.session['tenantEmail']
    
    if 'tenantLocation' in request.session:
        session_location = request.session['tenantLocation']
    
    

    id_name = request.POST.get('name', '')
    id_company = request.POST.get('company', '')
    id_location = request.POST.get('location', '')
    id_studio = request.POST.get('studio', '')
    id_booking = request.POST.get('booking', '')
    id_phone = request.POST.get('phone', '')
    id_email = request.POST.get('email', '')
    id_password = request.POST.get('password', '')
    id_website = request.POST.get('website', '')
    id_social_1 = request.POST.get('social_1', '')
    id_social_2 = request.POST.get('social_2', '')
    id_photo = request.POST.get('photo', '')
    id_upload = ''
    id_load_photo = ''

    if request.method == 'POST' and request.FILES:
      upload_file = request.FILES.get('photo', '')
      fs = FileSystemStorage(location='static/images/')
      filename = fs.save(upload_file.name, upload_file)
      id_upload = 'https://www.summitsalonstudios.com/static/images/'+upload_file.name
#      id_upload = fs.url(filename)
    
    id_service = (',').join(request.POST.getlist('service'))
    id_service_list = id_service.split(",")
      
    tenant_info = {
      'id_name': id_name,
      'id_company': id_company,
      'id_location': id_location,
      'id_service': id_service,
      'id_studio': id_studio,
      'id_booking': id_booking,
      'id_phone': id_phone,
      'id_email': id_email,
      'id_password': id_password,
      'id_website': id_website,
      'id_social_1': id_social_1,
      'id_social_2': id_social_2,
      'id_photo': id_upload,
    }
    statu = ''
    alertContent = ''
    session_tenant_info = ''
    
    session_info = {
      'id_email': session_email,
      'id_location': session_location,
    }
    
    if id_name:
      with TenantImporter() as importer:
        statu = importer.import_info(**tenant_info)
        if statu == 'new':
          #alertContent = 'Added successfully!'
          alertContent = statu
        elif statu == 'modify':
          #alertContent = 'Modified Successfully!'
          alertContent = statu
        else:
          #alertContent = 'Failed'
          alertContent = statu
    
    with TenantImporter() as importer:
        load_statu = importer.load_info(**session_info)
        session_tenant_info = load_statu
        
    id_name = session_tenant_info.get('name')
    id_company = session_tenant_info.get('business_name')
    id_location = session_location
    id_service_list = session_tenant_info.get('services')
    id_studio = session_tenant_info.get('studio')
    id_booking = session_tenant_info.get('booking_link')
    id_phone = session_tenant_info.get('phone_number')
    id_email = session_tenant_info.get('email')
    id_password = session_tenant_info.get('password')
    id_website = session_tenant_info.get('website')
    id_social_1 = session_tenant_info.get('social_media_link_1')
    id_social_2 = session_tenant_info.get('social_media_link_2')
    id_photo = ''
    id_load_photo = session_tenant_info.get('photo')
    
    search_query = request.POST.get('query', '')
    search_results = Professional.objects.filter(page__live=True)
    if search_query:
        s = get_search_backend()
        search_results = s.search(search_query, search_results)
    service_ids = reduce(
        lambda base, result: base | set(result.services.values_list('id', flat=True)),
        search_results,
        set(),
    )
    services = Service.objects.filter(pk__in=service_ids)
    locations = LocationPage.objects.live()
    
    return TemplateResponse(request, 'locations/account.html', {
        'title': 'Account',
        'search_query': search_query,
        'search_results': search_results,
        'id_name': id_name,
        'id_company': id_company,
        'id_location': id_location,
        'id_service': id_service,
        'id_service_list': id_service_list,
        'id_studio': id_studio,
        'id_booking': id_booking,
        'id_phone': id_phone,
        'id_email': id_email,
        'id_password': id_password,
        'id_website': id_website,
        'id_social_1': id_social_1,
        'id_social_2': id_social_2,
        'id_photo': id_photo,
        'alertContent': alertContent,
        'services': services,
        'locations': locations,
        'request_data': request.POST,
        'id_upload': id_upload,
        'id_load_photo': id_load_photo,
    })

def login(request):

    if request.session.get('tenantEmail'):
        return redirect('/account')

    session_email = ''
    session_location = ''

    id_email = request.POST.get('email', '')
    id_password = request.POST.get('password', '')
    
    tenant_info = {
      'id_email': id_email,
      'id_password': id_password,
    }
    
    tenantStatu = ''
    if id_email:
      with TenantImporter() as importer:
          statu = importer.loginTenant(**tenant_info)
          tenantStatu = statu
    
    if tenantStatu != '' and tenantStatu != 'empty':
        request.session['tenantEmail'] = id_email
        request.session['tenantLocation'] = tenantStatu
        request.session.modified = True
        return redirect('/account')
    
    if 'tenantEmail' in request.session:
        session_email = request.session['tenantEmail']
    
    if 'tenantLocation' in request.session:
        session_location = request.session['tenantLocation']
    
    return TemplateResponse(request, 'locations/login.html', {
        'title': 'Login',
        'statu': tenantStatu,
    })

def logout(request):

    if 'tenantEmail' in request.session:
        del request.session['tenantEmail']
    if 'tenantLocation' in request.session:
        del request.session['tenantLocation']
    
    return redirect('/login')
    
def register(request):
    if request.session.get('tenantEmail'):
        return redirect('/account')
  
    id_name = request.POST.get('name', '')
    id_company = request.POST.get('company', '')
    id_location = request.POST.get('location', '')
    id_studio = request.POST.get('studio', '')
    id_booking = request.POST.get('booking', '')
    id_phone = request.POST.get('phone', '')
    id_email = request.POST.get('email', '')
    id_password = request.POST.get('password', '')
    id_website = request.POST.get('website', '')
    id_social_1 = request.POST.get('social_1', '')
    id_social_2 = request.POST.get('social_2', '')
    id_photo = request.POST.get('photo', '')
    id_upload = ''

    if request.method == 'POST' and request.FILES:
      upload_file = request.FILES.get('photo', '')
      fs = FileSystemStorage(location='static/images/')
      filename = fs.save(upload_file.name, upload_file)
      id_upload = 'https://www.summitsalonstudios.com/static/images/'+upload_file.name
#      id_upload = fs.url(filename)
    
    id_service = (',').join(request.POST.getlist('service'))
    id_service_list = id_service.split(",")
      
    tenant_info = {
      'id_name': id_name,
      'id_company': id_company,
      'id_location': id_location,
      'id_service': id_service,
      'id_studio': id_studio,
      'id_booking': id_booking,
      'id_phone': id_phone,
      'id_email': id_email,
      'id_password': id_password,
      'id_website': id_website,
      'id_social_1': id_social_1,
      'id_social_2': id_social_2,
      'id_photo': id_upload,
    }
    statu = ''
    alertContent = ''
    if id_name:
      with TenantImporter() as importer:
        statu = importer.import_info(**tenant_info)
        alertContent = statu
        if statu == 'success':
            request.session['tenantEmail'] = id_email
            request.session['tenantLocation'] = id_location
            request.session.modified = True
            return redirect('/account')
            
    search_query = request.POST.get('query', '')
    search_results = Professional.objects.filter(page__live=True)
    if search_query:
        s = get_search_backend()
        search_results = s.search(search_query, search_results)
    service_ids = reduce(
        lambda base, result: base | set(result.services.values_list('id', flat=True)),
        search_results,
        set(),
    )
    services = Service.objects.filter(pk__in=service_ids)
    locations = LocationPage.objects.live()
    
    return TemplateResponse(request, 'locations/register_page.html', {
        'title': 'Register',
        'search_query': search_query,
        'search_results': search_results,
        'id_name': id_name,
        'id_company': id_company,
        'id_location': id_location,
        'id_service': id_service,
        'id_service_list': id_service_list,
        'id_studio': id_studio,
        'id_booking': id_booking,
        'id_phone': id_phone,
        'id_email': id_email,
        'id_password': id_password,
        'id_website': id_website,
        'id_social_1': id_social_1,
        'id_social_2': id_social_2,
        'id_photo': id_photo,
        'alertContent': alertContent,
        'services': services,
        'locations': locations,
        'request_data': request.POST,
        'id_upload': id_upload,
        'empty': 'fill',
    })


@require_http_methods(['POST'])
def file_webhook(request):
    rollbar.report_message('Tenant file changed', level='info', request=request)
    return HttpResponse()
