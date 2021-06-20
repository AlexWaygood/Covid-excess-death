from typing import TYPE_CHECKING, TypeVar, Optional, List, Sequence, Tuple, Union

assert TYPE_CHECKING, "Can't import this module at runtime!"

from src.common_files.data_wrangling import Country
from src.common_files.graph_plotting import GraphPlotter
from src.remembering_dict.remembering_dict_remote import RemoteRememberingDict
from src.remembering_dict.remembering_dict_local import LocalRememberingDict

from pandas import DataFrame

GraphPlotterTypeVar = TypeVar('GraphPlotterTypeVar', bound=GraphPlotter)
RememberingDictType = Union[RemoteRememberingDict, LocalRememberingDict]
AllCountriesType = Union[RemoteRememberingDict[str, Country], LocalRememberingDict[str, Country]]

OPTIONAL_STR = Optional[str]
STRING_LIST = List[str]
STRING_SEQUENCE = Sequence[str]
DATA_FRAME_LIST = List[DataFrame]
IMAGE_AND_TITLE = Tuple[str, str]
PAGE_AND_ERROR_CODE = Tuple[str, int]
