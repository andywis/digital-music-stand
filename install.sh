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
		echo "INSTALL VIRTUALENV AND THEN COME BACK"
	echo "Exiting"
		exit 1
	fi

    echo "The virtual env is not set up. Will do that now"
    cp pip_requirements.txt $TARGET/pip_requirements.txt
	where_was_i=`pwd`
    cd $TARGET
	virtualenv venv
    source venv/bin/activate
    pip install -r $TARGET/pip_requirements.txt
    rm $TARGET/pip_requirements.txt
    cd $where_was_i
    echo "The virtual env should not be set up"

else
    source $TARGET/venv/bin/activate
fi

mkdir -p $TARGET/config  # where the playlists will be stored
mkdir -p $TARGET/static  # where the images etc will be stored
mkdir -p $TARGET/static/uploads  # where we upload to
mkdir -p $TARGET/dmslib  # where the python libraries stored
mkdir -p $TARGET/templates  # where the HTML templates will be stored

cp run.py $TARGET/run.py
cp -r dmslib/* $TARGET/dmslib
cp -r templates/* $TARGET/templates
cp tests.py $TARGET/tests.py  # optional

# Copy the start script into $HOME
# Note the ':' as the sed delimiter. Works unless $TARGET has a : in.
cat start_dms.sh | sed -e "s:{{DMSHOME}}:$TARGET:" > $HOME/start_dms.sh
chmod +x $HOME/start_dms.sh
