import hashlib
import json
import logging
from contextlib import suppress
from copy import deepcopy
from io import BytesIO
from typing import Dict, List

import requests
from django.core.exceptions import ValidationError
from django.core.files.images import ImageFile
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from wagtail.core.models import PageRevision
from wagtail.images import get_image_model

from locations.models import LocationsIndexPage, LocationPage, Service

logger = logging.getLogger(__name__)


class LocationData:
    def __init__(self, revision_content):
        self.revision_content = revision_content
        self.professionals = []
        self.modified = False


class TenantImporter:
    def __init__(self):
        self.index: LocationsIndexPage = LocationsIndexPage.objects.first()
        self.locations: Dict[str, LocationData] = {
            location.slug: LocationData(json.loads(location.get_latest_revision().content_json))
            for location in self.index.get_children()
        }
        self.services: Dict[str, int] = {
            service.name: service.pk for service in Service.objects.all()
        }
        self.user = get_user_model().objects.get(username='system')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for location_data in self.locations.values():
            if location_data.modified:
                location_data.revision_content['professionals'] = location_data.professionals
                page = PageRevision(
                    page_id=location_data.revision_content['pk'],
                    content_json=json.dumps(location_data.revision_content),
                ).as_page_object()
                page.save_revision(log_action=True, user=self.user).publish();
                # Start moderation workflow
                with suppress(ValidationError):
                    workflow = page.get_workflow()
                    workflow.start(page, self.user)

    def _get_location(self, name) -> LocationData:
#        slug = slugify(name)
        slug = name
        if slug not in self.locations:
            location = LocationPage(slug=slug, title=name, live=False, owner=self.user)
            self.index.add_child(instance=location)
            revision = location.save_revision(log_action=True, user=self.user)
            self.locations[slug] = LocationData(json.loads(revision.content_json))
        return self.locations[slug]


    def _import_services(self, tenant_info: Dict[str, str]) -> List[int]:
        services = []
        service_names = tenant_info.get('id_service', '')
        for service_name in service_names.split(','):
            service_name = service_name.strip()
            if not service_name:
                continue
            elif service_name not in self.services:
                service = Service(name=service_name)
                service.save()
                self.services[service_name] = service.pk
            if self.services[service_name] not in services:
                services.append(self.services[service_name])
        return sorted(services)

    def _import_profile_image(self, name, tenant_info: Dict[str, str]) -> int:
        image_url = tenant_info.get('id_photo', '').strip()
        if not image_url:
            raise ValueError('No image')
        title = f'{name} Profile.jpg'
        image_model = get_image_model()
        file_contents = requests.get(image_url).content
        file_hash = hashlib.sha1(file_contents).hexdigest()
        try:
            image = image_model.objects.get(file_hash=file_hash)
        except image_model.DoesNotExist:
            image_content = BytesIO(file_contents)
            image_file = ImageFile(image_content, name=title)
            image = image_model(title=title, file=image_file, file_hash=file_hash)
            image.save()
        return image.pk

    def import_info(self, **tenant_info):
        location_name = tenant_info.get('id_location')
        location = self._get_location(location_name)
        email = tenant_info.get('id_email', '').strip()
        new_tenant = True


        for professional in location.revision_content.get('professionals'):
            if professional['email'] == email:
                new_tenant = False
                professional['name'] = tenant_info.get('id_name', '').strip()
                professional['business_name'] = tenant_info.get('id_company', '').strip()
                professional['studio'] = tenant_info.get('id_studio', '').strip()
                professional['email'] = email
                professional['password'] = tenant_info.get('id_password', '').strip()
                professional['phone_number'] = tenant_info.get('id_phone', '').strip()
                professional['website'] = tenant_info.get('id_website', '').strip()
                professional['booking_link'] = tenant_info.get('id_booking', '').strip()
                professional['social_media_link_1'] = tenant_info.get('id_social_1', '').strip()
                professional['social_media_link_2'] = tenant_info.get('id_social_2', '').strip()
                professional['services'] = self._import_services(tenant_info)
                with suppress(Exception):
                    if tenant_info.get('id_photo', '').strip() != '':
                        professional['photo'] = self._import_profile_image(professional['name'], tenant_info)
            location.professionals.append(professional)
            location.modified = True
            
        if new_tenant:
            current_professional = next(
                (
                    professional
                    for professional in location.revision_content.get('professionals')
                    if professional['email'] == email
                ),
                dict(pk=None, email=email, page=location.revision_content['pk'])
            )
            
            new_professional = deepcopy(current_professional)
            new_professional['name'] = tenant_info.get('id_name', '').strip()
            new_professional['business_name'] = tenant_info.get('id_company', '').strip()
            new_professional['studio'] = tenant_info.get('id_studio', '').strip()
            new_professional['email'] = email
            new_professional['password'] = tenant_info.get('id_password', '').strip()
            new_professional['phone_number'] = tenant_info.get('id_phone', '').strip()
            new_professional['website'] = tenant_info.get('id_website', '').strip()
            new_professional['booking_link'] = tenant_info.get('id_booking', '').strip()
            new_professional['social_media_link_1'] = tenant_info.get('id_social_1', '').strip()
            new_professional['social_media_link_2'] = tenant_info.get('id_social_2', '').strip()
            new_professional['services'] = self._import_services(tenant_info)
            with suppress(Exception):
              if tenant_info.get('id_photo', '').strip() != '':
                new_professional['photo'] = self._import_profile_image(new_professional['name'], tenant_info)
            
            location.professionals.append(new_professional)
            location.modified = True


        
#        return location.professionals
        return 'success'


    def loginTenant(self, **tenant_info):
        id_email = tenant_info.get('id_email', '').strip()
        id_password = tenant_info.get('id_password', '').strip()
        
        for location in self.locations.values():
            for professional in location.revision_content.get('professionals'):
                if professional['email'] == id_email:
                    if 'password' in professional:
                        if professional['password'] == id_password:    
                            return location.revision_content.get('slug')
                    
        return 'empty'
        
    def load_info(self, **tenant_info):
        id_email = tenant_info.get('id_email', '').strip()
        id_location = tenant_info.get('id_location', '').strip()
        
        for location in self.locations.values():
            if id_location == location.revision_content.get('slug'):
                for professional in location.revision_content.get('professionals'):
                    if professional['email'] == id_email:
                        if professional['photo']:
                          image_model = get_image_model()
                          image = image_model.objects.get(id=professional['photo'])
                          professional['photo'] = image
                        return professional
                    
        return ''