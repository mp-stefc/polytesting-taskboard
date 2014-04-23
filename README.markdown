# Taskboard

**Taskboard** is a demo project to illustrate the theory described in my
[End-to-End testing posts][zspe2e].

The problem domain is a Kanban board, where tasks can be moved between
statuses and people.

## Installation instructions

    $ git clone ....
    $ cd taskboard
    $ virtualenv taskboard-venv
    $ source taskboard-venv/bin/activate
    $ pip install -r requirements.txt

Now you can run the tests using

    $ ./run_tests.sh

## Roadmap

to illustrate the points needed for explaining the concept:

* add validations (nonexistent task, nonexistent owner, status, etc.)
* add html/json response (preparing for API)
* JS drag-n-drop UI
* add phantomjs/selenium tests

### Future ideas if this project turns serious

* enable adding tasks from the board
* add more backends - jira, fogbugz, own model store, etc.
* record moves and task states
* provide reporting / analysis based on moves and states

[zspe2e]: http://blog.zsoldosp.eu/category/end-to-end/
