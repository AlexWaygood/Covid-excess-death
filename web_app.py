from src.graph_plotting import GraphPlotter, PlotAsGraph
from src.data_wrangling import WrangleData
from flask import Flask, request
import src.settings as st
from typing import Optional
from threading import Thread


NEW_LINE = '<p><br></p>'
HOW_MANY_COUNTRIES = 'HowManyCountries'
WHICH_COUNTRIES = 'WhichCountries'
app = Flask(__name__)


def InsertLineBreaks(text: str) -> str:
	text = text.replace('\n', '<br>')
	return f"<p>{text}</p>"


class WebGraphPlotter(GraphPlotter):
	__slots__ = 'CountryNumber'

	def __init__(self) -> None:
		super().__init__()
		self.CountryNumber = 0


plotter: Optional[WebGraphPlotter] = None
ThreadStarted = False


def InitialiseGraphPlotter() -> None:
	global plotter, ThreadStarted
	ThreadStarted = True
	p = WebGraphPlotter()
	plotter = p
	print('Plotter initialised.')


@app.before_first_request
def InitialiseManager() -> None:
	Thread(target=InitialiseGraphPlotter).start()


HOW_MANY_COUNTRIES_FORM = f''''<form action="" method="get">
  <label for="quantity">{st.HOW_MANY_COUNTRIES_MESSAGE}</label>
  <input type="number" id="{HOW_MANY_COUNTRIES}" name="{HOW_MANY_COUNTRIES}" min="{st.MIN_COUNTRIES}" max="{st.MAX_COUNTRIES}">
  <input type="submit" value="{st.HOW_MANY_COUNTRIES_BUTTON_LABEL}">
</form>'''

OrdinalDict = {
	0: 'first',
	1: 'second',
	2: 'third',
	3: 'fourth',
	4: 'fifth'
}


def FTCountriesForHTML() -> str:
	return "".join(
		f"<option value='{country}'>"
		for country in sorted(plotter.FT_Countries)
		if country not in request.args.values()
	)


def SingleCountryOption(i: int, Countries: str) -> str:
	Label = f'Please enter the {OrdinalDict[i]} country you would like to compare: '

	return f'''<tr>
					<td align="left">{Label}</td>
					<td align="left">
				        <input list="countries" name="Country{i}">
				        <datalist id="countries">
				            {Countries}
				        </datalist>
					</td>
				</tr>'''


@app.route('/')
def index() -> str:
	global plotter
	Page = '<title>Pandemic excess deaths</title>'
	Page += InsertLineBreaks(st.WELCOME_MESSAGE)

	if not plotter:
		Page += f'{NEW_LINE}{st.LOADING_FT_DATA}{NEW_LINE}(Refresh until an input box pops up on the screen!)'
	elif not any((
			(CountryNumber := request.args.get(HOW_MANY_COUNTRIES)),
			(Country0 := request.args.get('Country0'))
	)):
		Page += HOW_MANY_COUNTRIES_FORM
	elif not Country0:
		plotter.CountryNumber = CountryNumber = int(CountryNumber)
		CountryList = FTCountriesForHTML()

		Page += f'''<form action="" method="get">
		  <table>
		  {"<tr></tr>".join(SingleCountryOption(i, CountryList) for i in range(CountryNumber))}
		  <tr></tr><tr></tr>
		  <tr><td><input type="submit"></td></tr>
		</table>
		</form>'''

	else:
		return PlotAsGraph(
			*WrangleData(plotter.FT_data, [request.args.get(f'Country{i}') for i in range(plotter.CountryNumber)]),
			ReturnImage=True
		)

	return Page


if __name__ == '__main__':
	app.run(host="127.0.0.1", port=8080, debug=True)
