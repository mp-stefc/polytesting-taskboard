from django.test import TestCase


class DisplayingTasks(object):

    def test_constructing_boards_owner_state_order_is_preserved(self):
        self.a_board(owners=['a', 'b', 'c'], states=['x', 'y'])
        self.assertEquals(['a', 'b', 'c'], self.get_owners())
        self.assertEquals(['x', 'y'], self.get_states())
        self.a_board(owners=['y', 'x'], states=['c', 'b', 'a'])
        self.assertEquals(['y', 'x'], self.get_owners())
        self.assertEquals(['c', 'b', 'a'], self.get_states())

    def test_single_user_single_status_single_task_placed_correctly(self):
        self.a_board(owners=['Alice'], states=['Open'])
        self.with_task(owner='Alice', name='Task', href='/1/', status='Open')
        self.assertEquals(
            [{'name': 'Task', 'href': '/1/'}], 
            self.get_tasks_for(owner='Alice', status='Open'))

    def test_two_users_single_status_single_task_placed_correctly(self):
        self.a_board(owners=['Alice', 'Bob'], states=['Open'])
        self.with_task(owner='Alice', name='Task', href='/1/', status='Open')
        self.assertEquals([], self.get_tasks_for(owner='Bob', status='Open'))
        self.assertEquals(
            [{'name': 'Task', 'href': '/1/'}], 
            self.get_tasks_for(owner='Alice', status='Open'))

    def test_single_user_two_statuses_single_task_placed_correctly(self):
        self.a_board(owners=['Cecile'], states=['Open', 'Closed'])
        self.with_task(owner='Cecile', name='Task', href='/1/', status='Open')
        self.assertEquals([], self.get_tasks_for(owner='Cecile', status='Closed'))
        self.assertEquals(
            [{'name': 'Task', 'href': '/1/'}],
            self.get_tasks_for(owner='Cecile', status='Open'))

    def test_two_users_two_statuses_two_tasks_same_owner_same_status(self):
        self.a_board(owners=['Dan', 'Emilia'], states=['Open', 'Closed'])
        self.with_task(name='First', href='1', status='Closed', owner='Dan')
        self.with_task(name='Second', href='2', status='Closed', owner='Dan')
        self.assertEquals([], self.get_tasks_for(owner='Emilia', status='Open'))
        self.assertEquals([], self.get_tasks_for(owner='Emilia', status='Closed'))
        self.assertEquals([], self.get_tasks_for(owner='Dan', status='Open'))
        self.assertEquals(
            [{'name': 'First', 'href': '1'}, {'name': 'Second', 'href': '2'}],
            self.get_tasks_for(owner='Dan', status='Closed'))

    def _getAssertEqualityFunc(self, first, second):
        """ see  http://bugs.python.org/issue2578 - by design it
            only uses rich assertion if the two objects are the
            exact same type """
        if isinstance(second, type(first)): # I use the expected, actual convention
            asserter = self._type_equality_funcs.get(type(first))
            if asserter is not None and isinstance(asserter, basestring):
                    return getattr(self, asserter)
        return super(DisplayingTasks, self)._getAssertEqualityFunc(first, second)

from taskboard import TaskBoard


class InMemoryBoardStorage(object):

    def a_board(self, owners, states):
        self.board = TaskBoard(owners=owners, states=states)

    def with_task(self, owner, name, href, status):
        self.board.add_task(owner=owner, name=name, href=href, status=status)


class DisplayingTasksInMemoryBoard(DisplayingTasks, InMemoryBoardStorage, TestCase):

    def get_tasks_for(self, owner, status):
        return self.board.get_tasks_for(owner, status)

    def get_owners(self):
        return self.board.get_owners()

    def get_states(self):
        return self.board.get_states()

from django.template.loader import render_to_string
from bs4 import BeautifulSoup
from taskboard.test_helpers import SoupSelectionList


class DisplayingTasksInMemoryBoardViewTest(DisplayingTasks, InMemoryBoardStorage, TestCase):

    def get_owners(self):
        return SoupSelectionList(
            self.get_html(), 
            lambda soup: soup.find_all('td', class_='owner'),
            lambda td: td.string
        )

    def get_states(self):
        return SoupSelectionList(
            self.get_html(), 
            lambda soup: soup.find_all('th'),
            lambda th: th.string
        )

    def get_tasks_for(self, owner, status):
        css_selector = 'td a.%s.%s' % (owner, status)
        return SoupSelectionList(
            self.get_html(), 
            lambda soup: soup.select(css_selector),
            lambda a: dict(name=a.string, href=a['href'])
        )

    def get_html(self):
        return render_to_string('taskboard/board.html', {'board': self.board})
