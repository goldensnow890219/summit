import io
import logging
from uuid import uuid4

import rollbar
from django.conf import settings

from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload


logger = logging.getLogger(__name__)

# If modifying these scopes, delete the content of `` SystemVali.
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.readonly',
]


class GDrive:
    def __init__(self, credentials):
        self.service = build('drive', 'v3', credentials=credentials)

    @staticmethod
    def create_credentials(path, response_url, state):
        flow = Flow.from_client_config(
            settings.GOOGLE_API_CLIENT_CONFIG, scopes=SCOPES, state=state
        )
        flow.redirect_uri = settings.BASE_URL + path
        flow.fetch_token(authorization_response=response_url)

        return flow.credentials

    @staticmethod
    def create_auth_url(path):
        # If there are no credentials available, let the user log in.
        flow = Flow.from_client_config(settings.GOOGLE_API_CLIENT_CONFIG, SCOPES)
        # Indicate where the API server will redirect the user after the user completes
        # the authorization flow. The redirect URI is required. The value must exactly
        # match one of the authorized redirect URIs for the OAuth 2.0 client, which you
        # configured in the API Console. If this value doesn't match an authorized URI,
        # you will get a 'redirect_uri_mismatch' error.
        flow.redirect_uri = settings.BASE_URL + path
        # Generate URL for request to Google's OAuth 2.0 server.
        # Use kwargs to set optional request parameters.
        return flow.authorization_url(
            # Enable offline access so that you can refresh an access token without
            # re-prompting the user for permission. Recommended for web server apps.
            access_type='offline',
            # Enable incremental authorization. Recommended as a best practice.
            include_granted_scopes='true',
            state=str(uuid4()),
        )

    def list_files(self, page_size=10, page_token=None):
        params = {'pageSize': page_size, 'fields': 'nextPageToken, files(id, name)'}
        if page_token:
            params['pageToken'] = page_token
        # Call the Drive v3 API
        results = self.service.files().list(**params).execute()
        next_page_token = results.get('nextPageToken')
        files = results.get('files')
        return files, next_page_token

    def get_file_meta(self, file_id):
        return self.service.files().get(fileId=file_id, fields='id, modifiedTime').execute()

    def get_file_content(self, file_id, mime_type):
        request = self.service.files().export_media(fileId=file_id, mimeType=mime_type)
        file_handler = io.BytesIO()
        downloader = MediaIoBaseDownload(file_handler, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        file_handler.seek(0)
        return file_handler

    def watch_file(self, file_id, webhook_url):
        body = {
            "id": str(uuid4()),
            "type": "web_hook",
            "address": webhook_url
        }
        rollbar.report_message(
            'Registering file watch', 'info', extra_data={'fileId': file_id, **body}
        )
        return self.service.files().watch(fileId=file_id, body=body).execute()
