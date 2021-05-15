from __future__ import annotations

import logging
import src.settings as st

from typing import NoReturn
from textwrap import fill as textwrap_fill
from pyinputplus import inputInt, inputCustom
from traceback_with_variables import iter_exc_lines

from src.unchanging_constants import STRING_LIST
from src.graph_plotting import GraphPlotter, PlotAsGraph
from src.data_analysis_message import GetMessage
from src.desktop_app_user_input import AskIfTheyWantTheListOfCountries, AskRepeatQuestion, RandomGraphSelected


logging.basicConfig(format=st.LOGGING_CONFIG, filename=st.LogFileName())
logger = logging.getLogger(__name__)


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
            RandomGraph = RandomGraphSelected()
            print()

            if RandomGraph:
                self.RandomGraphLoop(SaveFile=SaveFile, GUIUsage=GUIUsage)
                ErrorOccured = False
            else:
                ErrorOccured = self.CustomGraph(SaveFile=SaveFile, GUIUsage=GUIUsage)

            if AskRepeatQuestion(GUIUsage=GUIUsage, SaveFile=SaveFile, ErrorOccured=ErrorOccured) == st.QUIT:
                break

    def CustomGraph(
            self,
            SaveFile: bool,
            GUIUsage: bool
    ) -> bool:

        AskIfTheyWantTheListOfCountries(self.FT_Countries)
        CountriesToCompare = self.GetCountryNames()
        print()

        # noinspection PyBroadException
        try:
            self.MakeGraph(CountriesToCompare, SaveFile=SaveFile, GUIUsage=GUIUsage)
            return False
        except:
            logging.error(st.Desktop_Error_Message('\n'.join(iter_exc_lines())))
            print(st.UNEXPECTED_ERROR_MESSAGE)
            return True

    def RandomGraph(
            self,
            SaveFile: bool,
            GUIUsage: bool
    ) -> None:
        self.MakeGraph(self.RandomCountries(), SaveFile=SaveFile, GUIUsage=GUIUsage)

    def MakeGraph(
            self,
            CountriesToCompare: STRING_LIST,
            SaveFile: bool = False,
            GUIUsage: bool = False
    ) -> None:

        for m in filter(lambda x: x, GetMessage(self.FT_data, CountriesToCompare)):
            print(textwrap_fill(m, width=80))
            print('\n')

        PlotAsGraph(
            self.FT_data,
            CountriesToCompare,
            st.GraphTitle(CountriesToCompare),
            SaveFile=SaveFile,
            GUIUsage=GUIUsage
        )

    def GetCountryNames(self) -> STRING_LIST:
        CountryNumber = inputInt(prompt=st.HOW_MANY_COUNTRIES_MESSAGE, min=st.MIN_COUNTRIES, max=st.MAX_COUNTRIES)

        return [
            inputCustom(self.ValidateCountryName, f'{st.Select_Country_Message(i, CountryNumber, True)}: ')
            for i in range(CountryNumber)
        ]

    def ValidateCountryName(self, CountryName: str) -> str:
        if CountryName in self.FT_Countries:
            return CountryName
        if (Capitalised := CountryName.title()) in self.FT_Countries:
            return Capitalised
        if (AllCaps := CountryName.upper()) in self.FT_Countries:
            return AllCaps
        raise Exception(st.COUNTRY_NOT_FOUND_MESSAGE)


DesktopGraphPlotter().Run(GUIUsage=True)
