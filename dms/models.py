
import json
import os

# Import the global "app" Flask context.
from dms import app as APP

class Playlist(object):
    """ An object that represents a playlist.
    A playlist is an ordered collection of pages
    of music.
    """
    # TODO: import the modules in dmslib/DigitalMusicStand.py
    #       DMSPlaylist
    #           get_page_data()
    #           get_last_page_number()
    #           get_image_for_page()
    #           delete_item()
    #
    #           not yet implemented:
    #           load()
    #           save()
    def __init__(self, filename=None):

        # Normally lives in config/active_playlist.json
        if filename:
            assert os.path.exists(filename)
        else:
            filename = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "config", "active_playlist.json")
        self.playlist_filename = filename

    def create_playlist_item(self, img_url, label):
        """ Create the JSON for a playlist entry.

        :param img_url: is the full URL (and hence local pathname)
            to the image
        :param label: is the text to be displayed when showing this
            image/page of score, explaining what it is (i.e. name
            of the piece and page number)
        """
        return {
            "comment": "this is a comment",
            "type": "image",
            "path": img_url,
            "css": "max-width: 70%; display: block; margin: 0 auto",
            "name": label,
        }

    def add_items_to_playlist(self, items, insert_after):
        """ Add one or more playlist `items' (created with 
        create_playlist_item) to an existing playlist, after the item 
        numbered `insert_after'

        :param items: a list of dicts
        :param insert_after: an int or str; the index number identifying
            where to insert the new items.

        The playlist data is a list of dicts, and so is the 'items' 
        variable, so we can just merge the lists as below:
        
        insert_after is zero based, with -1 meaning "at the beginning"
        array sicing syntax effectively means "insert before", so we
        add 1 to "insert_after" to get the correct value.
        
        >>> # Note: in this example, "insert_after == 2"
        >>> x = [1,2,3,7,8,9]
        >>> y = [4,5,6]
        >>> x[3:3] = y
        >>> x
        [1, 2, 3, 4, 5, 6, 7, 8, 9]
        >>>

        """
        with open(self.playlist_filename, "r") as playlist_file:
            playlist_data = json.load(playlist_file)

        insert_after = int(insert_after)
        assert insert_after < len(playlist_data)

        insert_point = insert_after + 1
        playlist_data[insert_point:insert_point] = items

        with open(self.playlist_filename, "w") as output_file:
            json.dump(playlist_data, output_file, indent=4)


class Score(object):
    """ An object representing a musical score, 
    which can consist of several pages (usually JPEGs)
    of music.
    """

    @staticmethod
    def get_scores_folder():
        return APP.config['SCORES_FOLDER']

    @staticmethod
    def scores_folder_exists():
        return os.path.exists(Score.get_scores_folder())

    @staticmethod
    def get_all_scores(perform_integrity_checks=False):
        """ Returns a list of the scores """
        scores_folder = Score.get_scores_folder()
        score_dirs = os.listdir(scores_folder)
        scores_info = []
        for sdir in score_dirs:
            sc = Score.get_score_by_folder_name(sdir)
            if perform_integrity_checks:
                sc.perform_integrity_checks(sdir)

            scores_info.append(sc)

        return scores_info

    @staticmethod
    def get_score_by_folder_name(folder_name):
        scores_folder = Score.get_scores_folder()
        if os.path.exists(os.path.join(scores_folder, folder_name)):
            s = Score()
            s.set_from_folder(folder_name)
            return s

    def __init__(self):
        self.name = ''
        self.num_files = 0
        self.folder_name = ''
        self.files = []

    def set_from_folder(self, folder_name):
        scores_folder = Score.get_scores_folder()
        meta_file = os.path.join(scores_folder, folder_name, "metadata.json")
        with open(meta_file, 'r') as md:
            metadata = json.load(md)
            self.name = metadata['score_name']
            self.num_files = len(metadata['files'])
            self.folder_name = metadata['score_dir']
            self.files = metadata['files']
            self.url_prefix = (APP.config['SCORES_URL_PREFIX'] + 
                '/' + metadata['score_dir'])

            # self.perform_integrity_checks(folder_name):

    def perform_integrity_checks(self, folder_name):
        scores_folder = Score.get_scores_folder()
        files = os.listdir(os.path.join(scores_folder, self.folder_name))
        assert len(files) -1 == len(self.files)
        assert self.folder_name == folder_name