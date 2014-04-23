#!/bin/sh
python --version 2>&1 | grep 2.7 
exit_code=$?
if [ "$exit_code" != "0" ]]; then
    echo "This only works with Python 2.7"
    exit $exit_code
fi
(python -m unittest discover -s enhance_exception $*) && \
(python -m unittest discover -s polytesting $*) && \
    ./manage.py test taskboard.tests $*
exit $?
