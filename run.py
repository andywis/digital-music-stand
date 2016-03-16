#!/usr/bin/env python

from flask import Flask
from flask import render_template

import dmslib.DigitalMusicStand

app = Flask(__name__)

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
    next_page_num = min(page_num + 1, playlist.get_last_page_number() )

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
    else:
        message = ('<strong style="color:red;">ERROR: Could not '
                  'find any data for page {0}<br><br>'
                  'type={1}, path={2}</strong>'.format(requested_page_num,
                                                pdata['type'],
                                                pdata['path']))
        return render_template('splash-page.html', message=message)

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

