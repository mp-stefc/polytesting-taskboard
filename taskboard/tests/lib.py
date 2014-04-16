from django.utils.decorators import classonlymethod
import taskboard
from polytesting import PolyTestCase


class BoardApi(PolyTestCase):

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
        board_builder_objs = list(o for o in self.polytest_created_objects if hasattr(o, 'given_a_board'))
        self.assertEquals(1, len(board_builder_objs), 'only one helper should build the board, but got multiple: %s' % ', '.join('%s' % type(x) for x in board_builder_objs))
        taskboard.board_loader = board_builder_objs[0]


    def get_tasks_for(self, owner, status):
        return self.getter.get_tasks_for(owner, status)

    def get_owners(self):
        return self.getter.get_owners()

    def get_states(self):
        return self.getter.get_states()

    def given_a_board(self, owners, states, with_tasks=None):
        self.builder.given_a_board(owners, states, with_tasks)
