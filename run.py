#!/usr/bin/env python

import json
import os
import re

from flask import (Flask, 
                   abort, 
                   request, 
                   send_from_directory, 
                   )
from flask import render_template

import dmslib.DigitalMusicStand
import dmslib.utils as utils

# ----------------------------------------------------------------------------
#
# TODO
#
# 28/4/2016: we now have a way of showing the uploaded files
#     * add buttons to add the uploaded files to the scores (if they're images)
#     * think about how you might add several "pages" to a single "score"
#     * need to add some meta-data about each img file
#     * add buttons to preview the uploaded file.
#  show the file listing with "preview" buttons next to each file,
#  and a tickbox for each file
#  The meta-data is after an <hr>, and applies to all the ticked
#  files. The "save" button takes all the ticked files and moves them
#  to static/scores/<folder_with_unique_name>, with a metadata.json
#  file.
#
#     * (later?) upload a PDF and process it - it creates several files
#  which can then hook into the above process.
#
#     * once we have files in static/scores, we can list the scores
#  and make a form to create a playlist.
#

# Static folder layout:
# Uploads get put into "static/uploads",
# We can then move them around later.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'static', 'uploads')
SCORES_FOLDER = os.path.join(PROJECT_ROOT, 'static', 'scores')


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_URL_PREFIX'] = "static/uploads/"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB
app.config['SCORES_FOLDER'] = SCORES_FOLDER
app.config['SCORES_URL_PREFIX'] = "static/scores/"
playlist = dmslib.DigitalMusicStand.DMSPlaylist()


# /static/*
# No need for a routing rule for static files;
# it happens automatically

@app.route('/')
def hello_world():
    return render_template('splash-page.html', message='')


@app.route('/p/<int:page_num>')
def show_page(page_num):
    pdata = playlist.get_page_data(page_num)

    requested_page_num = page_num
    previous_page_num = max(page_num - 1, 0)
    next_page_num = min(page_num + 1, playlist.get_last_page_number())

    next_image = None
    if next_page_num > page_num:
        next_image = playlist.get_image_for_page(next_page_num)

    if pdata['type'] in ['image']:
        return render_template('image_stub.html',
                               path=pdata['path'],
                               css_style=pdata['css_style'],
                               prev=previous_page_num,
                               next=next_page_num,
                               next_image=next_image)
    elif pdata['type'] == 'webpage':
        return render_template('iframe_stub.html',
                               url=pdata['path'],
                               css_style=pdata['css_style'],
                               prev=previous_page_num,
                               next=next_page_num,
                               next_image=next_image)

    elif pdata['type'] == 'LEARN_SCALES':
            return render_template('learn_scales.html',
                                   url=pdata['path'],
                                   css_style=pdata['css_style'],
                                   prev=previous_page_num,
                                   next=next_page_num,
                                   next_image=next_image)
    else:
        message = ('<strong style="color:red;">ERROR: Could not '
                   'find any data for page {0}<br><br>'
                   'type={1}, path={2}</strong>'.format(requested_page_num,
                                                        pdata['type'],
                                                        pdata['path']))
        return render_template('splash-page.html', message=message)


@app.route('/uploads')
def uploads_listing():
    """ Directory listing for the uploads folder
    See http://stackoverflow.com/a/23724948/6097907
    """
    upload_folder = app.config['UPLOAD_FOLDER']

    # Return 404 if path doesn't exist
    if not os.path.exists(upload_folder):
        return abort(404)
    if os.path.isfile(upload_folder):
        return abort(404)

    files = os.listdir(upload_folder)

    return render_template('uploads.html',
                           prefix=app.config['UPLOAD_URL_PREFIX'],
                           files=files,
                           debug="")


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """ Display an individual file from the uploads folder.
    """
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route('/create_score', methods=['POST'])
def create_score_from_uploads():
    """ Handle the response from the "/uploads" form, creating
    a new "score"

    TODO: detect that the user entered a score_dir that's already
    been used, and report a more user-friendly message.
    """
    # ensure app.config['SCORES_FOLDER'] exists. (should be
    # created by the installer)
    if not os.path.exists(app.config['SCORES_FOLDER']):
        return abort(404)

    if request.method == 'POST':
        score_name = request.form['score_name']
        score_dir = utils.get_file_safe_name(request.form['score_name'])

        files_to_upload = utils.get_files_to_upload(request.form)

        # create dir
        try:
            os.mkdir(os.path.join(app.config['SCORES_FOLDER'], score_dir))
        except OSError:
            # if the dir exists, complain
            # TODO: complain in a more meaningful way
            return abort(500)

        # move the files.
        #    TODO: Exception handling
        utils.move_uploads_to_score_dir(
            files_to_upload, 
            old_folder=app.config['UPLOAD_FOLDER'], 
            new_folder=os.path.join(app.config['SCORES_FOLDER'], score_dir))
       

        metadata = {
            "score_name": score_name,
            "score_dir": score_dir,
            "files": files_to_upload,  # a list.
        }
        metadata_file = os.path.join(app.config['SCORES_FOLDER'], score_dir, "metadata.json")
        with open(metadata_file, "w") as output_file:
            json.dump(metadata, output_file, indent=4)

        # TODO: test the modules in utils.

        # TODO: return to uploads page with a message saying score_dir created.."
        # return ("name={0}, dir={1}, {2}".format(score_name, score_dir, ' '.join(files_to_upload)))
        return render_template('score_created.html',
                               prefix=app.config['SCORES_URL_PREFIX'] + '/' + score_dir + "/",
                               files=files_to_upload,
                               score_name=score_name,
                               score_dir=score_dir,
                               debug="")

    # else: what do we show on 'GET'?

@app.route('/scores')
def scores_listing():
    """ Directory listing for the scores folder
    """
    scores_folder = app.config['SCORES_FOLDER']

    # Return 404 if path doesn't exist
    if not os.path.exists(scores_folder):
        return abort(404)
    
    score_dirs = os.listdir(scores_folder)

    scores_info = []
    for sdir in score_dirs:
        files = os.listdir(os.path.join(scores_folder, sdir))
        # assume one file is metadata.json; we will ignore that
        num_files = len(files) - 1
        if num_files < 0:
            num_files = 0

        with open(os.path.join(scores_folder, sdir, "metadata.json"), 'r') as md:
            metadata = json.load(md)
        
            score_name = metadata['score_name']
            if num_files != len(metadata['files']):
                print "Oops. Metadata does not match reality"

            scores_info.append({"name": score_name, 
                                "num_files": num_files,
                                "num_files_str": utils.pluralise("%d file", "%d files", num_files)
                                })


    return render_template('scores.html',
                           scores_info=scores_info,
                           debug="")



if __name__ == '__main__':
    app.run(debug=True)

"""
Further Documentation

Flask Tutorial is here:
http://flask.pocoo.org/docs/0.10/quickstart/#quickstart

Docstring convention is
https://sphinxcontrib-napoleon.readthedocs.org/
en/latest/example_google.html#example-google

"""
