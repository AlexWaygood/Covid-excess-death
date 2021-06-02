from src.common_files import use_case

use_case.WEB_MODE = True

from typing import Optional, Tuple
from warnings import filterwarnings
from flask import Flask, render_template, send_from_directory
from src.web_app.web_graph_plotting import WebGraphPlotter


filterwarnings('ignore')
app = Flask(__name__)
plotter: Optional[WebGraphPlotter] = None


@app.before_first_request
def InitialiseManager() -> None:
    global plotter
    plotter = WebGraphPlotter()


@app.route('/')
def home() -> str:
    return render_template('home.html', plotter=plotter.Reset(), AboutPage=False)


@app.route('/link-preview.png')
def preview() -> str:
    return send_from_directory('static', 'images/coronavirus.png')


@app.route('/about/')
def about() -> str:
    return render_template('about.html', plotter=plotter.Reset(), AboutPage=True)


@app.route('/dataviewer/')
def dataviewer(FromRedirect=False) -> str:
    if plotter.Update(FromRedirect).IncorrectEntry:
        return dataviewer(FromRedirect=True)
    return render_template('data_viewer.html', plotter=plotter, FromRedirect=FromRedirect, AboutPage=False)


# noinspection PyUnusedLocal
@app.errorhandler(404)
def page_not_found(e) -> Tuple[str, int]:
    return render_template('404.html', plotter=plotter.Reset(), AboutPage=False), 404


# noinspection PyUnusedLocal
@app.errorhandler(500)
def ServerError(e) -> Tuple[str, int]:
    return render_template('500.html', plotter=plotter.Reset(), AboutPage=False), 500


if __name__ == '__main__':
    app.run(debug=True)
