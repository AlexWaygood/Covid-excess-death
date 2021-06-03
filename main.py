from src.common_files import use_case

use_case.WEB_MODE = True

from typing import Optional, Tuple
from warnings import filterwarnings
from flask import Flask, render_template, send_from_directory, request
from src.web_app.web_graph_plotting import WebGraphPlotter


filterwarnings('ignore')
app = Flask(__name__, static_folder='static')
plotter: Optional[WebGraphPlotter] = None


### Configuration routes ###


@app.before_first_request
def InitialiseManager() -> None:
    """
    Initialises an o plotter object that will grab the FT's data from Github
    in the background and start wrangling it
    """

    global plotter
    plotter = WebGraphPlotter()


@app.route('/robots.txt')
def static_from_root() -> str:
    """The robots.txt file defines whether robots are allowed to crawl this site or not."""

    return send_from_directory(app.static_folder, request.path[1:])


@app.route('/link-image/')
def preview() -> str:
    """The image that's shown on links when they're shared on Facebook/Twitter"""

    return send_from_directory(app.static_folder, 'images/link-graphic.png')


### Specific webpage routes ###


@app.route('/')
def home() -> str:
    return render_template('home.html', plotter=plotter.Reset(), AboutPage=False)


@app.route('/about/')
def about() -> str:
    return render_template('about.html', plotter=plotter.Reset(), AboutPage=True)


@app.route('/dataviewer/')
def dataviewer(FromRedirect=False) -> str:
    if plotter.Update(FromRedirect).IncorrectEntry:
        return dataviewer(FromRedirect=True)
    return render_template('data_viewer.html', plotter=plotter, FromRedirect=FromRedirect, AboutPage=False)


### Error handlers ###


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
