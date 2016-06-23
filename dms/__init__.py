#!/usr/bin/env python

from flask import Flask
app = Flask(__name__)

import dms.views

"""

-----
TODO
-----

28/4/2016: we now have a way of showing the uploaded files
    * need to add some meta-data about each img file
    * add buttons to preview the uploaded file.
    show the file listing with "preview" buttons next to each file,
    and a tickbox for each file

    * (later?) upload a PDF and process it - it creates several files
        which can then hook into the above process.

23/6/2016: 
    * reorganise score.py, utils.py and DigitalMusicStand.py into models.py
    * remove the configuration below; it should be in other files.
"""

# Static folder layout:
# Uploads get put into "static/uploads",
# We can then move them around later.
import os
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'static', 'uploads')
SCORES_FOLDER = os.path.join(PROJECT_ROOT, 'static', 'scores')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_URL_PREFIX'] = "static/uploads/"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB
app.config['SCORES_FOLDER'] = SCORES_FOLDER
app.config['SCORES_URL_PREFIX'] = "static/scores/"

"""
Further Documentation

Flask Tutorial is here:
http://flask.pocoo.org/docs/0.10/quickstart/#quickstart

Docstring convention is
https://sphinxcontrib-napoleon.readthedocs.org/
en/latest/example_google.html#example-google

Flask package layout: http://flask.pocoo.org/docs/0.11/patterns/packages/

"""
