from __future__ import annotations

import pickle

from typing import TYPE_CHECKING, Final

from google.cloud.storage import Client as GoogleClient
from src.web_app.google_credentials import SCOPED_CREDENTIALS

from src.common_files.secret_passwords import GOOGLE_CLOUD_BUCKET_ID
from src.remembering_dict.remembering_dict_base import AbstractRememberingDict

if TYPE_CHECKING:
	from google.cloud.storage.blob import Blob


FILE_PATH: Final = 'static/FT_data.pickle'
GOOGLE_CLOUD_CLIENT = GoogleClient(credentials=SCOPED_CREDENTIALS)
GOOGLE_CLOUD_BUCKET = GOOGLE_CLOUD_CLIENT.get_bucket(GOOGLE_CLOUD_BUCKET_ID)


def GetGoogleBlob() -> Blob:
	return GOOGLE_CLOUD_BUCKET.get_blob(FILE_PATH)


class RemoteRememberingDict(AbstractRememberingDict):
	def to_disk(self) -> None:
		"""I retrieve a copy of the FT's dataset from a Google Cloud Storage account"""

		GetGoogleBlob().upload_from_string(pickle.dumps(self))

	@staticmethod
	def from_disk() -> RemoteRememberingDict:
		"""I upload a copy of the FT's dataset to a Google Cloud Storage account"""

		return pickle.loads(GetGoogleBlob().download_as_bytes())
