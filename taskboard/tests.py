from django.test import TestCase
from taskboard.test_helpers import (
   PurePythonBoardBuilder, PurePythonBoardGetter,
   TemplateRenderingBoardGetter, DjangoClientViewBoardGetter,
)

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

###

    def _getAssertEqualityFunc(self, first, second):
        """ see  http://bugs.python.org/issue2578 - by design it
            only uses rich assertion if the two objects are the
            exact same type """
        if isinstance(second, type(first)): # I use the expected, actual convention
            asserter = self._type_equality_funcs.get(type(first))
            if asserter is not None and isinstance(asserter, basestring):
                    return getattr(self, asserter)
        return super(DisplayingTasks, self)._getAssertEqualityFunc(first, second)

    def setUp(self):
        super(DisplayingTasks, self).setUp()
        self.builder = self.builder_cls(self)
        self.getter = self.getter_cls(self)

    def get_tasks_for(self, owner, status):
        return self.getter.get_tasks_for(
            self.builder.get_board(), owner, status)

    def get_owners(self):
        return self.getter.get_owners(self.builder.get_board())

    def get_states(self):
        return self.getter.get_states(self.builder.get_board())

    def a_board(self, owners, states):
        self.builder.a_board(owners, states)

    def with_task(self, owner, name, href, status):
        self.builder.with_task(owner, name, href, status)


class DisplayingTasksInMemoryBoard(DisplayingTasks, TestCase):
    builder_cls = PurePythonBoardBuilder
    getter_cls = PurePythonBoardGetter


class DisplayingTasksTemplateRenderingInMemoryBoardViewTest(DisplayingTasks, TestCase):
    builder_cls = PurePythonBoardBuilder
    getter_cls = TemplateRenderingBoardGetter


class DisplayingTasksViaDjangoClientInMemoryBoardViewTest(DisplayingTasks, TestCase):

    urls = True  # TODO: hack - to ensure that root url conf will be stored by the testcase
    builder_cls = PurePythonBoardBuilder
    getter_cls = DjangoClientViewBoardGetter
