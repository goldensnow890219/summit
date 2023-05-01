import csv
import io
import logging
from datetime import datetime, timezone

from django.core.management import CommandError
from django.core.management.base import BaseCommand
from django.urls import reverse
from google_auth_httplib2 import Request

from core.gdrive import GDrive
from core.models import SystemVariable
from locations.importer import TenantImporter

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Add google drive file watcher'

    INFO_MESSAGE = f"Tenant file is not setup yet. Go to {reverse('google-api-files')} fix this."

    def handle(self, *args, **options):
        previous_file_info = SystemVariable.get('tenant_file_info')
        if not previous_file_info:
            logger.info(self.INFO_MESSAGE)
            raise CommandError('Configuration missing: Tenant file not found')

        gd = GDrive(self.get_credential())
        file_info = gd.get_file_meta(previous_file_info.get('id'))
        modified_time = datetime.fromisoformat(file_info.get('modifiedTime').replace('Z', '+00:00'))
        imported_time = datetime.fromisoformat(previous_file_info.get('importedTime'))
        f = open("professional_checking.txt", "w+")
        f.write(imported_time.strftime("%m/%d/%Y, %H:%M:%S"))
        f.close()
        #if imported_time < modified_time:
        file_info['importedTime'] = datetime.now(tz=timezone.utc).isoformat()
        with gd.get_file_content(file_info.get('id'), 'text/csv') as file_content:
            csv_file = io.StringIO(file_content.read().decode('UTF-8'))
            reader = csv.DictReader(csv_file)
            with TenantImporter() as importer:
                for tenant_info in reader:
                    importer.import_info(**tenant_info)
            csv_file.close()
        SystemVariable.set('tenant_file_info', file_info)

    @staticmethod
    def get_credential():
        token = SystemVariable.get('google_api_token')
        if not token:
            raise CommandError('Configuration missing: Google API token not found')
        else:
            credentials, state = token
        if not credentials.valid:
            if credentials.expired and credentials.refresh_token:
                #credentials.refresh(Request())
                SystemVariable.set('google_api_token', (credentials, state))
            else:
                logger.error("Invalid Google credentials state")
                raise CommandError("Invalid Google credentials state")

        return credentials
