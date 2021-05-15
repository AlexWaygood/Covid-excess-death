from pyinputplus import inputYesNo, inputCustom, inputMenu
from pprint import pprint
from src.settings import QUIT, LIST_OF_COUNTRIES_QUESTION, INVALID_RESPONSE, ANNOUNCE_LIST_OF_COUNTRIES
from src.unchanging_constants import YES


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


def AskIfTheyWantTheListOfCountries(FT_Countries: set) -> None:
    if inputYesNo(LIST_OF_COUNTRIES_QUESTION) == YES:
        print(ANNOUNCE_LIST_OF_COUNTRIES)
        pprint(FT_Countries)
        print()


def ValidateRepeatQuestionAnswer(Answer: str) -> str:
    if Answer not in ('', QUIT, QUIT.lower()):
        raise Exception(INVALID_RESPONSE)
    return Answer.upper()


def RepeatQuestionText(
        GUIUsage: bool = False,
        PNGExport: bool = False,
        ErrorOccured: bool = False
) -> str:

    if ErrorOccured:
        return f"Press enter to generate another graph, or enter '{QUIT}' to quit. "
    if GUIUsage and PNGExport:
        return f"Hope you liked the graph! It's been saved to your computer :)\nPress enter to generate another one, or enter '{QUIT}' to quit. "
    if GUIUsage:
        return f"Hope you liked the graph! Press enter to generate another one, or enter '{QUIT}' to quit. "
    if PNGExport:
        return f"Your graph has been saved to your computer :)\nPress enter to generate another one, or enter '{QUIT}' to quit. "
    return "Your graph has been cast into the ether, as you apparently didn't want to see it or save it"


RANDOM_GRAPH = 'Random graph'
RANDOM_OR_CUSTOM_CHOICES = (RANDOM_GRAPH, 'Custom graph')


def RandomGraphSelected() -> bool:
    choice = inputMenu(
        prompt='Would you like to generate a random graph, or create a custom graph?\n\n',
        choices=RANDOM_OR_CUSTOM_CHOICES,
        numbered=True
    )

    return choice == RANDOM_GRAPH
