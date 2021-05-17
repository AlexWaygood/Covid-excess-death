from __future__ import annotations
from typing import TYPE_CHECKING

from rich.text import Text
from rich.panel import Panel
from rich import print as rprint

from src.unchanging_constants import STRING_LIST
from src.data_analysis_message import GetMessage

if TYPE_CHECKING:
	from pandas import DataFrame


TEXT_JUSTIFY = 'center'
TEXT_STYLE = 'bold white on red'
VERTICAL_PADDING = 3


def PrintDesktopMessage(
		FT_data: DataFrame,
		Countries: STRING_LIST,
		GraphTitle: str
) -> None:

	message = '\n\n'.join(filter(bool, GetMessage(FT_data, Countries)))

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
