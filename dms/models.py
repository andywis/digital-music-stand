
import json
import os

# Import the global "app" Flask context.
from dms import app as APP


class PlaylistFileMissingException(BaseException):
    pass


class Playlist(object):
    """ An object that represents a playlist.
    A playlist is an ordered collection of pages
    of music.
    """
    def __init__(self, filename=None, force_create_if_absent=False):
        """ instantiate a Playlist, including loading data from JSON

        If the playlist file does not exist, we can do one of two
        things: either create it if force_create_if_absent is set 
        to True. Otherwise, we raise a PlaylistFileMissingException.
        """

        # Normally lives in config/active_playlist.json
        if not filename:
            #filename = os.path.join(
            #    os.path.dirname(os.path.abspath(__file__)),
            #    "config", "active_playlist.json")
            filename = Playlist.get_default_playlist_filename()

        self.playlist_filename = filename

        if not os.path.exists(filename):
            if force_create_if_absent:
                playlist_data = []
                with open(filename, "w") as output_file:
                    json.dump(playlist_data, output_file, indent=4)
            else:
                raise PlaylistFileMissingException()

        with open(self.playlist_filename, "r") as playlist_file:
            self.playlist_data = json.load(playlist_file)


    @classmethod
    def get_default_playlist_filename(cls):
        return os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "config", "active_playlist.json")


    def get_page_data(self, page_num, qsargs):
        """
        Obtain the data about a page in the playlist.

        Args:
            page_num (int): the number of the page being requested, this
                being a zero-based index into the playlist_data array
            qsargs (object) The Query String, in the format from 'requests'

        Returns:
            a dict with {'type': '...', 'path': '...'}
            where type is "image" or "webpage"
            and the path is a reference to a file or URL
        """
        if page_num < 0 or page_num >= len(self.playlist_data):
            return {'type': None, 'path': None, 'num_pages': len(self.playlist_data)}
        item = self.playlist_data[page_num]
        css = item.get('css', '')
        if css and qsargs.get('lastpageheight'):
            if css[-1] != ";":
                css += ";"
            css += ";height: %dpx" % int(qsargs.get('lastpageheight'))

        return {'type': item['type'],
                'path': item['path'],
                'css_style': css,
                'name': item['name'],
                'num_pages': len(self.playlist_data),
                }

    def get_last_page_number(self):
        """ Return the number of the last page in the playlist """
        return len(self.playlist_data) - 1

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
            "css": "display: block; margin: 0 auto",
            "name": label,
        }

    def get_image_for_page(self, page_num):
        """Obtain the path to the image for the specified page
        This is used when collecting the Image for the 'next' page,
        so that the browser can pre-fetch the image, making page
        transitions smoother.

        Returns: the path to the image, or None if the item is not
        an image.
        """
        if self.playlist_data[page_num]['type'] == 'image':
            return self.playlist_data[page_num]['path']

    def delete_item(self, page_num, return_json=False, save=True):
        """Delete an item from a playlist (by deleting the row
            from the JSON data)

        @param: page_num = the item number to delete (zero based)
            this should be an int, but may come in as a string
            from a web query.
        @param (bool): return_json - whether to return the JSON. The
            default is to return None
        @param (bool): save - whether to save the file. The default is
            to save the file.
        """
        page_num = int(page_num)
        del self.playlist_data[page_num]

        if save:
            with open(self.playlist_filename, "w") as outfile:
                json.dump(self.playlist_data, outfile, indent=4)

        if return_json:
            return self.playlist_data

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
        insert_after = int(insert_after)
        assert insert_after < len(self.playlist_data)

        insert_point = insert_after + 1
        self.playlist_data[insert_point:insert_point] = items

        with open(self.playlist_filename, "w") as output_file:
            json.dump(self.playlist_data, output_file, indent=4)

        # reload
        with open(self.playlist_filename, "r") as playlist_file:
            self.playlist_data = json.load(playlist_file)


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
        assert len(files) - 1 == len(self.files)
        assert self.folder_name == folder_name