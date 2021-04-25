from pyinputplus import inputYesNo
from pprint import pprint
from src.settings import QUIT_STRING


def AskIfTheyWantTheListOfCountries(FT_Countries: set) -> None:
    if inputYesNo("Would you like to see a list of available countries in the FT's dataset? ") == 'yes':
        print("The following countries are available in the FT's dataset: ")
        pprint(FT_Countries)
        print()


def ValidateRepeatQuestionAnswer(Answer: str) -> str:
    if Answer not in ('', 'Q'):
        raise Exception('Not a valid response, please try again.')
    return Answer


def RepeatQuestionText(
        GUIUsage: bool = False,
        PNGExport: bool = False,
        ErrorOccured: bool = False
) -> str:
    if ErrorOccured:
        return f"Press enter to generate another graph, or enter '{QUIT_STRING}' to quit. "
    if GUIUsage and PNGExport:
        return f"Hope you liked the graph! It's been saved to your computer :)\nPress enter to generate another one, or enter '{QUIT_STRING}' to quit. "
    if GUIUsage:
        return f"Hope you liked the graph! Press enter to generate another one, or enter '{QUIT_STRING}' to quit. "
    return f"Your graph has been saved to your computer :)\nPress enter to generate another one, or enter '{QUIT_STRING}' to quit. "
