from __future__ import annotations

import pickle
from functools import lru_cache
from datetime import datetime
from contextlib import suppress
from operator import itemgetter
from typing import Tuple, Dict, Optional, Final, TYPE_CHECKING
from pandas import read_csv, notna, offsets, date_range, DataFrame

from src.common_files.use_case import LOCAL_HOSTING
import src.common_files.unchanging_constants as uc
import src.common_files.settings as st

if TYPE_CHECKING:
    from src.common_files.covid_graph_types import TWO_CALLABLES

COUNTRIES_WHICH_NEED_ARTICLE: Final = ('US', 'UK', 'Netherlands', 'Czech Republic', 'Philippines')


def GetFuncs() -> TWO_CALLABLES:

    # If we're running it on the Flask development server,
    # we need the RememberingDict class to be implemented with the following functions

    if LOCAL_HOSTING:
        from os import path
        FILE_PATH: Final = path.join('static', 'FT_data.pickle')

        def to_file(self: RememberingDict) -> None:
            with open(FILE_PATH, 'wb') as f:
                pickle.dump(self, f)

        # noinspection PyUnusedLocal
        def from_file(self: RememberingDict) -> RememberingDict:
            with open(FILE_PATH, 'rb') as f:
                LatestDataset: RememberingDict = pickle.load(f)
            return LatestDataset

        return to_file, from_file

    # If it's being run on Google's servers, we want the implementation to have these functions instead.

    else:
        from google.cloud.storage import Client as GoogleClient
        from google.oauth2.service_account import Credentials as GoogleCredentials
        from src.common_files.secret_passwords import GOOGLE_CLOUD_BUCKET_ID

        if TYPE_CHECKING:
            from google.cloud.storage.blob import Blob

        PATH_TO_CREDENTIALS: Final = 'google-auth-credentials.json'
        FILE_PATH: Final = 'static/FT_data.pickle'

        CREDENTIALS = GoogleCredentials.from_service_account_file(PATH_TO_CREDENTIALS)
        SCOPED_CREDENTIALS = CREDENTIALS.with_scopes(['https://www.googleapis.com/auth/cloud-platform'])
        GOOGLE_CLOUD_CLIENT = GoogleClient(credentials=SCOPED_CREDENTIALS)
        GOOGLE_CLOUD_BUCKET = GOOGLE_CLOUD_CLIENT.get_bucket(GOOGLE_CLOUD_BUCKET_ID)

        def GetGoogleBlob() -> Blob:
            return GOOGLE_CLOUD_BUCKET.get_blob(FILE_PATH)

        def to_cloud(self: RememberingDict) -> None:
            from io import BytesIO
            file = BytesIO()
            pickle.dump(self, file)
            file.seek(0)
            GetGoogleBlob().upload_from_file(file)

        # noinspection PyUnusedLocal
        def from_cloud(self: RememberingDict) -> RememberingDict:
            return pickle.loads(GetGoogleBlob().download_as_bytes())

        return to_cloud, from_cloud


class RememberingDict(dict):
    to_disk, from_disk = GetFuncs()

    def __init__(self, data: Optional[dict] = None) -> None:

        super().__init__(data if data is not None else {})
        self.LastGithubUpdate: datetime = datetime.now()

    def LastUpdateTimeReset(self) -> None:
        self.LastGithubUpdate: datetime = datetime.now()


def FetchFTData() -> DataFrame:
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

    AllCountries: RememberingDict[str, Country] = RememberingDict()

    @classmethod
    def CountriesFromFile(cls) -> None:
        # noinspection PyArgumentList
        cls.AllCountries = cls.AllCountries.from_disk()

    @classmethod
    def CountriesFromGithub(cls, FT_data: DataFrame) -> None:
        cls.AllCountries = RememberingDict({name: Country(name, FT_data) for name in FT_data.country.unique()})
        # noinspection PyArgumentList
        cls.AllCountries.to_disk()

    @classmethod
    def select_countries(cls, *SelectedCountries: str) -> Dict[str, Country]:
        return {
            CountryName: country
            for CountryName, country in sorted(cls.AllCountries.items(), key=itemgetter(1), reverse=True)
            if CountryName in SelectedCountries
        }

    def __init__(self, name: str, FT_data: DataFrame) -> None:
        self.LookupName = name
        self.name = f'the {name}' if name in COUNTRIES_WHICH_NEED_ARTICLE else name

        df = (
            FT_data
            .loc[FT_data.country == name]
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


@lru_cache
def PlottableData(*countries: str):
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
            return Message1, Message2, Message3, Title, StartDate, EndDate,\
                   data.interpolate(method=method, limit_area=uc.INSIDE)


@lru_cache
def GetMessage(*Countries: Country) -> Tuple[str, str, str, str]:
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

    return Country0.SummaryStringPart1(), Seg2, Country0.SummaryStringPart2(), Title
