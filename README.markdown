# Taskboard

**Taskboard** is a demo project to illustrate the theory described in my
[End-to-End testing posts][zspe2e].

The problem domain is a task board, where tasks can be moved between
statuses and people.

I've given presentations at DjangoCon EU 2014 and at the Softwerkskammer
Nürnberg user group. The [slides][slides] are available from my [blog][blog]

## Installation instructions

It has been tested with python 2.7 and Ubuntu

    $ git clone git@github.com:zsoldosp/polytesting-taskboard.git
    $ ./setup.sh

To view the application's minimalist UI, run

    $ virtualenv venv-taskboard
    $ source venv-taskboard/bin/activate
    $ export DJANGO_SETTINGS_MODULE=settings
    $ ./manage.py runserver

You can run the tests using

    $ ./run_tests.sh


### Future ideas if this project turns serious

* port it to behave
* enable adding tasks from the board
* add more backends - jira, fogbugz, own model store, etc.
* record moves and task states
* provide reporting / analysis based on moves and states

[zspe2e]: http://blog.zsoldosp.eu/category/end-to-end/
[blog]: http://blog.zsoldosp.eu
[slides]: http://blog.zsoldosp.eu/DjangoConEurope-2014-LT-Polytesting.pdf
