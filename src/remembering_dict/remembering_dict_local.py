from __future__ import annotations

import pickle

from os import path
from typing import Final

from src.remembering_dict.remembering_dict_base import AbstractRememberingDict


FILE_PATH: Final = path.join('static', 'FT_data.pickle')


class LocalRememberingDict(AbstractRememberingDict):
	def to_disk(self) -> None:
		"""I retrieve a local copy of the FT's dataset from where it's saved on a hard-drive"""

		with open(FILE_PATH, 'wb') as f:
			pickle.dump(self, f)

	@staticmethod
	def from_disk() -> LocalRememberingDict:
		"""I save a local copy of the FT's dataset to a hard-drive"""

		with open(FILE_PATH, 'rb') as f:
			LatestDataset: LocalRememberingDict = pickle.load(f)
		return LatestDataset
