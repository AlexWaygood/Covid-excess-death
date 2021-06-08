from __future__ import annotations

from src.common_files.use_case import WEB_MODE, GUI_USAGE
import matplotlib, logging

if not GUI_USAGE:
    matplotlib.use('Agg')

import matplotlib.pyplot as plt
import src.common_files.unchanging_constants as uc
import src.common_files.settings as st

from threading import Thread
from itertools import chain
from random import randint, sample as random_sample
from typing import TYPE_CHECKING, Optional, KeysView
from time import sleep
from datetime import datetime

from pandas import DataFrame
from PyQt5.QtGui import QIcon
from io import BytesIO
from github import Github

from src.common_files.data_wrangling import FetchFTData, Country, PlottableData
from src.common_files.secret_passwords import GITHUB_API_TOKEN

if WEB_MODE:
    from base64 import b64encode

if TYPE_CHECKING:
    from src.common_files.covid_graph_types import GraphPlotterTypeVar, STRING_LIST, OPTIONAL_STR, STRING_SEQUENCE
    from _io import BytesIO as BytesIOClass


logger = logging.getLogger(__name__)

matplotlib.rcParams.update({
    uc.FRAMEALPHA: st.LEGEND_OPACITY,
    uc.FACECOLOR: st.BACKGROUND_COLOUR
})

MATPLOTLIB_WINDOW_OPEN = False


# noinspection PyUnusedLocal
def IfWindowClosed(event) -> None:
    """This is only relevant if you're using this module in an interactive Python shell"""

    global MATPLOTLIB_WINDOW_OPEN
    MATPLOTLIB_WINDOW_OPEN = False


def UseInteractively(*countries: str) -> None:
    """Use from src.graph_plotting import UseInteractively to use this function in an interactive Python shell"""

    GraphPlotter(GUIUsage=True, InteractiveUse=True).PrePlot(*countries).Plot()


def CloseAllFigures() -> None:
    plt.close('all')


def NoNeedToUpdate(LocalDatasetDate: datetime) -> bool:
    LastFTUpdate = datetime.strptime(
        (
            Github(GITHUB_API_TOKEN)
            .get_repo('Financial-Times/coronavirus-excess-mortality-data')
            .get_contents('data')
            [0]
            .last_modified
        ),
        '%a, %d %b %Y %H:%M:%S %Z'
    )

    return LastFTUpdate < LocalDatasetDate


# noinspection PyAttributeOutsideInit
class GraphPlotter:
    __slots__ =  'DataWrangled', 'Message1', 'Message2', 'Message3', 'data', 'StartDate', 'EndDate', 'ImageTitle', \
                 'GUIUsage', 'SaveFile', 'ReturnImage', 'InteractiveUse'

    def __init__(
            self,
            GUIUsage: bool = False,
            SaveFile: bool = False,
            ReturnImage: bool = False,
            InteractiveUse: bool = False
    ) -> None:

        """
        The call to self.Reset() fills in the values
        for data, StartDate, EndDate, ImageTitle, Message1, Message2 & Message3 attrs.

        The call to self.Initialise() loads the data.
        We do this in a separate thread, as we need the object returned from __init__() as soon as possible.
        The website won't load until the object is returned.
        """

        self.GUIUsage = GUIUsage
        self.SaveFile = SaveFile
        self.ReturnImage = ReturnImage
        self.InteractiveUse = InteractiveUse
        self.DataWrangled = False
        self.Reset()
        Thread(target=self.Initialise).start()

    def Initialise(self) -> None:
        Country.CountriesFromFile()

        if not (datetime.now() - Country.AllCountries.LastGithubUpdate).days:
            self.DataWrangled = True
        else:
            Thread(target=self.CheckLastGithubUpdate).start()
            Thread(target=self.RequestFromFTGithub).start()

    @staticmethod
    def CountryNames() -> KeysView[str]:
        return Country.AllCountries.keys()

    def Reset(self) -> None:
        self.data = None
        self.StartDate = None
        self.EndDate = None
        self.ImageTitle = ''
        self.Message1 = ''
        self.Message2 = ''
        self.Message3 = ''

    def CheckLastGithubUpdate(self) -> None:
        """
        In the event that we updated the dataset >1 day ago,
        we check to see if the FT dataset has been updated since then.

        If it hasn't, we change self.DataWrangled to True,
        indicating to the other Thread that it does not need to update our local dataset.

        If it has, we leave self.DataWrangled as False,
        informing the thread running in parallel that it needs to update our local dataset
        """

        if NoNeedToUpdate(Country.AllCountries.LastGithubUpdate):
            self.DataFromFile()  # Changes self.DataWrangled to True

    def RequestFromFTGithub(self) -> None:
        """
        Download the csv file on github and process it.

        The other thread running in parallel uses a different function call
        to determine whether the csv file has been updated since last we downloaded it.

        If it has, then this thread will use the data we have just downloaded to update our local dataset.

        If it hasn't, then we dicard the data that we have just downloaded,
        as it is identical to the data we already had.
        """

        df = FetchFTData()

        if not self.DataWrangled:
            Country.CountriesFromGithub(df)
            self.DataWrangled = True

    def DataFromFile(self) -> None:
        self.DataWrangled = True
        Country.AllCountries.LastUpdateTimeReset()

    def PrePlot(self: GraphPlotterTypeVar, *countries: str) -> GraphPlotterTypeVar:
        (
            self.Message1,
            self.Message2,
            self.Message3,
            self.ImageTitle,
            self.StartDate,
            self.EndDate,
            self.data
        ) = PlottableData(*countries)

        return self

    def WaitForLoad(self) -> None:
        while not self.DataWrangled:
            sleep(0.5)

    def RandomCountries(self) -> STRING_LIST:
        self.WaitForLoad()
        return random_sample(self.CountryNames(), randint(st.MIN_COUNTRIES, st.MAX_COUNTRIES))

    def RandomGraph(self, **kwargs) -> None:
        """Placeholder method to be filled in higher up the inheritance chain"""
        raise NotImplementedError

    def RandomGraphLoop(self) -> None:
        for i in range(5):
            # noinspection PyBroadException
            try:
                self.RandomGraph()
                break
            except NotImplementedError:
                raise
            except Exception:
                logger.error(st.Desktop_Error_Message())
        else:
            # This clause only reached if there are 5 errors in a row when trying to make a graph.
            print('Lots of errors seem to be taking place here! Check the error log for more details.')

    def Plot(self, *CountriesToPlot: str) -> OPTIONAL_STR:
        return PlotAsGraph(
            CountriesToPlot,
            self.data,
            self.StartDate,
            self.EndDate,
            self.ImageTitle,
            GUIUsage=self.GUIUsage,
            SaveFile=self.SaveFile,
            ReturnImage=self.ReturnImage,
            InteractiveUse=self.InteractiveUse
        )


def PlotAsGraph(
        CountriesToPlot: STRING_SEQUENCE,
        data: DataFrame,
        StartDate: str,
        EndDate: str,
        Title: str,
        GUIUsage: bool = False,
        SaveFile: bool = False,
        ReturnImage: bool = False,
        InteractiveUse: bool = False
) -> OPTIONAL_STR:

    global MATPLOTLIB_WINDOW_OPEN

    fig, ax = plt.subplots(figsize=(st.FIGURE_WIDTH, st.FIGURE_HEIGHT))

    if InteractiveUse:
        fig.canvas.mpl_connect('close_event', IfWindowClosed)

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

    if len(CountriesToPlot) == 1:
        ax.legend().set_visible(False)
    else:
        plt.setp(plt.legend().get_texts(), color=st.LEGEND_TEXT_COLOUR, fontproperties=st.LEGEND_FONT)

    if SaveFile:
        SaveToFileOrFileObj(Title)

    if GUIUsage:
        plt.show()
        if InteractiveUse:
            MATPLOTLIB_WINDOW_OPEN = True

    if ReturnImage:
        buf = BytesIO()
        SaveToFileOrFileObj(Title, buf)
        CloseAllFigures()
        buf.seek(0)
        return b64encode(buf.getvalue()).decode(uc.ASCII)

    if InteractiveUse:
        while MATPLOTLIB_WINDOW_OPEN:
            plt.pause(0.1)

    CloseAllFigures()


def SaveToFileOrFileObj(
        Title: str,
        SaveLocation: Optional[BytesIOClass] = None
) -> None:

    plt.savefig(
        (SaveLocation if SaveLocation else st.PNGFilePath()),
        format=st.WEB_DISPLAY_FILE_TYPE,
        dpi=(st.WEB_PNG_DPI if WEB_MODE else 'figure'),
        metadata=st.PNGMetadata(Title)
    )
