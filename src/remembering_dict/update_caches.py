from __future__ import annotations

from src.remembering_dict.remembering_dict_remote import RemoteRememberingDict
from src.remembering_dict.remembering_dict_local import LocalRememberingDict
from src.common_files import data_wrangling
from typing import Union, Type


DEBUGGING = False


def update_cache(cls: Union[Type[RemoteRememberingDict], Type[LocalRememberingDict]]) -> None:
	data_wrangling.RememberingDict = cls

	if DEBUGGING:
		print(f'data_wrangling class is {data_wrangling.RememberingDict}')
	else:
		data_wrangling.Country.CountriesFromGithub(data_wrangling.FetchFTData())


def update_both_caches() -> None:
	update_cache(LocalRememberingDict)
	update_cache(RemoteRememberingDict)


if __name__ == '__main__':
	update_both_caches()
