""" 
The unittest steps 
"""

import taskboard

from behave import *


@given(u'this board')
def step_impl(context):
    owners = []
    states = []
    for row in context.table:
        owners.append(row['owner'])
        states.append(row['status'])
    context.board = taskboard.TaskBoard(owners, states)

@given(u'the initial task')
def step_impl(context):
    for row in context.table:
        context.board.add_task(owner=row['owner'], name=row['name'], href = row['href'], status=row['status'] )
    

@given(u'there is a task called \'{t_name}\' and \'{t_href}\' owned by \'{prev_o}\' with the status \'{prev_stat}\'')
def step_impl(context, t_name, t_href, prev_o, prev_stat):
    context.board.add_task(owner=prev_o, name=t_name, href = t_href, status=prev_stat )
    

@when(u'I move the task with \'{url}\' to \'{new_owner}\' with \'{new_stat}\'')
def step_impl(context, url, new_owner, new_stat):
    print(new_owner, new_stat)
    context.board.move(url, new_owner, new_stat)

@then(u'the single task location is owner=\'{owner}\' with status=\'{status}\'')
def step_impl(context, owner, status):
        expected = {}
        actual = {}
        for owner_l in context.board.get_owners():
            expected.setdefault(owner_l, {})
            actual.setdefault(owner_l, {})
            for status_l in context.board.get_states():
                expected[owner_l][status_l] = []
                actual[owner_l][status_l] = context.board.get_tasks_for(owner_l, status_l)
        expected[owner][status] = [{'name': 'task', 'href': '/task'}]
        assert expected == actual

