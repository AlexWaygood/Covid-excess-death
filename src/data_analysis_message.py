from __future__ import annotations

from typing import TYPE_CHECKING, Tuple
import src.settings as st
from src.unchanging_constants import TOTAL_EXCESS_DEATHS_PCT, DATE, STRING_LIST

if TYPE_CHECKING:
	from pandas import DataFrame


class Country:
	__slots__ = 'LookupName', 'name', 'ExcessDeath'

	def __init__(
			self,
			name: str,
			FT_data: DataFrame
	) -> None:

		self.LookupName = name
		self.name = st.AddArticle(name)
		self.ExcessDeath = round(FT_data.loc[FT_data.region == name][TOTAL_EXCESS_DEATHS_PCT].max())

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


def GetMessage(
		FT_data: DataFrame,
		Countries: STRING_LIST
) -> Tuple[str, str, str]:

	Countries = sorted([Country(c, FT_data) for c in Countries], reverse=True)
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
	StartOfWorstWeek = FT_data.loc[(EndOfWorstWeekID - 1), DATE].strftime('%d %B %Y')
	WorstExcessDeaths = int(FT_data.loc[EndOfWorstWeekID, 'excess_deaths'])

	Seg3 = f"{Country0.title()}'s worst week of the pandemic so far was week beginning {StartOfWorstWeek}, " \
	       f"in which the country experienced {WorstExcessDeaths:,} more deaths than would be expected" \
	       f" for that week of the year."

	return Seg1, Seg2, Seg3
