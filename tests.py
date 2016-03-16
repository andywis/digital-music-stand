#!/usr/bin/env python

# Some really noddy unit tests; to get us started...
#
import dmslib.DigitalMusicStand
playlist = dmslib.DigitalMusicStand.DMSPlaylist()


def test_a():
    print("playlist_data is the right length?")
    assert len(playlist.playlist_data) == 6

    print("playlist_data[1] contains the expected values")
    item_1 = playlist.get_page_data(1)

    assert 'type' in item_1
    assert 'path' in item_1
    assert item_1['type'] == "image"
    assert item_1['path'] == "/static/Blues_Scale-1.png"

    print("request for a page outside len(playlist_data) returns a dict with None values")
    assert playlist.get_page_data(99) ==  {'type': None, 'path': None}

    # Page numbers are zero-based.
    assert playlist.get_last_page_number() == 5

    assert playlist.get_image_for_page(1) == "/static/Blues_Scale-1.png"
    assert playlist.get_image_for_page(5) == None

    # THIS SHOULD ASSERT.
    # assert playlist.get_image_for_page(99) == None




test_a()
