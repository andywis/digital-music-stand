#!/usr/bin/env python

from flask import Flask
app = Flask(__name__)
app.secret_key = '1e7ef89dccf05e829a88ca4a8db7f0dca2f2580f7e9e96e0d1bc5d0dd5a'

import dms.views

# Static folder layout:
# Uploads get put into "static/uploads",
# We can then move them around later.
import os
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'static', 'uploads')
SCORES_FOLDER = os.path.join(PROJECT_ROOT, 'static', 'scores')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_URL_PREFIX'] = "/static/uploads/"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB
app.config['SCORES_FOLDER'] = SCORES_FOLDER
app.config['SCORES_URL_PREFIX'] = "/static/scores/"
