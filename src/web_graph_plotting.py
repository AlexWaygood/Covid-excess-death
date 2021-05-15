from typing import TypeVar
import src.settings as st
from src.graph_plotting import GraphPlotter, PlotAsGraph
from src.unchanging_constants import STRING_LIST, TOTAL_EXCESS_DEATHS_PCT
from src.data_analysis_message import GetMessage
from flask import request
from time import sleep
from threading import Thread


T = TypeVar('T')


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
class WebGraphPlotter(GraphPlotter):
	__slots__ = 'CountryNumber', 'img', 'ImageTitle', 'InputBoxes', 'GraphStage', 'Message1', 'Message2', 'Message3', \
	            '_IncorrectEntry', 'Initialised'

	# noinspection PyMissingConstructor
	def __init__(self) -> None:
		self.Reset()
		self.Initialised = False
		Thread(target=self.Initialise).start()

	def Reset(self: T) -> T:
		self.CountryNumber = 0
		self.img = ''
		self.ImageTitle = ''
		self.InputBoxes = ['']
		self.GraphStage = 0
		self.Message1 = ''
		self.Message2 = ''
		self.Message3 = ''
		self._IncorrectEntry = False
		return self

	def Initialise(self) -> None:
		super().__init__()
		self.Initialised = True

	@property
	def IncorrectEntry(self) -> bool:
		IncorrectEntry = self._IncorrectEntry
		self._IncorrectEntry = False
		return IncorrectEntry

	@IncorrectEntry.setter
	def IncorrectEntry(self, value: bool) -> None:
		self._IncorrectEntry = value

	def WaitForData(self) -> None:
		while not self.Initialised:
			sleep(0.1)

	def RandomGraph(self) -> None:
		self.GraphAndTitle(self.RandomCountries())

	def Update(
			self: T,
			FromRedirect: bool
	) -> T:

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

			self.WaitForData()

			if not all((c in self.FT_Countries) for c in countries):
				self.GraphStage = 0
				self.CountryNumber = 0
				self.IncorrectEntry = True
				return None

			self.GraphAndTitle(countries)

		elif CountryNumber := request.args.get('HowManyCountries'):
			self.IncorrectEntry = False

			if CountryNumber == 'random':
				self.WaitForData()
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
			self.WaitForData()
		else:
			self.InputBoxes = ['']

		return self

	def GraphAndTitle(self, countries: STRING_LIST) -> None:
		self.IncorrectEntry = False
		self.GraphStage = 2
		self.ImageTitle = st.GraphTitle(countries)
		self.img = PlotAsGraph(self.FT_data, countries, Title=self.ImageTitle, ReturnImage=True)
		self.Message1, self.Message2, self.Message3 = GetMessage(self.FT_data, countries)

	def TotalExcessDeaths(self, country: str) -> float:
		return self.FT_data.loc[self.FT_data.region == country][TOTAL_EXCESS_DEATHS_PCT].max()
