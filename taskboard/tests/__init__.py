from django.test import TestCase
from taskboard.test_helpers import (
    PurePythonBoardBuilder, PurePythonBoardGetter,
    TemplateRenderingBoardGetter, DjangoClientHtmlViewBoardGetter,
    DjangoClientJsonViewBoardGetter, PurePythonTaskMover, HttpTaskMover,
)
from django.utils.decorators import classonlymethod
import taskboard


class BoardApi(object):

    def _getAssertEqualityFunc(self, first, second):
        """ see  http://bugs.python.org/issue2578 - by design it
            only uses rich assertion if the two objects are the
            exact same type """
        if isinstance(second, type(first)): # I use the expected, actual convention
            asserter = self._type_equality_funcs.get(type(first))
            if asserter is not None and isinstance(asserter, basestring):
                    return getattr(self, asserter)
        return super(BoardApi, self)._getAssertEqualityFunc(first, second)

    @classonlymethod
    def setUpClass(cls):
        super(BoardApi, cls).setUpClass()
        cls.orig_board_loader = taskboard.board_loader

    @classonlymethod
    def tearDownClass(cls):
        super(BoardApi, cls).tearDownClass()
        taskboard.board_loader = cls.orig_board_loader

    def setUp(self):
        super(BoardApi, self).setUp()
        cls = type(self)
        board_builder_objs = []
        for prop_cls_name in filter(lambda name: name.endswith('_cls'), dir(cls)):
            prop_name = prop_cls_name[:-4]
            try:
                tp_to_create = getattr(cls, prop_cls_name)
                obj = tp_to_create(self)
                if hasattr(obj, 'a_board'):
                    board_builder_objs.append(obj)
            except TypeError as e:
                raise TypeError(
                    'could not create instance of %s (from %s.%s) - %s' % (
                        tp_to_create, cls, prop_cls_name, e
                    )
                )
            setattr(self, prop_name, obj)
        self.assertEquals(1, len(board_builder_objs), 'only one helper should build the board, but got multiple: %s' % ', '.join('%s' % type(x) for x in board_builder_objs))
        taskboard.board_loader = board_builder_objs[0]

    def get_tasks_for(self, owner, status):
        return self.getter.get_tasks_for(owner, status)

    def get_owners(self):
        return self.getter.get_owners()

    def get_states(self):
        return self.getter.get_states()

    def a_board(self, owners, states):
        self.builder.a_board(owners, states)

    def with_task(self, owner, name, href, status):
        self.builder.with_task(owner, name, href, status)


class DisplayingTasks(BoardApi):

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


class DisplayingTasksPurePythonBoard(DisplayingTasks, TestCase):
    builder_cls = PurePythonBoardBuilder
    getter_cls = PurePythonBoardGetter


class DisplayingTasksHtmlTemplateRenderingPurePythonBoard(DisplayingTasks, TestCase):
    builder_cls = PurePythonBoardBuilder
    getter_cls = TemplateRenderingBoardGetter


class DisplayingTasksHtmlViewViaDjangoClientPurePythonBoard(DisplayingTasks, TestCase):

    urls = True  # TODO: hack - to ensure that root url conf will be stored by the testcase
    builder_cls = PurePythonBoardBuilder
    getter_cls = DjangoClientHtmlViewBoardGetter


class DisplayingTasksJsonViewViaDjangoClientPurePythonBoard(DisplayingTasks, TestCase):

    urls = True  # TODO: hack - to ensure that root url conf will be stored by the testcase
    builder_cls = PurePythonBoardBuilder
    getter_cls = DjangoClientJsonViewBoardGetter


class MovingSingleTaskOnTwoByTwoBoard(BoardApi):

    def setUp(self):
        super(MovingSingleTaskOnTwoByTwoBoard, self).setUp()
        self.a_board(owners=['Alice', 'Bob'], states=['Open', 'Done'])
        self.with_task(owner='Alice', name='task', href='/task', status='Open')
        self.assert_single_tasks_location_is(owner='Alice', status='Open')

    def test_can_move_to_same_status_different_person(self):
        self.move_task('/task', to_owner='Bob', to_status='Open')
        self.assert_single_tasks_location_is(owner='Bob', status='Open')

    def test_can_move_to_different_status_same_person(self):
        self.move_task('/task', to_owner='Alice', to_status='Done')
        self.assert_single_tasks_location_is(owner='Alice', status='Done')

    def test_can_move_to_differnt_status_different_person(self):
        self.move_task('/task', to_owner='Bob', to_status='Done')
        self.assert_single_tasks_location_is(owner='Bob', status='Done')

    def test_moving_to_self_does_not_move(self):
        self.move_task('/task', to_owner='Alice', to_status='Open')
        self.assert_single_tasks_location_is(owner='Alice', status='Open')

    def test_can_move_multiple_times(self):
        self.move_task('/task', to_owner='Bob', to_status='Done')
        self.move_task('/task', to_owner='Alice', to_status='Open')
        self.assert_single_tasks_location_is(owner='Alice', status='Open')

###

    def move_task(self, url, to_owner, to_status):
        self.mover.move_task(url, to_owner, to_status)

    def assert_single_tasks_location_is(self, owner, status):
        # TODO: this is pretty inefficient in its current form,
        #   wonder whether 
        #   a) this neccessiates using caching headers
        #   b) makes me "cache" in the test - self.change_... method
        #      resets self.actual_board and this method only initializes
        expected = {}
        actual = {}
        for owner_l in self.get_owners():
            expected.setdefault(owner_l, {})
            actual.setdefault(owner_l, {})
            for status_l in self.get_states():
                expected[owner_l][status_l] = []
                actual[owner_l][status_l] = self.get_tasks_for(owner_l, status_l)
        expected[owner][status] = [{'name': 'task', 'href': '/task'}]
        self.assertEquals(expected, actual)

class MovingTasksPurePythonBoard(MovingSingleTaskOnTwoByTwoBoard, TestCase):
    builder_cls = PurePythonBoardBuilder
    getter_cls = PurePythonBoardGetter
    mover_cls = PurePythonTaskMover

class MovingTasksHtmlViaDjangoClientViewPurePythonBoard(MovingSingleTaskOnTwoByTwoBoard, TestCase):

    urls = True  # TODO: hack - to ensure that root url conf will be stored by the testcase
    builder_cls = PurePythonBoardBuilder
    getter_cls = PurePythonBoardGetter  # DjangoClientHtmlViewBoardGetter
    mover_cls = HttpTaskMover


