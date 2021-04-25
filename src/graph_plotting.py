import src.unchanging_constants as uc
import src.settings as st
from pandas import DataFrame
from matplotlib import rcParams
import matplotlib.pyplot as plt
from os import path, getcwd
from datetime import datetime


rcParams[uc.FRAMEALPHA] = st.LEGEND_OPACITY
rcParams[uc.FACECOLOR] = st.BACKGROUND_COLOUR


def PNGFilePath() -> str:
	return path.join(
		st.EXPORT_FILE_PATH,
		f'Covid graph {str(datetime.now()).replace(":", ".")}.{st.EXPORT_FILE_TYPE}'
	)


def PlotAsGraph(
		data: DataFrame,
		StartDate: str,
		GUIUsage: bool = False,
		ImageExport: bool = False
) -> None:

	ax = data.plot(figsize=(st.FIGURE_WIDTH, st.FIGURE_HEIGHT))
	ax.set_facecolor(st.BACKGROUND_COLOUR)

	plt.suptitle(
		st.GRAPH_TITLE,
		size=st.TITLE_SIZE,
		fontfamily=st.TITLE_FONT,
		color=st.TITLE_COLOUR,
		y=st.GRAPH_TITLE_POSITION
	)

	plt.title(
		st.SUB_TITLE,
		pad=st.SUB_TITLE_PADDING_FROM_GRAPH,
		color=st.SUB_TITLE_COLOUR,
		fontfamily=st.SUB_TITLE_FONT
	)

	for i in st.HORIZONTAL_LINE_POSITIONS:
		plt.hlines(
			i,
			StartDate,
			st.END_DATE,
			colors=st.HORIZONTAL_LINE_COLOUR,
			linestyles=st.HORIZONTAL_LINE_STYLE,
			linewidths=st.HORIZONTAL_LINE_WIDTH
		)

	plt.subplots_adjust(top=st.GRAPH_TOP, bottom=st.GRAPH_BOTTOM)

	plt.xlabel(
		st.COPYRIGHT_LABEL,
		fontfamily=st.COPYRIGHT_LABEL_FONT,
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

	plt.yticks(fontname=st.AXIS_FONT)
	plt.xticks(fontname=st.AXIS_FONT)

	for s in (uc.TOP, uc.RIGHT, uc.LEFT, uc.BOTTOM):
		ax.spines[s].set_visible(False)

	plt.setp(plt.legend().get_texts(), color=st.LEGEND_TEXT_COLOUR, fontfamily=st.LEGEND_FONT)

	if ImageExport:
		try:
			plt.savefig(PNGFilePath())
		except FileNotFoundError as e:
			print(getcwd())
			print(path.abspath(PNGFilePath()))
			raise e

	if GUIUsage:
		plt.show()
