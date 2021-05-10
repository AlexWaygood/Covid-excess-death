from flask import Flask, render_template
from time import sleep
from typing import Optional
from threading import Thread
from src.web_app import WebGraphPlotter


app = Flask(__name__)
plotter: Optional[WebGraphPlotter] = None


def InitialiseGraphPlotter() -> None:
    global plotter
    p = WebGraphPlotter()
    plotter = p


@app.before_first_request
def InitialiseManager() -> None:
    Thread(target=InitialiseGraphPlotter).start()


@app.route('/')
def home() -> str:
    return render_template('home.html', plotter=plotter)


@app.route('/dataviewer/')
def dataviewer() -> str:
    while not plotter:
        sleep(0.1)

    return render_template('data_viewer.html', plotter=plotter.Updated())


if __name__ == '__main__':
    app.run(debug=True)
