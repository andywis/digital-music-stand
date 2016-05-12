

"""
file management utilities for DMS
"""

import os
import re


def get_file_safe_name(name):
    """
    create a name that's safe to use in a filing system.
    """
    return re.sub('[^a-zA-Z0-9_]', '_', name)


def get_files_to_upload(inputs):
    """
    generate a list of the filenames to upload,
    based on the names from the form inputs.

    The ones representing files have a "incl__" prefix.

    @param: inputs: a list of form input elements, usually a
        list from request.form
    """
    files_to_upload = []
    for param in inputs.keys():
        if param[0:6] == "incl__" and inputs[param] == "on":
            # remove "incl__" from the front.
            print param
            print param[0:6]
            print param[6:]
            files_to_upload.append(param[6:])
    print files_to_upload
    return files_to_upload


def move_uploads_to_score_dir(files_to_upload, old_folder, new_folder):
    """
    Move a list of files from the uploads folder to the scores folder.

    @param: files_to_upload: a list of files, as generated by get_files_to_upload()
    """
    # TODO: better Exception/error handling
    for ff in files_to_upload:
        if ff != "metadata.json":
            old_path = os.path.join(old_folder, ff)
            new_path = os.path.join(new_folder, ff)
            try:
                os.rename(old_path, new_path)
            except:
                print "Failed to move the files %s" % ff


def pluralise(str, str_pl, num):
    if num ==  1:
        return str % num
    else:
        return str_pl % num