from __future__ import annotations

from os import path
from src.common_files import use_case

use_case.WEB_MODE = True

# This file isn't uploaded to Google App Engine, so won't "exist" from Google's PoV.
if path.exists('DEVELOPMENT_ONLY.py'):
    use_case.LOCAL_HOSTING = True

from flask import Flask, render_template, send_from_directory, request
from expiringdict import ExpiringDict
from typing import Optional, Tuple, Final
from warnings import filterwarnings

from src.web_app.web_graph_plotting import WebGraphPlotter

filterwarnings('ignore')
app: Final = Flask(__name__, static_url_path='/static/', static_folder='static')
plotter: Optional[WebGraphPlotter] = None
CACHED_PAGES: Final[ExpiringDict[str, str]] = ExpiringDict(1_000_000, 86_400)


def cached_template_renderer(page: str) -> str:
    plotter.Reset()
    if page not in CACHED_PAGES:
        CACHED_PAGES[page] = render_template(page, plotter=plotter)
    return CACHED_PAGES[page]


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
    return cached_template_renderer('home.html')


@app.route('/about/')
def about() -> str:
    return cached_template_renderer('about.html')


@app.route('/dataviewer/')
def dataviewer(FromRedirect=False) -> str:
    if plotter.Update(FromRedirect).IncorrectEntry:
        return dataviewer(FromRedirect=True)
    return render_template('data_viewer.html', plotter=plotter, FromRedirect=FromRedirect)


### Error handlers ###


# noinspection PyUnusedLocal
@app.errorhandler(404)
def page_not_found(e) -> Tuple[str, int]:
    return cached_template_renderer('404.html'), 404


# noinspection PyUnusedLocal
@app.errorhandler(500)
def ServerError(e) -> Tuple[str, int]:
    return cached_template_renderer('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True, ssl_context=(None if use_case.LOCAL_HOSTING else 'adhoc'))
