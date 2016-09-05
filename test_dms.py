#!/usr/bin/env python
#
# To run these tests, you need "py.test". This is already installed
# in the "target" venv.
#
# (1) activate the venv: source $HOME/.dms/digitalmusicstand/venv/bin/activate
# (2) py.test
#

import pytest

import dms.dmslib.DigitalMusicStand
import dms.dmslib.utils as utils


def test_dms_playlist_obj():
    """ Use a test playlist file for testing."""
    playlist = dms.models.Playlist(filename="dms/test_data/playlist-1.json")

    # playlist_data is the right length?
    assert len(playlist.playlist_data) == 4

    # playlist_data[1] contains the expected values
    item_1 = playlist.get_page_data(1)

    assert 'type' in item_1
    assert 'path' in item_1
    assert item_1['type'] == "image"
    assert item_1['path'] == "second_entry.png"

    # request for a page outside len(playlist_data) should
    # return a dict with None values
    assert playlist.get_page_data(99) == {'type': None, 'path': None}

    # Page numbers are zero-based.
    assert playlist.get_last_page_number() == 3

    assert playlist.get_image_for_page(1) == "second_entry.png"
    assert playlist.get_image_for_page(3) is None  # a web page item

    with pytest.raises(IndexError):
        # should assert, as it's out of range
        x = playlist.get_image_for_page(99)


def test_delete_row_from_playlist():
    """
    test the functionality to handle deleting an entry from the
    playlist
    """
    playlist = dms.dmslib.DigitalMusicStand.DMSPlaylist(
        config_filename="dms/test_data/playlist-1.json")

    # make sure the data's as expected.
    assert len(playlist.playlist_data) == 4
    # Delete the 2nd entry (index=1)
    result = playlist.delete_item(1, return_json=True, save=False)
    assert len(result) == 3

    assert result[0]['path'] == "first_entry.png"
    assert result[1]['path'] == "third_entry.png"
    assert result[2]['path'] == "http://www.example.com/fourth_entry.html"


def test_get_safe_name():
    inp = "this name is &;# unsafe.pdf"
    outp = utils.get_file_safe_name(inp)
    assert outp == "this_name_is_____unsafe_pdf"


def test_pluralise():
    assert utils.pluralise("%d flute", "%d flutes", 1) == "1 flute"
    assert utils.pluralise("%d flute", "%d flutes", 2) == "2 flutes"

    assert utils.pluralise("%d child", "%d children", 2) == "2 children"
    assert utils.pluralise("%d child", "%d children", 2) != "2 childs"
