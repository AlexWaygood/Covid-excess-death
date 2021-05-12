from __future__ import annotations

from typing import TYPE_CHECKING, List, TypeVar, Tuple
import src.settings as st
from src.graph_plotting import GraphPlotter, PlotAsGraph
from src.unchanging_constants import STRING_LIST
from random import randint, sample as random_sample
from flask import request
from time import sleep

if TYPE_CHECKING:
	from pandas import DataFrame


T = TypeVar('T')


class Country:
	__slots__ = 'LookupName', 'name', 'ExcessDeath'

	def __init__(
			self,
			name: str,
			FT_data: DataFrame
	) -> None:

		self.LookupName = name
		self.name = st.AddArticle(name)
		self.ExcessDeath = round(FT_data.loc[FT_data.region == name]['total_excess_deaths_pct'].max())

	def __str__(self) -> str:
		return self.name

	def __repr__(self) -> str:
		return self.LookupName

	def __lt__(self, other) -> bool:
		return self.ExcessDeath < other.ExcessDeath

	def __gt__(self, other) -> bool:
		return self.ExcessDeath > other.ExcessDeath

	def title(self) -> str:
		return f'The {" ".join(self.name.split()[1:])}' if 'the' in self.name else self.name


def ExtractDateFromIndex(
		FT_data: DataFrame,
		index: int
) -> str:

	return FT_data.loc[index, 'date'].strftime('%d %B %Y')


def GetMessage(
		FT_data: DataFrame,
		Countries: List[Country]
) -> Tuple[str, str, str]:

	Countries.sort(reverse=True)
	Country0, Len = Countries[0], len(Countries)

	Seg1 = f'Since the date at which it reached 100 cases of COVID-19, ' \
	           f'{Country0} has suffered {Country0.ExcessDeath}% greater mortality than would be expected ' \
	           f'for the same dates in normal times.'

	if Len == 1:
		Seg2 = ''

	elif Len == 2:
		Country1 = Countries[1]
		Seg2 = f'{Country1.title()}, by comparison, has had an excess death rate of {Country1.ExcessDeath}%.'

	elif Len == 3:
		Country1, Country2 = Countries[1:3]

		Seg2 = f'{Country1.title()} and {Country2} have had excess mortality rates of ' \
		       f'{Country1.ExcessDeath}% and {Country2.ExcessDeath}% respectively.'

	elif Len == 4:
		Country1, Country2, Country3 = Countries[1:]

		Seg2 = f'{Country1.title()}, {Country2} and {Country3} have had excess mortality rates of ' \
		       f'{Country1.ExcessDeath}%, {Country2.ExcessDeath}% and {Country3.ExcessDeath}%, respectively.'

	else:
		Country1, Country2, Country3, Country4 = Countries[1:]

		Seg2 = f'{Country1.title()}, {Country2}, {Country3} and {Country4} have had excess mortality rates of ' \
		       f'{Country1.ExcessDeath}%, {Country2.ExcessDeath}%, {Country3.ExcessDeath}% and {Country4.ExcessDeath}%, ' \
		       f'respectively.'

	EndOfWorstWeekID = FT_data.loc[FT_data.region == repr(Country0), 'excess_deaths'].idxmax()
	StartOfWorstWeek = ExtractDateFromIndex(FT_data, (EndOfWorstWeekID - 1))
	WorstExcessDeaths = int(FT_data.loc[EndOfWorstWeekID, 'excess_deaths'])

	Seg3 = f"{Country0.title()}'s worst week of the pandemic so far was week beginning {StartOfWorstWeek}, " \
	       f"in which the country experienced {WorstExcessDeaths:,} more deaths than would be expected" \
	       f" for that week of the year."

	return Seg1, Seg2, Seg3


ORDINALS = ('first', 'second', 'third', 'fourth', 'fifth')


class InputBox:
	__slots__ = 'label', 'index'

	def __init__(
			self,
			index: int,
			CountryNumber: int
	) -> None:

		if CountryNumber > 1:
			self.label = f'Please select the {ORDINALS[index]} country you would like to compare'
		else:
			self.label = 'Please select which country you would like to graph'

		self.index = f'Country{index}'


class WebGraphPlotter(GraphPlotter):
	__slots__ = 'CountryNumber', 'img', 'ImageTitle', 'InputBoxes', 'GraphStage', 'Message1', 'Message2', 'Message3', \
	            '_IncorrectEntry', 'Initialised'

	# noinspection PyMissingConstructor
	def __init__(self) -> None:
		self.CountryNumber = 0
		self.img = ''
		self.ImageTitle = ''
		self.InputBoxes = ['']
		self.GraphStage = 0
		self.Message1 = ''
		self.Message2 = ''
		self.Message3 = ''
		self._IncorrectEntry = False
		self.Initialised = False

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

	def Reset(self: T) -> T:
		self.__init__()
		self.Initialised = True
		return self

	def Update(
			self: T,
			FromRedirect: bool
	) -> T:

		while not self.Initialised:
			sleep(0.1)

		if FromRedirect:
			return self

		self.ImageTitle = ''
		self.img = ''

		if request.args.get('Country0'):
			self.CountryNumber = 1

			while self.CountryNumber < 5 and bool(request.args.get(f'Country{self.CountryNumber}')):
				self.CountryNumber += 1

			countries = [request.args.get(f'Country{i}') for i in range(self.CountryNumber)]

			if not all((c in self.FT_Countries) for c in countries):
				self.GraphStage = 0
				self.CountryNumber = 0
				self.IncorrectEntry = True
				return None

			self.GraphAndTitle(countries)

		elif CountryNumber := request.args.get('HowManyCountries'):
			self.IncorrectEntry = False

			if CountryNumber == 'random':
				while True:
					# noinspection PyBroadException
					try:
						self.GraphAndTitle(random_sample(self.FT_Countries, randint(1, 5)))
						break
					except:
						pass
			else:
				try:
					assert float(CountryNumber).is_integer()
					CountryNumber = int(CountryNumber)
					assert 0 < CountryNumber < 6
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
		else:
			self.InputBoxes = ['']

		return self

	def GraphAndTitle(self, countries: STRING_LIST) -> None:
		self.IncorrectEntry = False
		self.GraphStage = 2
		self.ImageTitle = st.GraphTitle(countries)
		self.img = PlotAsGraph(self.FT_data, countries, Title=self.ImageTitle, ReturnImage=True)

		self.Message1, self.Message2, self.Message3 = GetMessage(
			self.FT_data,
			[Country(c, self.FT_data) for c in countries]
		)

	def TotalExcessDeaths(self, country: str) -> float:
		return self.FT_data.loc[self.FT_data.region == country]['total_excess_deaths_pct'].max()
