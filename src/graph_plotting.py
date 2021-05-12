import src.unchanging_constants as uc
import src.settings as st
from src.data_wrangling import WrangleData
from pandas import DataFrame, read_csv
from matplotlib import rcParams
import matplotlib.pyplot as plt
from os import path
from datetime import datetime
from itertools import chain


rcParams[uc.FRAMEALPHA] = st.LEGEND_OPACITY
rcParams[uc.FACECOLOR] = st.BACKGROUND_COLOUR


def FetchFTData() -> DataFrame:
    return read_csv(st.FT_DATA_URL, dtype=st.FT_DATA_TYPES, parse_dates=[uc.DATE, ])


class GraphPlotter:
    __slots__ =  'FT_data', 'FT_Countries'

    def __init__(self) -> None:
        self.FT_data = FetchFTData()
        self.FT_Countries = sorted(list(set(self.FT_data.country.to_list())))


def PNGFilePath() -> str:
    return path.join(
        st.EXPORT_FILE_PATH,
        f'Covid graph {str(datetime.now()).replace(":", ".")}.{st.EXPORT_FILE_TYPE}'
    )


def PlotAsGraph(
        FT_data: DataFrame,
        countries: uc.STRING_LIST,
        Title: str,
        GUIUsage: bool = False,
        SaveFile: bool = False,
        ReturnImage: bool = False
) -> uc.OPTIONAL_STR:

    data, StartDate = WrangleData(FT_data, countries)
    fig, ax = plt.subplots(figsize=(st.FIGURE_WIDTH, st.FIGURE_HEIGHT))
    ax = data.plot(ax=ax)
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

    for i in chain(PosLines, NegLines):
        if i:
            plt.hlines(i, StartDate, st.END_DATE, colors=colour, linestyles=style, linewidths=width)

    plt.hlines(
        0,
        StartDate,
        st.END_DATE,
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

    plt.yticks(fontfamily='serif')
    plt.xticks(fontfamily='serif')

    for s in (uc.TOP, uc.RIGHT, uc.LEFT, uc.BOTTOM):
        ax.spines[s].set_visible(False)

    plt.setp(plt.legend().get_texts(), color=st.LEGEND_TEXT_COLOUR, fontproperties=st.LEGEND_FONT)

    if SaveFile:
        plt.savefig(PNGFilePath())

    if GUIUsage:
        plt.show()

    if ReturnImage:
        from io import BytesIO
        from base64 import b64encode
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        return b64encode(buf.getvalue()).decode('ascii')
