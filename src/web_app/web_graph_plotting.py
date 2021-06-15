from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, final

import src.common_files.settings as st
from src.common_files.unchanging_constants import DATAVIEWER_0_PAGE, DATAVIEWER_1_PAGE, DATAVIEWER_2_PAGE
from src.common_files.graph_plotting import GraphPlotter

if TYPE_CHECKING:
	from src.common_files.covid_graph_types import STRING_LIST
	from flask import Request


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
	__slots__ = 'CountryNumber', 'img', 'InputBoxes', 'TemplateForRendering', '_IncorrectEntry', 'RandomGraphSelected', \
	            'RandomGraphPermanentURL'

	def __init__(self) -> None:
		super().__init__(
			ReturnImage=True,
			SaveFile=False,
			InteractiveUse=False,
			GUIUsage=False
		)

	def Reset(self) -> WebGraphPlotter:
		super().Reset()
		self.CountryNumber = 0
		self.img = ''
		self.InputBoxes = ['']
		self.TemplateForRendering = DATAVIEWER_0_PAGE
		self.IncorrectEntry = False
		self.RandomGraphSelected = False
		self.RandomGraphPermanentURL = ''  # Only relevant if the user has asked for a random graph
		return self

	@property
	def IncorrectEntry(self) -> bool:
		IncorrectEntry = self._IncorrectEntry
		self._IncorrectEntry = False
		return IncorrectEntry

	@IncorrectEntry.setter
	def IncorrectEntry(self, value: bool) -> None:
		self._IncorrectEntry = value

	def RandomGraph(self, url_root: str) -> None:
		self.RandomGraphSelected = True
		countries = self.RandomCountries()

		self.RandomGraphPermanentURL = ''.join((
			url_root,
			'/dataviewer/?',
			'&'.join(f'Country{i}={country}' for i, country in enumerate(countries))
		))

		self.GraphAndTitle(countries)

	def Update(self, request_context: Request) -> WebGraphPlotter:
		self.ImageTitle = ''
		self.img = ''
		self.RandomGraphSelected = False
		self.RandomGraphPermanentURL = ''

		if Country0 := request_context.args.get('Country0'):
			self.CountryNumber, countries = 1, [Country0]

			while (
					self.CountryNumber < st.MAX_COUNTRIES
					and bool(country := (request_context.args.get(f'Country{self.CountryNumber}')))
			):
				self.CountryNumber += 1
				# noinspection PyUnboundLocalVariable
				countries.append(country)

			self.WaitForLoad()

			if not all((c in self.CountryNames) for c in countries):
				self.TemplateForRendering = DATAVIEWER_0_PAGE
				self.CountryNumber = 0
				self.IncorrectEntry = True
				return self

			self.GraphAndTitle(countries)
			return self

		elif CountryNumber := request_context.args.get('HowManyCountries'):
			self.IncorrectEntry = False

			if CountryNumber == 'random':
				self.WaitForLoad()
				self.RandomGraphLoop(url_root=request_context.url_root)
			else:
				try:
					assert float(CountryNumber).is_integer()
					CountryNumber = int(CountryNumber)
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
