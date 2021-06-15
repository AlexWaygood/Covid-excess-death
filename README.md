# Covid excess deaths

Use the web app here: http://covid-excess-deaths.ew.r.appspot.com/ (main.py).

Alternatively, run on your desktop by running desktop_app.py.

A simple script to generate a graph comparing excess deaths between two or more countries. The script uses data on excess deaths that has been collected by the excellent team of data journalists at the FT. The FT's original repository is here: https://github.com/Financial-Times/coronavirus-excess-mortality-data.

The web app was made using Flask, and the graphs are made using the pandas and matplotlib libraries. The entire core of the app is written in Python (plus some HTML templates, javascript functions and CSS styling for the web app).

N.B. requirements.txt only holds requirements for the web app; desktop_requirements.txt has the requirements for the desktop app. all_requirements.txt has the two package requirements combined into one list.