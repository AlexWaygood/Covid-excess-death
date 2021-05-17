from __future__ import annotations

import matplotlib.pyplot as plt
import src.unchanging_constants as uc
import src.settings as st

from typing import TYPE_CHECKING
from itertools import chain
from random import randint, sample as random_sample

from matplotlib import rcParams
from PyQt5.QtGui import QIcon

from src.data_wrangling import WrangleData, FTDataAndCountries

if TYPE_CHECKING:
    from pandas import DataFrame


rcParams[uc.FRAMEALPHA] = st.LEGEND_OPACITY
rcParams[uc.FACECOLOR] = st.BACKGROUND_COLOUR


class GraphPlotter:
    __slots__ =  'FT_data', 'FT_Countries'

    def __init__(self) -> None:
        self.FT_data, self.FT_Countries = FTDataAndCountries()

    def RandomCountries(self) -> uc.STRING_LIST:
        return random_sample(self.FT_Countries, randint(st.MIN_COUNTRIES, st.MAX_COUNTRIES))

    def RandomGraph(self, **kwargs) -> None:
        raise NotImplementedError

    def RandomGraphLoop(self, **kwargs) -> None:
        while True:
            # noinspection PyBroadException
            try:
                self.RandomGraph(**kwargs)
                break
            except:
                pass

    def DoTest(
            self,
            OnlyDataTest: bool = False,
            GraphingTest: bool = False
    ) -> None:

        """Only seems to work as intended in an interactive console when testing matplotlib"""

        print('Starting testing...')

        for country in self.FT_Countries:
            # noinspection PyBroadException
            try:
                if OnlyDataTest:
                    WrangleData(self.FT_data, [country])
                elif GraphingTest:
                    PlotAsGraph(self.FT_data, [country], 'Graph', ReturnImage=True)
            except:
                print(country)

        print('Testing finished.')


def PlotAsGraph(
        FT_data: DataFrame,
        countries: uc.STRING_LIST,
        Title: str,
        GUIUsage: bool = False,
        SaveFile: bool = False,
        ReturnImage: bool = False
) -> uc.OPTIONAL_STR:

    data, StartDate, EndDate = WrangleData(FT_data, countries)
    fig, ax = plt.subplots(figsize=(st.FIGURE_WIDTH, st.FIGURE_HEIGHT))
    ax = data.plot(ax=ax)

    if GUIUsage:
        fig.canvas.set_window_title(st.WINDOW_CAPTION)
        plt.get_current_fig_manager().window.setWindowIcon(QIcon(st.FAVICON_FILE_PATH))

    ax.set_facecolor(st.BACKGROUND_COLOUR)

    plt.suptitle(
        Title,
        size=st.TITLE_SIZE,
        fontproperties=st.TITLE_FONT,
        color=st.TITLE_COLOUR,
        y=st.GRAPH_TITLE_POSITION
    )

    plt.title(
        st.SUB_TITLE,
        pad=st.SUB_TITLE_PADDING_FROM_GRAPH,
        color=st.SUB_TITLE_COLOUR,
        fontproperties=st.SUB_TITLE_FONT
    )

    PosLines = range(0, int(max(data.max())), st.HORIZONTAL_LINE_INCREMENT)
    NegLines = range(0, int(min(data.min())), -st.HORIZONTAL_LINE_INCREMENT)
    colour, style, width = st.HORIZONTAL_LINE_COLOUR, st.HORIZONTAL_LINE_STYLE, st.HORIZONTAL_LINE_WIDTH

    for i in filter(bool, chain(PosLines, NegLines)):
        plt.hlines(i, StartDate, EndDate, colors=colour, linestyles=style, linewidths=width)

    plt.hlines(
        0,
        StartDate,
        EndDate,
        colors=st.X_AXIS_COLOUR,
        linestyles=st.X_AXIS_LINE_SYTLE,
        linewidths=st.X_AXIS_WIDTH
    )

    plt.subplots_adjust(top=st.GRAPH_TOP, bottom=st.GRAPH_BOTTOM)

    plt.xlabel(
        st.COPYRIGHT_LABEL,
        fontproperties=st.COPYRIGHT_LABEL_FONT,
        color=st.COPYRIGHT_LABEL_COLOUR,
        labelpad=st.COPYRIGHT_LABEL_PADDING_FROM_X_AXIS
    )

    ax.tick_params(
        axis=uc.Y_AXIS,
        which=uc.BOTH,
        left=False,
        right=False,
        labelcolor=st.AXIS_TICK_COLOUR
    )

    ax.tick_params(axis=uc.X_AXIS, which=uc.BOTH, colors=st.AXIS_TICK_COLOUR)

    plt.yticks(fontfamily=st.AXIS_FONT)
    plt.xticks(fontfamily=st.AXIS_FONT)

    for s in (uc.TOP, uc.RIGHT, uc.LEFT, uc.BOTTOM):
        ax.spines[s].set_visible(False)

    if len(countries) == 1:
        ax.legend().set_visible(False)
    else:
        plt.setp(plt.legend().get_texts(), color=st.LEGEND_TEXT_COLOUR, fontproperties=st.LEGEND_FONT)

    if SaveFile:
        plt.savefig(st.PNGFilePath())

    if GUIUsage:
        plt.show()

    if ReturnImage:
        from io import BytesIO
        from base64 import b64encode
        buf = BytesIO()
        plt.savefig(buf, format=st.WEB_DISPLAY_FILE_TYPE)
        plt.close('all')
        buf.seek(0)
        return b64encode(buf.getvalue()).decode(uc.ASCII)

    plt.close('all')


if __name__ == '__main__':
    GraphPlotter().DoTest(GraphingTest=True)
