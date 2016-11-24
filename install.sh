#!/bin/bash

TARGET=$HOME/.dms/digitalmusicstand

# TODO: Make sure $TARGET exists and is writable without sudo
#  * [sudo] pip install virtualenv
#  * [sudo] mkdir -p /usr/local/dms
#
# TODO: Test this script on an empty target_dir

mkdir -p $TARGET
if [ ! -d $TARGET ]
then
	echo "Cannot create installation folder $TARGET"
	echo "Exiting"
	exit
fi

if [ ! -d $TARGET/venv ]
then

	if [ -z  `which virtualenv` ]
    then
		echo "Please install virtualenv and then try again."
        echo "(Something like \"sudo pip install virtualenv\")"
	echo "Exiting"
		exit 1
	fi

    echo "Setting up the Virtual environment"
    cp pip_requirements.txt $TARGET/pip_requirements.txt
	where_was_i=`pwd`
    cd $TARGET
	virtualenv venv
    . $TARGET/venv/bin/activate
    pip install -r $TARGET/pip_requirements.txt
    rm $TARGET/pip_requirements.txt
    cd $where_was_i
    echo "The virtual env should now be set up"

else
    . $TARGET/venv/bin/activate
fi

mkdir -p $TARGET/dms  # where the flask app is stored
mkdir -p $TARGET/dms/config  # where the playlists will be stored
mkdir -p $TARGET/dms/static  # where the images etc will be stored
mkdir -p $TARGET/dms/static/uploads  # where we upload to
mkdir -p $TARGET/dms/static/scores  # where scores are kept

cp runserver.py $TARGET/runserver.py
cp -r dms/* $TARGET/dms
cp test_dms.py $TARGET/test_dms.py  # optional

# copy the static content
cp -r static-assets/* $TARGET/dms/static/

# Copy the start script into $HOME
# Note the ':' as the sed delimiter. Works unless $TARGET has a : in.
cat start_dms.sh | sed -e "s:{{DMSHOME}}:$TARGET:" > $HOME/start_dms.sh
chmod +x $HOME/start_dms.sh
