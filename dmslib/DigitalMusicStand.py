
import json
import os

class DMSPlaylist(object):
    def __init__(self):
        """
        A DigitalMusicStand Playlist object holds the config 
        and knows how to give you the data for a specific page.

        N.B. The play_list file is relative to the "run" file.
        """
        config_filename = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "config", "active_playlist.json")

        with open(config_filename, "r") as playlist_file:
            self.playlist_data = json.load(playlist_file)


    def get_page_data(self, page_num):
        """
        Obtain the data about a page in the playlist.

        Args:
            page_num (int): the number of the page being requested, this
                being a zero-based index into the playlist_data array

        Returns:
            a dict with {'type': '...', 'path': '...'}
            where type is "image" or "webpage"
            and the path is a reference to a file or URL
        """
        if page_num < 0 or page_num >= len(self.playlist_data):
            return {'type': None, 'path': None}
        item = self.playlist_data[page_num]
        return {'type': item['type'],
                'path': item['path'],
                'css_style': item.get('css', ''),
                }

    def get_last_page_number(self):
        """ Return the number of the last page in the playlist """
        return len(self.playlist_data) - 1

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

