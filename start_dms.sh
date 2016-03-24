#!/bin/sh

#---------------------------------------------
# Function to Launch the default browser via Python 
# (-t for new tab, -n for new window)
# Uses an existing browser if it's already open
# After http://stackoverflow.com/a/3124679
#
launch_browser() {
    URL=$1
	python -mwebbrowser -t "$URL" >/dev/null 2>&1
}


#---------------------------------------------
# Main routine follows
echo "Starting DMS daemon and browser"

launch_browser "http://127.0.0.1:5000/"

cd {{DMSHOME}}
# activate the VENV
source venv/bin/activate
python ./run.py
