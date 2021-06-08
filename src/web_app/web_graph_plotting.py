from __future__ import annotations
from src.common_files import use_case

use_case.WEB_MODE = True

from functools import lru_cache
from flask import request
from typing import TYPE_CHECKING, final

import src.common_files.settings as st
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
	__slots__ = 'CountryNumber', 'img', 'InputBoxes', 'GraphStage', '_IncorrectEntry'

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
		self.GraphStage = 0
		self._IncorrectEntry = False
		return self

	@property
	def IncorrectEntry(self) -> bool:
		IncorrectEntry = self._IncorrectEntry
		self._IncorrectEntry = False
		return IncorrectEntry

	@IncorrectEntry.setter
	def IncorrectEntry(self, value: bool) -> None:
		self._IncorrectEntry = value

	def RandomGraph(self) -> None:
		self.GraphAndTitle(self.RandomCountries())

	def Update(self, FromRedirect: bool) -> WebGraphPlotter:
		if FromRedirect:
			return self

		self.ImageTitle = ''
		self.img = ''

		if Country0 := request.args.get('Country0'):
			self.CountryNumber, countries = 1, [Country0]

			while (
					self.CountryNumber < st.MAX_COUNTRIES
					and bool(country := (request.args.get(f'Country{self.CountryNumber}')))
			):
				self.CountryNumber += 1
				# noinspection PyUnboundLocalVariable
				countries.append(country)

			self.WaitForLoad()

			if not all((c in self.CountryNames()) for c in countries):
				self.GraphStage = 0
				self.CountryNumber = 0
				self.IncorrectEntry = True
				return self

			self.GraphAndTitle(countries)
			return self

		elif CountryNumber := request.args.get('HowManyCountries'):
			self.IncorrectEntry = False

			if CountryNumber == 'random':
				self.WaitForLoad()
				self.RandomGraphLoop()
			else:
				try:
					assert float(CountryNumber).is_integer()
					CountryNumber = int(CountryNumber)
					assert st.MIN_COUNTRIES <= CountryNumber <= st.MAX_COUNTRIES
					self.CountryNumber = CountryNumber
					self.GraphStage = 1
				except (ValueError, AssertionError):
					self.IncorrectEntry = True
					self.GraphStage = 0
					self.CountryNumber = 0
		else:
			self.GraphStage = 0
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
		self.GraphStage = 2
		self.PrePlot(*countries)
		self.img = self.Plot(*countries)

	@lru_cache
	def Plot(self, *CountriesToPlot, **kwargs) -> str:
		return super().Plot(*CountriesToPlot)
