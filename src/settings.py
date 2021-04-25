from os import path
from src.unchanging_constants import WEEK, EXCESS_DEATHS, EXPECTED_DEATHS, DATE, INTERPOLATE, SPLINE
from datetime import datetime

"""Settings to alter how the graph is constructed"""

# MISC SETTINGS
QUIT_STRING = 'Q'
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
GRAPH_TITLE = 'Pandemic Excess Deaths'
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
HORIZONTAL_LINE_POSITIONS = (0, 50, 100)

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
INTERPOLATE_METHOD = SPLINE

# only relevant if INTERPOLATE_METHOD is SPLINE or POLYNOMIAL. Needs to be in range 1 <= x <= 5.
INTERPOLATE_ORDER = 2
