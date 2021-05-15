from __future__ import annotations

from typing import Tuple
from datetime import datetime
from pandas import date_range, notna, DataFrame
import src.unchanging_constants as uc
from src import settings as st

"""Smattering of helper functions"""


def FilterDataForOneCountry(
        FT_data: DataFrame,
        CountryName: str
) -> DataFrame:

    return (
        FT_data
        .loc[FT_data.region == CountryName]
        .sort_values(uc.DATE)
        .drop_duplicates()
        .set_index(uc.DATE)
        .reindex(date_range(
            start=FT_data[uc.DATE].min(),
            end=FT_data[uc.DATE].max()
        ))
    )


def GetMinMonth(df: DataFrame) -> int:
    return (
        df
        .loc[(notna(df.excess_deaths)) & (df.index < datetime.strptime(uc.JAN_01_2021, uc.FT_DATETIME_FORMAT))]
        .index
        .month
        .min(skipna=True)
        )


def WrangleData(
        FT_data: DataFrame,
        CountryNames: uc.STRING_LIST
) -> Tuple[DataFrame, str]:

    data = (
        FT_data
        .loc[(2019 < FT_data.year) & (FT_data.date <= st.END_DATE)]
        .assign(excess_weekly_pct=lambda x: ((x.excess_deaths / x.expected_deaths) * 100))
        )

    data = [FilterDataForOneCountry(data, CountryName) for CountryName in CountryNames]
    StartDate = f'2020-{int(min(map(GetMinMonth, data))):02}-01'
    data = [CountrySeries.loc[CountrySeries.index >= StartDate] for CountrySeries in data]

    data = {
        CountryName: CountrySeries[uc.EXCESS_WEEKLY_PCT]
        for CountryName, CountrySeries in zip(CountryNames, data)
    }

    return (
        DataFrame(data, index=date_range(start=StartDate, end=st.END_DATE))
        .interpolate(method=st.INTERPOLATE_METHOD, limit_area=uc.INSIDE)
    ), StartDate
