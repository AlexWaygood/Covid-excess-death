from google.oauth2.service_account import Credentials as GoogleCredentials
from typing import Final
from os import path

PATH_TO_CREDENTIALS: Final = path.join('src', 'web_app', 'google-auth-credentials.json')
CREDENTIALS = GoogleCredentials.from_service_account_file(PATH_TO_CREDENTIALS)
SCOPED_CREDENTIALS = CREDENTIALS.with_scopes(['https://www.googleapis.com/auth/cloud-platform'])
