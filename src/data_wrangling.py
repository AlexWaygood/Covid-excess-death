from __future__ import annotations

from operator import methodcaller
from typing import Tuple
from pandas import read_csv, date_range, notna, DataFrame, offsets
import src.unchanging_constants as uc
from src import settings as st
from contextlib import suppress

"""Smattering of helper functions"""


def CountryHasExcessDeathEstimates(FT_data: DataFrame, CountryName: str) -> bool:
    return not FT_data.loc[
        (FT_data.region == CountryName)
        & (FT_data.country == CountryName)
        & notna(FT_data.expected_deaths)
        ].empty


def FTDataAndCountries() -> Tuple[DataFrame, uc.STRING_LIST]:
    FT_data = read_csv(st.FT_DATA_URL, dtype=st.FT_DATA_TYPES, parse_dates=[uc.DATE, ])[
        [uc.DATE, uc.COUNTRY, uc.REGION, uc.EXCESS_DEATHS, uc.EXPECTED_DEATHS, uc.TOTAL_EXCESS_DEATHS_PCT]
    ]

    return FT_data, [c for c in FT_data.country.unique() if CountryHasExcessDeathEstimates(FT_data, c)]


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


def WrangleData(
        FT_data: DataFrame,
        CountryNames: uc.STRING_LIST
) -> Tuple[DataFrame, str, str]:

    data = [FilterDataForOneCountry(FT_data, CountryName) for CountryName in CountryNames]
    Dates_With_Data = [df.loc[(notna(df.excess_deaths))].index for df in data]

    StartMonth = int(min(map(methodcaller('min', skipna=True), Dates_With_Data)).month)
    StartDate = f'2020-{StartMonth:02}-01'

    EndDate = (
        (max(map(methodcaller('max', skipna=True), Dates_With_Data)) + offsets.MonthBegin(1))
        .strftime(uc.FT_DATETIME_FORMAT)
    )

    data = DataFrame(
        {
            CountryName: ((CountrySeries[uc.EXCESS_DEATHS] / CountrySeries[uc.EXPECTED_DEATHS]) * 100)
            for CountryName, CountrySeries in zip(CountryNames, map(lambda df: df.loc[df.index >= StartDate], data))
        },
        index=date_range(start=StartDate, end=EndDate)
    )

    for method in st.INTERPOLATE_METHODS:
        with suppress(ValueError):
            return data.interpolate(method=method, limit_area=uc.INSIDE), StartDate, EndDate
