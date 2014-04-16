#!/bin/sh
(python -m unittest discover -s enhance_exception $*) && \
(python -m unittest discover -s polytesting $*) && \
    ./manage.py test taskboard.tests $*
exit $?
