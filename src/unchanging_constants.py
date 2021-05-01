from __future__ import annotations
from typing import List
from pandas import DataFrame

"""Magic numbers and strings that don't need to be changed."""

FFILL = 'ffill'
INTERPOLATE = 'interpolate'
SPLINE = 'spline'
POLYNOMIAL = 'polynomial'
WEEK = 'week'
MONTH = 'month'
EXPECTED_DEATHS = 'expected_deaths'
EXCESS_DEATHS = 'excess_deaths'
DATE = 'date'
YEAR = 'year'
EXCESS_WEEKLY_PCT = 'excess_weekly_pct'
FT_DATETIME_FORMAT = '%Y-%m-%d'
JAN_01_2021 = '2021-01-01'
TOP = 'top'
RIGHT = 'right'
LEFT = 'left'
BOTTOM = 'bottom'
BOTH = 'both'
X_AXIS = 'x'
Y_AXIS = 'y'
FRAMEALPHA = 'legend.framealpha'
FACECOLOR = 'figure.facecolor'
WEB_APP = 'web'
DESKTOP_APP = 'desktop'
YES = 'yes'


STRING_LIST = List[str]
DATA_FRAME_LIST = List[DataFrame]
