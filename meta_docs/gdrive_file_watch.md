# Instructions to register a file to receive changes notifications
[More details](https://developers.google.com/drive/api/v3/push#registering-your-domain)
 
1. Register your domain in the [Search Console](https://www.google.com/webmasters/tools).

   Get the google-site-verification token and add it as an env variable named GOOGLE_SITE_VERIFICATION to your
   project. It will be served add automatically as a head meta to the site.

1. Create a project in the [Google API Console](https://console.developers.google.com/projectcreate)

1. Add your [domain as verified](https://console.developers.google.com/apis/credentials/domainverification) to your project.

1. Enable the [Google Drive API](https://console.developers.google.com/apis/library/drive.googleapis.com) for your project.

1. Create [Web App credential](https://console.developers.google.com/apis/credentials/oauthclient) to connect to the app from a management command.

    Download the `client.json` file and copy the content to the `GOOGLE_API_CLIENT_CONFIG` environment variable.

    Note: If your are running in your local just copy the file in the root of the project.

1. Go to the admin to gran access to your Google Drive and pick the Tenant file.
    
    In the admin go to `Settings` -> `Tenant File`

1. Register a cron job to run the `tenant_file_watcher` management command every 10 minutes.
   
   ```
   python manage.py tenant_file_watcher
   ```