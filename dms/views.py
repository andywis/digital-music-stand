
import json
import os
import re
import urllib

from flask import (Flask, abort, redirect, request, render_template,
                   send_from_directory, url_for)
import dmslib.DigitalMusicStand
import dmslib.utils as utils
import dmslib.score as score

from dms import app

# /static/*
# No need for a routing rule for static files;
# it happens automatically

@app.route('/')
def hello_world():
    return render_template('splash-page.html', message='')


@app.route('/p/<int:page_num>')
def show_page(page_num):
    playlist = dmslib.DigitalMusicStand.DMSPlaylist()
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
    # Return 404 if path doesn't exist
    if not score.scores_folder_exists(app):
        return abort(404)
    
    scores_info = []
    scores = score.get_all_scores(app, perform_integrity_checks=True)
    for key in score.get_all_scores(app, perform_integrity_checks=True):
        num_files = scores[key]['num_files']
        scores_info.append(
            {"name": key, 
             "num_files": num_files,
             "num_files_str": utils.pluralise("%d file", "%d files", num_files)})


    return render_template('scores.html',
                           scores_info=scores_info,
                           debug='')

@app.route('/playlist', methods=['GET'])
def show_playlist():
    """ Show the current playlist in an editor """
    scores_folder = score.get_scores_folder(app)

    # Return 404 if path doesn't exist
    if not score.scores_folder_exists(app):
        return abort(404)

    score_dirs = os.listdir(scores_folder)

    # List all the available scores
    # TODO: create a subroutine for this. see scores_listing above
    scores_info = []
    for sdir in score_dirs:
        files = os.listdir(os.path.join(scores_folder, sdir))

        with open(os.path.join(scores_folder, sdir, "metadata.json"), 'r') as md:
            metadata = json.load(md)
            # TODO: Verify that score_dr == sdir and warn if not.
            size_str = utils.pluralise("%d page", "%d pages", 
                                       len(metadata['files']))
            scores_info.append({'dir': metadata['score_dir'], 
                                'name': metadata['score_name'],
                                'size_str': size_str})

    # List the items in the current playlist
    playlist = dmslib.DigitalMusicStand.DMSPlaylist()
    playlist_items = []
    for i in range(0, playlist.get_last_page_number()+1):
        data = playlist.get_page_data(i)
        playlist_items.append({'id': i,
                               'path': urllib.quote(data['path']),  # TODO: urlencode
                               'type': data['type'],
                               'name': data['name'],
                               # TODO: playlist items need the score name or dir recorded, 
                               # TODO: add the page number of the score.
                               #    e.g. "Brother CYSMAD (2 pages)" instead of "Brother (image)"
                
                              })

    return render_template('playlist.html',
                           scores_info=scores_info,
                           playlist_items=playlist_items,
                           debug='')


@app.route('/edit_playlist', methods=['GET', 'POST'])
def edit_playlist():
    """ handle editing of the playlist

    GET with action=delete & id=NNNN will delete item NNNN
    POST with suitable parameters will insert.
    """

    if request.method == 'GET':
        action = request.args.get('action')
        if action and action == "delete":
            # Handle delete of a playlist row.
            row_id = request.args.get('id')
            playlist = dmslib.DigitalMusicStand.DMSPlaylist()
            playlist.delete_item(row_id, return_json=False, save=True)

            return redirect(url_for('show_playlist'))

        return abort(404)  # incorrect GET data

    if request.method == 'POST':
        # Handle the post data; insert a score into the playlist.
        # data to add:
        # {"type": "image",
        # "path": location of JPG in static/scores,
        # "css": "max-width: 100%", (depends on image dimensions)
        # "name": name of score (page N)
        # }
        debug_html = "<body>"
        # TODO: Create an entry for a playlist (we should have a method for that)
        score_page_data = {"type":"image", "css": "background-color:yellow"}
        score_page_data['path'] = 'x'
        score_page_data['name'] = 'y'
        debug_html += "<pre>" + json.dumps(score_page_data) + "</pre><br>"
        for field in ["to_insert", "insert_after"]:
            debug_html += "POST {!r} = {!r}<br>".format(field, request.form[field])

        # TODO need a routine in score.xxx to find all the images to be copied, 
        # given a Score_dir called "to_insert"


        # score name is POST['to_insert']
        # location is POST['insert_after'] (an integer) -1 means the start. 0 = after 1st element.
        return debug_html