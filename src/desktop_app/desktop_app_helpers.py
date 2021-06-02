from __future__ import annotations

import logging
import src.common_files.settings as st

from typing import NoReturn, TYPE_CHECKING
from pprint import pprint

from rich.text import Text
from rich.panel import Panel
from rich import print as rprint

from pyinputplus import inputInt, inputCustom, inputYesNo, inputMenu

from src.common_files.graph_plotting import GraphPlotter
from src.common_files.unchanging_constants import YES, COUNTRIES_LOADED, DATA_WRANGLED

if TYPE_CHECKING:
    from src.common_files.covid_graph_types import STRING_LIST

logging.basicConfig(format=st.LOGGING_CONFIG, filename=st.LogFileName())

TEXT_JUSTIFY = 'center'
TEXT_STYLE = 'bold white on red'
VERTICAL_PADDING = 3


class DesktopGraphPlotter(GraphPlotter):
    __slots__ = 'ErrorOccured'

    def __init__(
            self,
            GUIUsage: bool = False,
            SaveFile: bool = False,
            ReturnImage: bool = False,
            InteractiveUse: bool = False
    ) -> None:

        print(f'\n{st.WELCOME_MESSAGE}')

        super().__init__(
            GUIUsage=GUIUsage,
            SaveFile=SaveFile,
            ReturnImage=ReturnImage,
            InteractiveUse=InteractiveUse
        )

        self.ErrorOccured = False

    def Run(self) -> NoReturn:
        while True:
            print()
            (self.RandomGraphLoop() if RandomGraphSelected() else (self.CustomGraph()))

            if self.AskRepeatQuestion() == st.QUIT:
                break

    def CustomGraph(self) -> None:
        self.WaitForLoad(COUNTRIES_LOADED)
        AskIfTheyWantTheListOfCountries(self.FT_Countries)
        CountriesToCompare = self.GetCountryNames()
        print()

        # noinspection PyBroadException
        try:
            self.MakeGraph(CountriesToCompare)
            self.ErrorOccured = False
        except:
            logging.error(st.Desktop_Error_Message())
            print(st.UNEXPECTED_ERROR_MESSAGE)
            self.ErrorOccured = True

    def WaitForLoad(self, attr: str) -> None:
        if not getattr(self, attr):
            print('Loading, please wait...')
            super().WaitForLoad(attr)

    def RandomGraph(self) -> None:
        self.MakeGraph(self.RandomCountries())
        self.ErrorOccured = False

    def MakeGraph(self, CountriesToCompare: STRING_LIST) -> None:
        self.WaitForLoad(DATA_WRANGLED)
        self.PrePlot(*CountriesToCompare)

        if self.GUIUsage:
            PrintDesktopMessage(self.ImageTitle, self.Message1, self.Message2, self.Message3)

        self.Plot(*CountriesToCompare)

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

    def AskRepeatQuestion(self) -> str:
        return inputCustom(
            ValidateRepeatQuestionAnswer,
            prompt=self.RepeatQuestionText(),
            blank=True
        )

    def RepeatQuestionText(self) -> str:
        if self.ErrorOccured:
            return f"Press enter to generate another graph, or enter '{st.QUIT}' to quit. "

        if self.GUIUsage and self.SaveFile:
            return f"Hope you liked the graph! It's been saved to your computer :)\n" \
                   f"Press enter to generate another one, or enter '{st.QUIT}' to quit. "

        if self.GUIUsage:
            return f"Hope you liked the graph! Press enter to generate another one, or enter '{st.QUIT}' to quit. "

        if self.SaveFile:
            return f"Your graph has been saved to your computer :)\n" \
                   f"Press enter to generate another one, or enter '{st.QUIT}' to quit. "

        return "Your graph has been cast into the ether, as you apparently didn't want to see it or save it"


def AskIfTheyWantTheListOfCountries(FT_Countries: set) -> None:
    if inputYesNo(st.LIST_OF_COUNTRIES_QUESTION) == YES:
        print(st.ANNOUNCE_LIST_OF_COUNTRIES)
        pprint(FT_Countries)
        print()


def ValidateRepeatQuestionAnswer(Answer: str) -> str:
    if Answer not in ('', st.QUIT, st.QUIT.lower()):
        raise Exception(st.INVALID_RESPONSE)
    return Answer.upper()


RANDOM_GRAPH = 'Random graph'
RANDOM_OR_CUSTOM_CHOICES = (RANDOM_GRAPH, 'Custom graph')


def RandomGraphSelected() -> bool:
    choice = inputMenu(
        prompt='Would you like to generate a random graph, or create a custom graph?\n\n',
        choices=RANDOM_OR_CUSTOM_CHOICES,
        numbered=True
    )
    print()
    return choice == RANDOM_GRAPH


def PrintDesktopMessage(GraphTitle: str, *Messages: str) -> None:
    message = '\n\n'.join(filter(bool, Messages))

    # noinspection PyTypeChecker
    text = Text(
        f"\n\n{GraphTitle.upper()}\n\n\n\n{message}\n\n\n\nFor the full details on how these graphs are made, go to \n\n",
        justify=TEXT_JUSTIFY,
        style=TEXT_STYLE
    )

    text.append(
        'http://covid-excess-deaths.ew.r.appspot.com/about/',
        style='link http://covid-excess-deaths.ew.r.appspot.com/about/ bold white on red'
    )

    text.append('\n\n', style='bold white on red')
    rprint(Panel(text, padding=(VERTICAL_PADDING, 2), style="black"))
    print()
