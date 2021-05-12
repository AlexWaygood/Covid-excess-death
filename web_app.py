from flask import Flask, render_template
from typing import Optional, Tuple
from threading import Thread
from src.web_graph_plotting import WebGraphPlotter


app = Flask(__name__)
plotter: Optional[WebGraphPlotter] = None


@app.before_first_request
def InitialiseManager() -> None:
    global plotter
    plotter = WebGraphPlotter()
    Thread(target=plotter.Initialise).start()


@app.route('/')
def home() -> str:
    return render_template('home.html', plotter=plotter.Reset(), AboutPage=False)


@app.route('/about/')
def about() -> str:
    return render_template('about.html', plotter=plotter.Reset(), AboutPage=True)


@app.route('/dataviewer/')
def dataviewer(FromRedirect=False) -> str:
    plotter.Update(FromRedirect)

    if plotter.IncorrectEntry:
        return dataviewer(FromRedirect=True)

    return render_template('data_viewer.html', plotter=plotter, FromRedirect=FromRedirect, AboutPage=False)


@app.errorhandler(404)
def page_not_found(e) -> Tuple[str, int]:
    return render_template('404.html', plotter=plotter.Reset(), AboutPage=False), 404


if __name__ == '__main__':
    app.run(debug=True)
