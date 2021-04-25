from __future__ import annotations

import logging
from pyinputplus import inputInt, inputCustom
from typing import Tuple
from pandas import DataFrame
from traceback_with_variables import iter_exc_lines
from src.unchanging_constants import STRING_LIST
from src.settings import QUIT_STRING, LOGGING_CONFIG, LogFileName
import src.data_wrangling as dw
from src.graph_plotting import PlotAsGraph
from src.user_input import AskIfTheyWantTheListOfCountries, ValidateRepeatQuestionAnswer, RepeatQuestionText

WELCOME_MESSAGE = """Welcome to Alex Waygood's interactive data viewer for weekly excess deaths!
This script uses the FT's data. However, the script itself was written by Alex Waygood, and is in no way affiliated with the FT.
Loading FT data..."""

GUI_USAGE = True
IMAGE_EXPORT = False

logging.basicConfig(format=LOGGING_CONFIG, filename=LogFileName())
logger = logging.getLogger(__name__)

FT_Countries = set()


def ValidateCountryName(CountryName: str) -> str:
    if CountryName not in FT_Countries:
        raise Exception('Country not in FT dataset, please try again')
    return CountryName


def GetCountryNames() -> STRING_LIST:
    return [
        inputCustom(ValidateCountryName, f'Please enter the name of country {i + 1} you wish to compare: ')
        for i in range(inputInt('Please enter how many countries you want to compare: '))
    ]


def WrangleData(
        FT_data: DataFrame,
        CountriesToCompare: STRING_LIST
) -> Tuple[DataFrame, str]:

    data = dw.FilterFTData1(FT_data, CountriesToCompare)
    StartDate = dw.GetStartDate(data)
    data = dw.FilterFTData2(StartDate, data)
    data = dw.CalculateWeeklyData(data)
    data = dw.FillMissingDataValues(data)
    return dw.MergeDataFrames(CountriesToCompare, data, StartDate), StartDate


def MakeGraph(
        FT_data: DataFrame,
        ImageExport: bool = False,
        GUIUsage: bool = False
) -> bool:

    # noinspection PyBroadException
    try:
        AskIfTheyWantTheListOfCountries(FT_Countries)
        CountriesToCompare = GetCountryNames()
        PlotAsGraph(*WrangleData(FT_data, CountriesToCompare), ImageExport=ImageExport, GUIUsage=GUIUsage)
    except:
        Traceback = '\n'.join(iter_exc_lines())
        logging.error(f"Exception!\n\n{Traceback}\n\n")
        print('Looks like there was an error here! Check the log file for more info. Maybe try with different countries?')
        return True


def Main(
        GUIUsage: bool = False,
        ImageExport: bool = False
) -> None:

    global FT_Countries
    print(WELCOME_MESSAGE)

    FT_data = dw.FetchFTData()
    FT_Countries = set(FT_data.country.to_list())

    while True:
        print()
        ErrorOccured = MakeGraph(FT_data, ImageExport=ImageExport, GUIUsage=GUIUsage)
        print()
        RepeatQuestionPrompt = RepeatQuestionText(GUIUsage=GUIUsage, PNGExport=ImageExport, ErrorOccured=ErrorOccured)
        if inputCustom(ValidateRepeatQuestionAnswer, prompt=RepeatQuestionPrompt, blank=True) == QUIT_STRING:
            break


Main(GUIUsage=True, ImageExport=True)
