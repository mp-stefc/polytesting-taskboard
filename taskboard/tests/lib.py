from django.utils.decorators import classonlymethod
import taskboard


class BaseBoardTestCaseMixin(object):

    def _getAssertEqualityFunc(self, first, second):
        """ see  http://bugs.python.org/issue2578 - by design it
            only uses rich assertion if the two objects are the
            exact same type """
        if isinstance(second, type(first)): # I use the expected, actual convention
            asserter = self._type_equality_funcs.get(type(first))
            if asserter is not None and isinstance(asserter, basestring):
                    return getattr(self, asserter)
        return super(BaseBoardTestCaseMixin, self)._getAssertEqualityFunc(first, second)

    @classonlymethod
    def setUpClass(cls):
        super(BaseBoardTestCaseMixin, cls).setUpClass()
        cls.orig_board_loader = taskboard.board_loader

    @classonlymethod
    def tearDownClass(cls):
        super(BaseBoardTestCaseMixin, cls).tearDownClass()
        taskboard.board_loader = cls.orig_board_loader

    def setUp(self):
        super(BaseBoardTestCaseMixin, self).setUp()
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


class BoardApi(BaseBoardTestCaseMixin):
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
