
import json
import os
import re
import urllib

from flask import (Flask, abort, flash, redirect, request, render_template,
                   send_from_directory, url_for)
from werkzeug.utils import secure_filename  # for file uploads
import dmslib.utils as utils

from dms import app
import dms.models

# @app.route('^/static/')
# No need for a routing rule for static files;
# it happens automatically


@app.route('/')
def hello_world():
    return render_template('splash-page.html', message='')


@app.route('/p/<int:page_num>')
def show_page(page_num):
    try:
        playlist = dms.models.Playlist()
    except dms.models.PlaylistFileMissingException:
        # If we don't have a playlist, send the user
        # to go make one.
        flash("WARNING: You don't have a playlist. Upload some files "
              "and create one.", 'warning')
        return redirect(url_for('handle_upload'))

    pdata = playlist.get_page_data(page_num, request.args)

    if pdata['num_pages'] == 0:
        # Empty playlist
        flash("WARNING: Your playlist is empty. Please and add "
              "something.", 'warning')
        return redirect(url_for('show_playlist'))

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

    else:
        message = ('<strong style="color:red;">ERROR: Could not '
                   'find any data for page {0}<br><br>'
                   'type={1}, path={2}</strong>'.format(requested_page_num,
                                                        pdata['type'],
                                                        pdata['path']))
        return render_template('splash-page.html', message=message)


@app.route('/upload', methods=['GET', 'POST'])
def handle_upload():
    """
    Display the upload form (GET) and handle file uploads (POST)
    """
    if request.method == 'GET':
        # Upload form needs some JS (upload_form.js) to render the
        # prettier file-upload box.
        return render_template('upload.html',
                               title="Upload file",
                               scripts=['bs', 'jq', 'upload_form.js'],
                               debug='')

    elif request.method == 'POST':
        debug = "we are in the POST section.\n\n"
        filename = "_unknown_"
        form_elt_name = 'fileinp1'

        if form_elt_name not in request.files:
            flash("Oops. Could not see the input file field", 'danger')
            return redirect(request.url)

        fileobj = request.files[form_elt_name]
        if not fileobj:
            flash('Oops. You need to specify a file!', 'danger')
            return redirect(request.url)

        upload_folder = app.config['UPLOAD_FOLDER']

        # un-taint the filename
        filename = secure_filename(fileobj.filename)

        if not utils.is_allowed_file(filename):
            flash("Sorry. I can't upload this type of file.", 'danger')
            return redirect(request.url)
        else:
            debug += "raw filename = %s\n\n" % fileobj.filename

            # TODO: Check filename does not already exist; if it does,
            # modify the name.
            fileobj.save(os.path.join(upload_folder, filename))
            flash(
                "File {0} was successfully uploaded.".format(filename),
                'success')

        # return to uploads page with a 'flash()' message
        return redirect(url_for('uploads_listing'))
       


@app.route('/uploads')
def uploads_listing():
    """ Directory listing for the uploads folder
    See http://stackoverflow.com/a/23724948/6097907

    TODO: a Delete button on the uploads page would be useful.
          Meanwhile, just delete the file from
          $HOME/.dms/digitalmusicstand/dms/static/uploads/
    """
    upload_folder = app.config['UPLOAD_FOLDER']

    if not os.path.exists(upload_folder):
        return abort(404)
    if os.path.isfile(upload_folder):
        return abort(404)

    files = os.listdir(upload_folder)

    return render_template('uploads.html',
                           title="Uploads",
                           prefix=app.config['UPLOAD_URL_PREFIX'],
                           files=files,
                           # scripts=['bs', 'jq'],
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

    TODO: use models.Score to create the metadata.

    TODO: missing "title:" should redirect back to the /uploads page.
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
            # TODO: if the dir already exists, complain in a more useful way
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
        metadata_file = os.path.join(app.config['SCORES_FOLDER'], score_dir,
                                     "metadata.json")
        with open(metadata_file, "w") as output_file:
            json.dump(metadata, output_file, indent=4)

        # TODO: test the modules in utils.
        return render_template('score_created.html',
                               prefix=app.config['SCORES_URL_PREFIX'] + '/' +
                               score_dir + "/",
                               files=files_to_upload,
                               score_name=score_name,
                               score_dir=score_dir,
                               debug="")

    # else: what do we show on 'GET'?


@app.route('/scores')
def scores_listing():
    """ Directory listing for the scores folder
    """
    if not dms.models.Score.scores_folder_exists():
        return abort(404)

    scores_info = []
    scores = dms.models.Score.get_all_scores(perform_integrity_checks=True)
    for score in scores:
        scores_info.append(
            {"name": score.name,
             "num_files": score.num_files,
             "num_files_str": utils.pluralise("%d file", "%d files",
                                              score.num_files)})

    return render_template('scores.html',
                           title="Scores",
                           scores_info=scores_info,
                           debug='')


@app.route('/playlist', methods=['GET'])
def show_playlist():
    """
    Show the current playlist in an editor
    """
    scores_folder = dms.models.Score.get_scores_folder()

    if not dms.models.Score.scores_folder_exists():
        return abort(404)

    score_dirs = os.listdir(scores_folder)

    # List all the available scores
    scores_info = []
    scores = dms.models.Score.get_all_scores(perform_integrity_checks=True)
    for score in scores:
        size_str = utils.pluralise("%d page", "%d pages", score.num_files)
        scores_info.append({'dir': score.folder_name,
                            'name': score.name,
                            'size_str': size_str})

    # List the items in the current playlist
    playlist = dms.models.Playlist(force_create_if_absent=True)
    

    playlist_items = []
    for i in range(0, playlist.get_last_page_number()+1):
        data = playlist.get_page_data(i)
        playlist_items.append({'id': i,
                               # TODO: urlencode path
                               'path': urllib.quote(data['path']),
                               'type': data['type'],
                               'name': data['name'],
                               # TODO: playlist items need the score name or
                               #    dir recorded,
                               # TODO: add the page number of the score.
                               #    e.g. "Score-name (2 pages)" instead of
                               #    "Score-name (image)"
                               })

    return render_template('playlist.html',
                           title="Playlist",
                           scores_info=scores_info,
                           playlist_items=playlist_items,
                           debug='')


@app.route('/edit_playlist', methods=['GET', 'POST'])
def edit_playlist():
    """ handle editing of the playlist

    GET with action=delete & id=NNNN will delete item NNNN
    POST with suitable parameters will insert.

    TODO: A successful POST (Add to playlist) results in a poorly
        styled page. Should redirect to the playlist page with a
        flash message.
    """

    if request.method == 'GET':
        action = request.args.get('action')
        if action and action == "delete":
            # Handle delete of a playlist row.
            row_id = request.args.get('id')
            playlist = dms.models.Playlist()
            playlist.delete_item(row_id, return_json=False, save=True)

            return redirect(url_for('show_playlist'))

        return abort(404)  # incorrect GET data

    if request.method == 'POST':
        # Handle the post data; insert a score into the playlist.
        # [] TODO: Test all the above with a score with 2 or 3 pages.

        playlist = dms.models.Playlist()
        items = []

        # TODO: ensure request.form['insert_after'] is an integer and is
        # in range.

        # Find all the images to be copied, given a Score_dir called
        # "to_insert"
        score_to_insert = dms.models.Score.get_score_by_folder_name(
            request.form['to_insert'])
        num_images = score_to_insert.num_files

        # print "epl_1"
        # print "%r" % score_to_insert.files
        # print "%r" % enumerate(score_to_insert.files)
        for i, image in enumerate(score_to_insert.files):
            # print "epl_2"
            if num_images > 1:
                image_name = "%s (Page %d)" % (score_to_insert.name, i)
            else:
                image_name = score_to_insert.name

            full_img_url = score_to_insert.url_prefix + "/" + image

            item = playlist.create_playlist_item(
                img_url=full_img_url, label=image_name)

            items.append(item)

        playlist.add_items_to_playlist(items, request.form['insert_after'])

        # 'insert_after' is zero-based and listed that way on /playlist
        flash('Score {!s} inserted after item number {}'.format(
                request.form['to_insert'], 
                request.form['insert_after']),
            'success')
        return redirect(url_for('show_playlist'))
