from __future__ import annotations

from time import sleep
from functools import lru_cache
from contextlib import suppress
from operator import itemgetter
from typing import Dict, Final, NamedTuple, TYPE_CHECKING
from pandas import read_csv, notna, offsets, date_range, DataFrame

from src.common_files.use_case import LOCAL_HOSTING
import src.common_files.unchanging_constants as uc
import src.common_files.settings as st


if LOCAL_HOSTING:
    from src.remembering_dict.remembering_dict_local import LocalRememberingDict as RememberingDict
else:
    from src.remembering_dict.remembering_dict_remote import RemoteRememberingDict as RememberingDict


if TYPE_CHECKING:
    from src.common_files.covid_graph_types import AllCountriesType


COUNTRIES_WHICH_NEED_ARTICLE: Final = ('US', 'UK', 'Netherlands', 'Czech Republic', 'Philippines')


def FetchFTData() -> DataFrame:
    """Retrieves a fresh copy of the data from the FT's Github repo."""

    return (
        read_csv(st.FT_DATA_URL, dtype=st.FT_DATA_TYPES, parse_dates=[uc.DATE, ])
        .filter(items=list(st.FT_DATA_TYPES.keys()))
        .pipe(lambda df: df.assign(period_start_date=df.date.shift(1)))
        .pipe(lambda df: df.loc[notna(df.excess_deaths) & (df.country == df.region)])
        .pipe(lambda df: df.assign(periodic_excess_deaths=((df.excess_deaths / df.expected_deaths) * 100)))
    )


class Country:
    __slots__ = 'LookupName', 'name', 'TotalExcessDeath', 'EndOfWorstPeriod', 'PeriodType', \
                'PeriodicExcessDeaths', 'RawExcessDeathsInWorstPeriod', 'StartOfWorstPeriod'

    AllCountries: AllCountriesType = RememberingDict()

    @classmethod
    def CountriesFromFile(cls) -> None:
        cls.AllCountries = cls.AllCountries.from_disk()

    @classmethod
    def CountriesFromGithub(cls, FT_data: DataFrame) -> None:
        cls.AllCountries = RememberingDict({name: Country(name, FT_data) for name in FT_data.country.unique()})
        cls.AllCountries.to_disk()

    @classmethod
    def select_countries(cls, *SelectedCountries: str) -> Dict[str, Country]:
        while not cls.AllCountries:
            sleep(0.5)

        return {
            CountryName: country
            for CountryName, country in sorted(cls.AllCountries.items(), key=itemgetter(1), reverse=True)
            if CountryName in SelectedCountries
        }

    def __init__(self, LookupName: str, FT_data: DataFrame) -> None:
        self.LookupName = LookupName
        self.name = f'the {LookupName}' if LookupName in COUNTRIES_WHICH_NEED_ARTICLE else LookupName

        df = (
            FT_data
            .loc[FT_data.country == LookupName]
            .set_index(uc.DATE)
        )

        self.TotalExcessDeath = round(df[uc.TOTAL_EXCESS_DEATHS_PCT].max())
        self.PeriodicExcessDeaths = df[uc.PERIODIC_EXCESS_DEATHS]
        self.EndOfWorstPeriod = self.PeriodicExcessDeaths.idxmax()
        self.StartOfWorstPeriod = df.loc[self.EndOfWorstPeriod, "period_start_date"].strftime("%d %B %Y")
        self.RawExcessDeathsInWorstPeriod = int(df.loc[self.EndOfWorstPeriod, uc.EXCESS_DEATHS])
        self.PeriodType = df.loc[self.EndOfWorstPeriod, uc.PERIOD]

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.LookupName

    def __lt__(self, other) -> bool:
        if not isinstance(other, Country):
            raise NotImplementedError
        return self.TotalExcessDeath < other.TotalExcessDeath

    def __gt__(self, other) -> bool:
        if not isinstance(other, Country):
            raise NotImplementedError
        return self.TotalExcessDeath > other.TotalExcessDeath

    def __eq__(self, other) -> bool:
        if not isinstance(other, Country):
            raise NotImplementedError
        return all(getattr(self, s) == getattr(other, s) for s in self.__slots__ if s != 'PeriodicExcessDeaths')

    def __hash__(self) -> int:
        return id(self)

    def title(self) -> str:
        return f'The {" ".join(self.name.split()[1:])}' if 'the' in self.name else self.name

    def SummaryStringPart1(self) -> str:
        return f'Since the date at which it reached 100 cases of COVID-19, ' \
               f'{self} has suffered {self.TotalExcessDeath}% greater mortality than would be expected ' \
               f'for the same dates in normal times.'

    def SummaryStringPart2(self) -> str:
        return f"{self.title()}'s worst point of the pandemic so far was the {self.PeriodType} beginning on" \
               f" {self.StartOfWorstPeriod}, in which the country experienced {self.RawExcessDeathsInWorstPeriod:,} " \
               f"more deaths than would be expected for that {self.PeriodType} of the year."


class DataAndDataAnalysis(NamedTuple):
    """All the info that's needed to plot a graph and produce a paragraph describing the data"""

    AnalysisPart1: str
    AnalysisPart2: str
    AnalysisPart3: str
    Title: str
    StartDate: str
    EndDate: str
    PlottableData: DataFrame


@lru_cache
def PlottableData(*countries: str) -> DataAndDataAnalysis:
    """
    Plug in some country names, and this function spits out the data in a form that can be plotted,
    plus some text strings that can be concatenated to make a coherent analysis of the data
    """

    data = Country.select_countries(*countries)
    Message1, Message2, Message3, Title = GetMessage(*data.values())
    data = {country.LookupName: country.PeriodicExcessDeaths for CountryName, country in data.items()}
    StartDate = f'2020-{min(x.index.min() for x in data.values()).month}-01'

    EndDate = (
        (max(x.index.max() for x in data.values()) + offsets.MonthBegin(1))
        .strftime(uc.FT_DATETIME_FORMAT)
    )

    data = DataFrame(data, index=date_range(start=StartDate, end=EndDate))

    for method in st.INTERPOLATE_METHODS:
        with suppress(ValueError):
            interpolated_data = data.interpolate(method=method, limit_area=uc.INSIDE)
            break

    return DataAndDataAnalysis(
        Message1,
        Message2,
        Message3,
        Title,
        StartDate,
        EndDate,
        interpolated_data
    )


class DataAnalysisMessage(NamedTuple):
    Part1: str
    Part2: str
    Part3: str
    Title: str


@lru_cache
def GetMessage(*Countries: Country) -> DataAnalysisMessage:
    """Plug in some countries, get out some strings that can be concatenated to make a coherent analysis of the data."""

    Country0, Len = Countries[0], len(Countries)

    Title_Countries = f'{Country0}' if Len == 1 else f'{", ".join(map(str, Countries[:-1]))} and {Countries[-1]}'
    Title = f'Pandemic excess deaths in {Title_Countries}'

    if Len == 1:
        Seg2 = ''

    elif Len == 2:
        Country1 = Countries[1]
        Seg2 = f'{Country1.title()}, by comparison, has had an excess death rate of {Country1.TotalExcessDeath}%.'

    elif Len == 3:
        Country1, Country2 = Countries[1:]

        Seg2 = f'{Country1.title()} and {Country2} have had excess mortality rates of ' \
               f'{Country1.TotalExcessDeath}% and {Country2.TotalExcessDeath}% respectively.'

    elif Len == 4:
        Country1, Country2, Country3 = Countries[1:]

        Seg2 = f'{Country1.title()}, {Country2} and {Country3} have had excess mortality rates of ' \
               f'{Country1.TotalExcessDeath}%, {Country2.TotalExcessDeath}% ' \
               f'and {Country3.TotalExcessDeath}%, respectively.'

    else:
        Country1, Country2, Country3, Country4 = Countries[1:]

        Seg2 = f'{Country1.title()}, {Country2}, {Country3} and {Country4} have had excess mortality rates of ' \
               f'{Country1.TotalExcessDeath}%, {Country2.TotalExcessDeath}%, {Country3.TotalExcessDeath}% ' \
               f'and {Country4.TotalExcessDeath}%, respectively.'

    return DataAnalysisMessage(Country0.SummaryStringPart1(), Seg2, Country0.SummaryStringPart2(), Title)
