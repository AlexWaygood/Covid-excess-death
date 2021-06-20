from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, final

import src.common_files.settings as st
from src.common_files.unchanging_constants import DATAVIEWER_0_PAGE, DATAVIEWER_1_PAGE, DATAVIEWER_2_PAGE
from src.common_files.graph_plotting import GraphPlotter

if TYPE_CHECKING:
	from src.common_files.covid_graph_types import STRING_LIST


class InputBox:
	__slots__ = 'label', 'index'

	def __init__(
			self,
			index: int,
			CountryNumber: int
	) -> None:

		self.label = st.Select_Country_Message(index, CountryNumber, False)
		self.index = f'Country{index}'


# noinspection PyAttributeOutsideInit
@final
class WebGraphPlotter(GraphPlotter):
	__slots__ = 'CountryNumber', 'img', 'InputBoxes', 'TemplateForRendering', 'IncorrectEntry', 'RandomGraphSelected', \
	            'RandomGraphPermanentURL', 'url_root'

	def __init__(self) -> None:
		super().__init__(
			ReturnImage=True,
			SaveFile=False,
			InteractiveUse=False,
			GUIUsage=False
		)

	def _Reset(self) -> WebGraphPlotter:
		super()._Reset()
		self.CountryNumber = 0
		self.img = ''
		self.InputBoxes = ['']
		self.TemplateForRendering = DATAVIEWER_0_PAGE
		self.IncorrectEntry = False
		self.RandomGraphSelected = False
		self.RandomGraphPermanentURL = ''  # Only relevant if the user has asked for a random graph
		return self

	def RandomGraph(self) -> None:
		self.RandomGraphSelected = True
		countries = self.RandomCountries()

		self.RandomGraphPermanentURL = \
			f"{self.url_root}/dataviewer/?{'&'.join(f'Country{i}={country}' for i, country in enumerate(countries))}"

		self.GraphAndTitle(countries)

	# noinspection PyUnusedLocal
	def Update(
			self,
			url_root: str,
			path: str,
			Country0: str = '',
			Country1: str = '',
			Country2: str = '',
			Country3: str = '',
			Country4: str = '',
			HowManyCountries: str = '',
			**kwargs: str
	) -> WebGraphPlotter:

		if not path.startswith('/dataviewer/'):
			return self._Reset()

		self.ImageTitle = ''
		self.img = ''
		self.RandomGraphSelected = False
		self.RandomGraphPermanentURL = ''

		if Country0:
			self.CountryNumber, countries = 1, [Country0]

			for arg in (Country1, Country2, Country3, Country4):
				if not arg:
					break

				self.CountryNumber += 1
				countries.append(arg)

			self.WaitForLoad()

			if not all((c in self.CountryNames) for c in countries):
				self.TemplateForRendering = DATAVIEWER_0_PAGE
				self.CountryNumber = 0
				self.IncorrectEntry = True
				return self

			self.GraphAndTitle(countries)
			return self

		elif HowManyCountries:
			self.IncorrectEntry = False

			if HowManyCountries == 'random':
				self.url_root = url_root
				self.WaitForLoad()
				self.RandomGraphLoop()
			else:
				try:
					assert float(HowManyCountries).is_integer()
					CountryNumber = int(HowManyCountries)
					assert st.MIN_COUNTRIES <= CountryNumber <= st.MAX_COUNTRIES
					self.CountryNumber = CountryNumber
					self.TemplateForRendering = DATAVIEWER_1_PAGE
				except (ValueError, AssertionError):
					self.IncorrectEntry = True
					self.TemplateForRendering = DATAVIEWER_0_PAGE
					self.CountryNumber = 0
		else:
			self.TemplateForRendering = DATAVIEWER_0_PAGE
			self.CountryNumber = 0
			self.IncorrectEntry = False

		if self.CountryNumber:
			self.InputBoxes = [InputBox(i, self.CountryNumber) for i in range(self.CountryNumber)]
			self.WaitForLoad()
		else:
			self.InputBoxes = ['']

		return self

	def GraphAndTitle(self, countries: STRING_LIST) -> None:
		self.IncorrectEntry = False
		self.TemplateForRendering = DATAVIEWER_2_PAGE
		self.PrePlot(*countries)
		self.img = self.Plot(*countries)

	@lru_cache
	def Plot(self, *CountriesToPlot: str, **kwargs) -> str:
		return super().Plot(*CountriesToPlot)
