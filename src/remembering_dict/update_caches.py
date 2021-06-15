from src.remembering_dict.remembering_dict_remote import RemoteRememberingDict
from src.remembering_dict.remembering_dict_local import LocalRememberingDict
from src.common_files import data_wrangling


def update_cache(cls, debugging: bool = False) -> None:
	data_wrangling.RememberingDict = cls

	if debugging:
		print(f'data_wrangling class is {data_wrangling.RememberingDict}')
	else:
		data_wrangling.Country.CountriesFromGithub(data_wrangling.FetchFTData())


def update_both_caches(debugging: bool = False) -> None:
	update_cache(LocalRememberingDict, debugging)
	update_cache(RemoteRememberingDict, debugging)
