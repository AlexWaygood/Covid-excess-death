from __future__ import annotations

import logging
from pyinputplus import inputInt, inputCustom
from traceback_with_variables import iter_exc_lines
from src.unchanging_constants import STRING_LIST
import src.settings as st
from src.graph_plotting import GraphPlotter, PlotAsGraph
from src.user_input import AskIfTheyWantTheListOfCountries, ValidateRepeatQuestionAnswer, RepeatQuestionText
from typing import NoReturn


logging.basicConfig(format=st.LOGGING_CONFIG, filename=st.LogFileName())
logger = logging.getLogger(__name__)


def AskRepeatQuestion(
        GUIUsage: bool,
        SaveFile: bool,
        ErrorOccured: bool
) -> str:

    return inputCustom(
        ValidateRepeatQuestionAnswer,
        prompt=RepeatQuestionText(GUIUsage=GUIUsage, PNGExport=SaveFile, ErrorOccured=ErrorOccured),
        blank=True
    )


class DesktopGraphPlotter(GraphPlotter):
    def __init__(self) -> None:
        print(st.WELCOME_MESSAGE)
        print(st.LOADING_FT_DATA)
        super().__init__()

    def Run(
            self,
            SaveFile: bool = False,
            GUIUsage: bool = False
    ) -> NoReturn:

        while True:
            print()
            ErrorOccured = self.MakeGraph(SaveFile=SaveFile, GUIUsage=GUIUsage)
            print()

            if AskRepeatQuestion(GUIUsage=GUIUsage, SaveFile=SaveFile, ErrorOccured=ErrorOccured) == st.QUIT:
                break

    def MakeGraph(
            self,
            SaveFile: bool = False,
            GUIUsage: bool = False
    ) -> bool:

        # noinspection PyBroadException
        try:
            AskIfTheyWantTheListOfCountries(self.FT_Countries)
            CountriesToCompare = self.GetCountryNames()

            PlotAsGraph(
                self.FT_data,
                CountriesToCompare,
                st.GraphTitle(CountriesToCompare),
                SaveFile=SaveFile,
                GUIUsage=GUIUsage
            )

        except:
            Traceback = '\n'.join(iter_exc_lines())
            logging.error(f"Exception!\n\n{Traceback}\n\n")
            print(st.UNEXPECTED_ERROR_MESSAGE)
            return True

    def GetCountryNames(self) -> STRING_LIST:
        return [
            inputCustom(self.ValidateCountryName, st.Select_Country_Message(i))
            for i in range(inputInt(st.HOW_MANY_COUNTRIES_MESSAGE))
        ]

    def ValidateCountryName(self, CountryName: str) -> str:
        if CountryName not in self.FT_Countries:
            raise Exception(st.COUNTRY_NOT_FOUND_MESSAGE)
        return CountryName


DesktopGraphPlotter().Run(GUIUsage=True)
