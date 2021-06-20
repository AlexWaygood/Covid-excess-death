from __future__ import annotations

from os import path
from src.common_files import use_case

use_case.WEB_MODE = True

# This file isn't uploaded to Google App Engine, so won't "exist" from Google's PoV.
use_case.LOCAL_HOSTING = path.exists(path.join('src', 'web_app', 'DEVELOPMENT_ONLY.py'))

from threading import Thread
from flask import Flask, render_template, send_from_directory, request
from time import sleep
import src.common_files.unchanging_constants as uc

from typing import TYPE_CHECKING, Optional, Final, Dict, Any

if TYPE_CHECKING:
    from src.web_app.web_graph_plotting import WebGraphPlotter
    from src.common_files.covid_graph_types import PAGE_AND_ERROR_CODE
    from expiringdict import ExpiringDict


app: Final = Flask(__name__, static_url_path='/static/', static_folder='static')
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

plotter: Optional[WebGraphPlotter] = None
Cached_pages: Optional[ExpiringDict[str, str]] = None


def cached_template_renderer(page: str) -> str:
    """
    A template renderer that caches its results.
    Only the /dataviewer/?HowManyCountries=random route is dynamic, and that route isn't sent to this function.
    All other routes can be safely cached.

    The plotter object & Cached_pages dict are launched in a separate thread,
    so we have to check they exist before using them.
    """

    if any((Cached_pages is None, page == uc.DATAVIEWER_1_PAGE, (bool(plotter) and plotter.RandomGraphSelected))):
        return render_template(page)

    # The dataviewer FromRedirect page will be the same every time, no matter what the typo in the URL is,
    # so it doesn't make sense to cache each typo separately.

    key = None if plotter.IncorrectEntry else request.url

    if key not in Cached_pages:
        Cached_pages[key] = render_template(page)

    return Cached_pages[key]


def threaded_before_first_request() -> None:
    """
    Initialises a WebGraphPlotter object that will grab the FT's data from Github
    in the background and start wrangling it.

    Also initialises an ExpiringDict object to cache web pages, for quicker access next time.

    This function is launched in a separate thread,
    as both of these actions involve imports that are inessential for the homepage to launch on first access.
    """

    # Since we're using global variables here, we can't type-annotate these variables as Final

    global plotter, Cached_pages

    from src.web_app.web_graph_plotting import WebGraphPlotter
    plotter = WebGraphPlotter()

    from expiringdict import ExpiringDict
    Cached_pages = ExpiringDict(1_000_000, 86_400)


### Configuration functions ###


@app.before_first_request
def InitialiseManager() -> None:
    """
    Fairly bulky imports that aren't essential to immediately launching the homepage,
    so we want to make sure we do the import in a separate thread.
    """

    Thread(target=threaded_before_first_request).start()


@app.before_request
def UpdatePlotter() -> None:
    if plotter:
        plotter.Update(request.url_root, request.path, **request.args)


@app.context_processor
def inject_plotter() -> Dict[str, Any]:
    return {'plotter': plotter}


@app.route('/robots.txt')
def static_from_root() -> str:
    """The robots.txt file defines whether robots are allowed to crawl this site or not."""

    return send_from_directory(app.static_folder, request.path[1:])


@app.route('/link-image')
def social_media_link_preview() -> str:
    """The image that's shown on links when they're shared on Facebook/Twitter"""

    return send_from_directory(app.static_folder, 'images/link-graphic.png')


### Specific webpage routes ###


@app.route('/dataviewer/')
def dataviewer() -> str:
    if not plotter:
        while not plotter:
            sleep(0.5)
        UpdatePlotter()

    return cached_template_renderer(plotter.TemplateForRendering)


@app.route('/', defaults={'page': 'home'})
@app.route('/<page>')
def static_routes(page: str) -> str:

    """
    Function for all static routes that are directly mapped onto an html template:
    home.html, about.html, 404.html, 500.html.

    This function must be defined last of all routes, due to the "catch-all" nature of the url_rule defined.
    """

    return cached_template_renderer(f'{page}.html')


### Error handlers ###


# noinspection PyUnusedLocal
@app.errorhandler(404)
def page_not_found(e) -> PAGE_AND_ERROR_CODE:
    return cached_template_renderer(uc.PAGE_NOT_FOUND_PAGE), 404


# noinspection PyUnusedLocal
@app.errorhandler(500)
def ServerError(e) -> PAGE_AND_ERROR_CODE:
    return cached_template_renderer(uc.SERVER_ERROR_PAGE), 500


if __name__ == '__main__':
    app.run(
        debug=use_case.LOCAL_HOSTING,
        ssl_context=(None if use_case.LOCAL_HOSTING else 'adhoc')
    )
