"""
Score utilities

TODO: how can we avoid having to throw 'app' around?
TODO: rename the module? dms_score?
"""
import os
import json


def get_scores_folder(app):
    return app.config['SCORES_FOLDER']


def scores_folder_exists(app):
    return os.path.exists(get_scores_folder(app))


def get_all_scores(app, perform_integrity_checks=False):
    """ Returns a dict of the scores """
    scores_folder = get_scores_folder(app)
    score_dirs = os.listdir(scores_folder)
    scores_info = {}
    for sdir in score_dirs:
        
        with open(os.path.join(scores_folder, sdir, "metadata.json"), 'r') as md:
            metadata = json.load(md)

        # Integrity checks
        if perform_integrity_checks:
            files = os.listdir(os.path.join(scores_folder, sdir))
            assert len(files) - 1 == len(metadata['files']), "Score data error in {}".format(sdir)
            assert metadata['score_dir'] == sdir, "Score data error in {}".format(sdir)

        scores_info[metadata['score_name']] = {
                    'name': metadata['score_name'],
                    'num_files': len(metadata['files']),
                    'score_dir': metadata['score_dir']
            }

    return scores_info