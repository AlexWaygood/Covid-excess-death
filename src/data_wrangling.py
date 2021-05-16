from __future__ import annotations

from typing import Tuple
from datetime import datetime
from pandas import date_range, notna, DataFrame
import src.unchanging_constants as uc
from src import settings as st
from contextlib import suppress

"""Smattering of helper functions"""


def FilterDataForOneCountry(
        FT_data: DataFrame,
        CountryName: str
) -> DataFrame:

    return (
        FT_data
        .loc[(FT_data.country == CountryName) & (FT_data.region == CountryName)]  # Need to test both because of Georgia.
        .sort_values(uc.DATE)
        .drop_duplicates()
        .set_index(uc.DATE)
        .reindex(date_range(
            start=FT_data[uc.DATE].min(),
            end=FT_data[uc.DATE].max()
        ))
    )


def GetMinDate(df: DataFrame) -> datetime:
    return df.loc[(notna(df.excess_deaths))].index.min(skipna=True)


def GetMaxDate(df: DataFrame) -> datetime:
    return df.index.max(skipna=True)


def WrangleData(
        FT_data: DataFrame,
        CountryNames: uc.STRING_LIST
) -> Tuple[DataFrame, str]:

    data = [FilterDataForOneCountry(FT_data, CountryName) for CountryName in CountryNames]
    StartDate, EndDate = f'2020-{int(min(map(GetMinDate, data)).month):02}-01', max(map(GetMaxDate, data))

    data = DataFrame(
        {
            CountryName: ((CountrySeries[uc.EXCESS_DEATHS] / CountrySeries[uc.EXPECTED_DEATHS]) * 100)
            for CountryName, CountrySeries in zip(CountryNames, map(lambda df: df.loc[df.index >= StartDate], data))
        },
        index=date_range(start=StartDate, end=f'{EndDate.year}-{(EndDate.month + 1): 02}-01')
    )

    for method in st.INTERPOLATE_METHODS:
        with suppress(ValueError):
            return data.interpolate(method=method, limit_area=uc.INSIDE), StartDate
