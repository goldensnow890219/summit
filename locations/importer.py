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
                page.save_revision(log_action=True, user=self.user)
                # Start moderation workflow
                with suppress(ValidationError):
                    workflow = page.get_workflow()
                    workflow.start(page, self.user)

    def _get_location(self, name) -> LocationData:
        slug = slugify(name)
        if slug not in self.locations:
            location = LocationPage(slug=slug, title=name, live=False, owner=self.user)
            self.index.add_child(instance=location)
            revision = location.save_revision(log_action=True, user=self.user)
            self.locations[slug] = LocationData(json.loads(revision.content_json))
        return self.locations[slug]

    def _import_services(self, tenant_info: Dict[str, str]) -> List[int]:
        services = []
        service_names = tenant_info.get('What Services do you Specialize In?', '')
        if tenant_info.get('Do you specialize in other services? (Y/N)', 'No') == 'Yes':
            service_names += ',' + tenant_info.get('Tell us which ones here', '')
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
        image_url = tenant_info.get('Image/Logo', '').strip()
                
        f = open("image_url.txt", "w+")
        f.write(image_url)
        f.close()
        

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
        location_name = tenant_info.get('Location')
        location = self._get_location(location_name)
        
        f = open("tenant_import.txt", "w+")
        f.write(location_name)
        f.close()
        
        phone_number = tenant_info.get('Tenant Phone Number for Clients', '').strip()
        current_professional = next(
            (
                professional
                for professional in location.revision_content.get('professionals')
                if professional['phone_number'] == phone_number
            ),
            dict(pk=None, phone_number=phone_number, page=location.revision_content['pk'])
        )
        professional = deepcopy(current_professional)
        first_name = tenant_info.get('Tenant First Name', '').strip()
        last_name = tenant_info.get('Tenant Last Name', '').strip()
        professional['name'] = f'{first_name} {last_name}'.strip()
        professional['website'] = tenant_info.get('Website', '').strip()
        professional['booking_link'] = tenant_info.get('Booking Link', '').strip()
        professional['services'] = self._import_services(tenant_info)
        with suppress(Exception):
            professional['photo'] = self._import_profile_image(professional['name'], tenant_info)
        location.professionals.append(professional)
        if current_professional != professional:
            logger.info(f"Modified professional: {professional['name']}")
            location.modified = True
