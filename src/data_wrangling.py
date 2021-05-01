from __future__ import annotations

from typing import Tuple
from datetime import datetime
from pandas import date_range, notna, DataFrame
# noinspection PyPep8Naming
import src.unchanging_constants as uc
from src import settings as st

"""Smattering of helper functions"""


def WrangleData(
        FT_data: DataFrame,
        CountriesToCompare: uc.STRING_LIST
) -> Tuple[DataFrame, str]:

    data = FilterFTData1(FT_data, CountriesToCompare)
    StartDate = GetStartDate(data)
    data = FilterFTData2(StartDate, data)
    data = CalculateWeeklyData(data)
    data = FillMissingDataValues(data)
    return MergeDataFrames(CountriesToCompare, data, StartDate), StartDate


def GetStartDate(data: uc.DATA_FRAME_LIST) -> str:
    Filtered = [
        country.loc[(notna(country.excess_deaths)) & (country.index < FTDatetime(uc.JAN_01_2021))]
        for country in data
    ]

    MinMonth = int(min(country.index.month.min(skipna=True) for country in Filtered))
    return f'2020-{MinMonth:02}-01'


def FTDatetime(date: str):
    return datetime.strptime(date, uc.FT_DATETIME_FORMAT)


def FilterDataForOneCountry(
        FT_data: DataFrame,
        CountryName: str,
        EndDate: datetime
) -> DataFrame:

    data = FT_data.loc[(FT_data.region == CountryName) & (2019 < FT_data.year) & (FT_data.date <= EndDate)]
    data = data[[uc.WEEK, uc.EXPECTED_DEATHS, uc.EXCESS_DEATHS, uc.DATE, uc.MONTH, uc.YEAR]]
    data = data.sort_values(uc.DATE).drop_duplicates().set_index(uc.DATE)
    return data.reindex(date_range(start=data.index[0], end=data.index[-1]))


def FilterFTData1(
        FT_data: DataFrame,
        CountryNames: uc.STRING_LIST
) -> uc.DATA_FRAME_LIST:

    EndDate = FTDatetime(st.END_DATE)
    return [FilterDataForOneCountry(FT_data, country, EndDate) for country in CountryNames]


def FilterFTData2(StartDate, data: uc.DATA_FRAME_LIST) -> uc.DATA_FRAME_LIST:
    return [series.loc[series.index >= StartDate] for series in data]


def CalculateWeeklyData(data: uc.DATA_FRAME_LIST) -> uc.DATA_FRAME_LIST:
    for Country in data:
        Country[uc.EXCESS_WEEKLY_PCT] = Country[uc.EXCESS_DEATHS] / Country[uc.EXPECTED_DEATHS] * 100
    return data


def MergeDataFrames(
        CountryNames: uc.STRING_LIST,
        data: uc.DATA_FRAME_LIST,
        StartDate: str
) -> DataFrame:

    return DataFrame(
        {CountryName: Country[uc.EXCESS_WEEKLY_PCT] for CountryName, Country in zip(CountryNames, data)},
        index=date_range(start=StartDate, end=st.END_DATE)
    )


def FillMissingDataValuesForOneCountry(data: DataFrame) -> DataFrame:
    if st.FILL_MISSING_DATA_METHOD == uc.INTERPOLATE:
        if st.INTERPOLATE_METHOD in (uc.SPLINE, uc.POLYNOMIAL):
            return data.interpolate(method=st.INTERPOLATE_METHOD, order=st.INTERPOLATE_ORDER)
        return data.interpolate(method=st.INTERPOLATE_METHOD)
    if st.FILL_MISSING_DATA_METHOD == uc.FFILL:
        return data.fillna(uc.FFILL)


def FillMissingDataValues(data: uc.DATA_FRAME_LIST) -> uc.DATA_FRAME_LIST:
    return [FillMissingDataValuesForOneCountry(country) for country in data]
