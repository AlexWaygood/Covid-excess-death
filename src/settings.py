from os import path
from src.unchanging_constants import WEEK, EXCESS_DEATHS, EXPECTED_DEATHS, DATE, INTERPOLATE, CUBIC, LINEAR, STRING_LIST
from datetime import datetime

"""Settings for the whole project"""


# USER INPUT SETTINGS
QUIT = 'Q'

WELCOME_MESSAGE = """Welcome to Alex Waygood's interactive data viewer for weekly excess deaths!
This script uses the FT's data. However, the script itself was written by Alex Waygood, and is in no way affiliated with the FT.
"""

LOADING_FT_DATA = "Loading FT data..."
FT_DATA_LOADED = "FT data has been loaded!"

LIST_OF_COUNTRIES_QUESTION = "Would you like to see a list of available countries in the FT's dataset? "
ANNOUNCE_LIST_OF_COUNTRIES = "The following countries are available in the FT's dataset: "
COUNTRY_NOT_FOUND_MESSAGE = 'Country not in FT dataset; please try again.'
HOW_MANY_COUNTRIES_MESSAGE = 'Please enter how many countries you want to compare: '
HOW_MANY_COUNTRIES_BUTTON_LABEL = 'Submit'
INVALID_RESPONSE = 'Not a valid response, please try again.'

UNEXPECTED_ERROR_MESSAGE = 'Looks like there was an error here! ' \
                           'Check the log file for more info. Maybe try with different countries?'


MIN_COUNTRIES = 1
MAX_COUNTRIES = 5


def Select_Country_Message(i: int) -> str:
	return f'Please enter the name of country {i + 1} you wish to compare: '


# LOGGING SETTINGS
LOGGING_CONFIG = '%(asctime)-15s %(name)s %(levelname)s %(message)s'


def LogFileName() -> str:
	return path.join('..', 'error_logs', f"Covid graph error log - {datetime.now().strftime('%Y-%m-%d')}.txt")


# GENERAL GRAPH SETTINGS
BACKGROUND_COLOUR = '#fdffd4'
STANDARD_TEXT_COLOUR = '#747564'
STANDARD_FONT = 'Times New Roman'

# GRAPH EXPORT SETTINGS
EXPORT_FILE_PATH = path.join('..', 'graph_images')
EXPORT_FILE_TYPE = 'png'

# AXES SETTINGS
AXIS_TICK_COLOUR = STANDARD_TEXT_COLOUR
AXIS_FONT = STANDARD_FONT
AXIS_TEXT_COLOUR = STANDARD_TEXT_COLOUR

# GRAPH DIMENSIONS SETTINGS
FIGURE_WIDTH = 12
FIGURE_HEIGHT = 6
GRAPH_TOP = 0.8
GRAPH_BOTTOM = 0.2

# TITLE SETTINGS

COUNTRIES_WHICH_NEED_ARTICLE = ('US', 'UK', 'Netherlands', 'Czech Republic', 'Philippines')


def AddArticle(country: str) -> str:
	return f'the {country}' if country in COUNTRIES_WHICH_NEED_ARTICLE else country


def GraphTitle(Countries: STRING_LIST) -> str:
	Countries = list(map(AddArticle, Countries))
	Countries = Countries[0] if len(Countries) == 1 else f'{", ".join(Countries[:-1])} and {Countries[-1]}'
	return f'Pandemic excess deaths in {Countries}'


GRAPH_TITLE_POSITION = 0.93
TITLE_SIZE = 'xx-large'
TITLE_FONT = STANDARD_FONT
TITLE_COLOUR = STANDARD_TEXT_COLOUR

# SUBTITLE SETTINGS
SUB_TITLE = 'Relative to historical average for same dates, %'
SUB_TITLE_PADDING_FROM_GRAPH = 18
SUB_TITLE_COLOUR = STANDARD_TEXT_COLOUR
SUB_TITLE_FONT = STANDARD_FONT

# LEGEND SETTINGS
LEGEND_OPACITY = 1
LEGEND_FONT = STANDARD_FONT
LEGEND_TEXT_COLOUR = STANDARD_TEXT_COLOUR

# DATA SELECTION SETTINGS
END_DATE = '2021-04-24'
FT_DATA_URL = 'https://raw.githubusercontent.com/Financial-Times/coronavirus-excess-mortality-data/master/data/ft_excess_deaths.csv'
FT_DATA_TYPES = {WEEK: float, EXPECTED_DEATHS: float, EXCESS_DEATHS: float, DATE: str}

# HORIZONTAL LINE SETTINGS
HORIZONTAL_LINE_COLOUR = 'silver'
HORIZONTAL_LINE_WIDTH = 1
HORIZONTAL_LINE_STYLE = 'dashed'
HORIZONTAL_LINE_INCREMENT = 50

X_AXIS_LINE_SYTLE = HORIZONTAL_LINE_STYLE
X_AXIS_COLOUR = 'grey'
X_AXIS_WIDTH = 1.3

# COPYRIGHT LABEL SETTINGS
COPYRIGHT_LABEL = 'Data from the Financial Times | Graph © Alex Waygood'
COPYRIGHT_LABEL_FONT = STANDARD_FONT
COPYRIGHT_LABEL_COLOUR = STANDARD_TEXT_COLOUR
COPYRIGHT_LABEL_PADDING_FROM_X_AXIS = 25

# GRAPH SMOOTHING SETTINGS
# See https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.interpolate.html#pandas.DataFrame.interpolate...
# ...For the full range of interpolation methods that can be supplied

# should be either FFILL or INTERPOLATE
FILL_MISSING_DATA_METHOD = INTERPOLATE

# only relevant if FILL_MISSING_DATA_METHOD is INTERPOLATE
# Should be CUBIC or LINEAR
INTERPOLATE_METHOD = CUBIC


