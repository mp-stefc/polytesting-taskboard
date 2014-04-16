#!/bin/sh
(python -m unittest discover -s enhance_exception) && \
    ./manage.py test taskboard.tests
exit $?
