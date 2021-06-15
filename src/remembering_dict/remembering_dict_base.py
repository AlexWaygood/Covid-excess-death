from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from datetime import datetime
from abc import ABC, abstractmethod
from collections import UserDict

if TYPE_CHECKING:
	from src.common_files.covid_graph_types import RememberingDictType


class AbstractRememberingDict(ABC, UserDict):
	"""
	A dict that remembers when it was created,
	and also knows how to save itself to a disk/unpickle itself from a disk.

	We have to subclass a UserDict rather than a dict itself, as ABCs don't play nicely with classes built in C.
	The UserDict subverts this problem as it's a pure-python class rather than a C class.
	"""

	def __init__(self, data: Optional[dict] = None) -> None:
		super().__init__(data if data is not None else {})
		self.LastGithubUpdate: datetime = datetime.now()

	def LastUpdateTimeReset(self) -> None:
		self.LastGithubUpdate: datetime = datetime.now()

	@abstractmethod
	def to_disk(self) -> None:
		pass

	@staticmethod
	@abstractmethod
	def from_disk() -> RememberingDictType:
		pass
