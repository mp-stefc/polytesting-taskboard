#!/bin/bash
readonly PROGDIR=$(dirname $(readlink -m $0))
cd $PROGDIR
sudo apt-get install firefox xvfb screen phantomjs
virtualenv --no-site-packages venv-taskboard
source venv-taskboard/bin/activate
pip install -Ur requirements.txt
