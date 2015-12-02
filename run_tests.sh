#!/bin/bash
readonly PROGDIR=$(dirname $(readlink -m $0))
cd $PROGDIR
python --version 2>&1 | grep 2.7 
exit_code=$?
if [ "$exit_code" != "0" ]; then
    echo "This only works with Python 2.7"
    exit $exit_code
fi
UNIQ_ID=$(python -c"print hash('${PROGDIR}') % 2**13")
XVFB_DISPLAY_NUMBER=$UNIQ_ID
xvfb_running() {
   ps aux | grep '[0-9]\+:[0-9]\+ Xvfb' | grep -v grep | grep ${XVFB_DISPLAY_NUMBER}
}

start_xvfb() {
   screen -A -m -d -S Xvfb-taskboard-display-${XVFB_DISPLAY_NUMBER} Xvfb :${XVFB_DISPLAY_NUMBER} -fbdir ${PROGDIR} -ac -noreset -screen 0 1024x768x8 &
}

xvfb_running || start_xvfb || exit $?
source venv-taskboard/bin/activate || exit $?
export DJANGO_SETTINGS_MODULE=settings
export DISPLAY=:${XVFB_DISPLAY_NUMBER}
(python -m unittest discover -s enhance_exception $*) && \
(python -m unittest discover -s polytesting $*) && \
    ./manage.py test taskboard.tests $*
exit $?
