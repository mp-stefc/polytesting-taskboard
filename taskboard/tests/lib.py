from django.utils.decorators import classonlymethod
from django.test import LiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
import taskboard
from django.core.urlresolvers import clear_url_caches, set_urlconf
from django.conf.urls import patterns
from django.conf import settings


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
        cls.start_liveserver_if_needed()
        cls.setup_root_urlconf_if_needed()

    @classonlymethod
    def setup_root_urlconf_if_needed(cls):
        urlpatterns = list(
            test_cls.urls.urlpatterns 
            for test_cls in cls.get_test_api_classes()
            if hasattr(test_cls, 'urls'))
        consolidated = reduce(lambda a, b: a + b, urlpatterns, [])
        class urls:
            urlpatterns = consolidated
        cls.urls = urls

        def change_root_urlconf_to(urls):
            # TODO: copied from django.test.SimpleTestCase._urlconf_setup - PR upstairs to make it availabel outside testing too?
            set_urlconf(None)
            settings.ROOT_URLCONF = urls
            clear_url_caches() 

        change_root_urlconf_to(cls.urls)

    @classonlymethod
    def tearDownClass(cls):
        super(BaseBoardTestCaseMixin, cls).tearDownClass()
        taskboard.board_loader = cls.orig_board_loader
        cls.stop_liveserver_if_needed()

    def setUp(self):
        super(BaseBoardTestCaseMixin, self).setUp()
        cls = type(self)
        cls.reset_webdriver_if_needed()
        board_builder_objs = []
        for prop_cls_name in cls.get_test_api_class_names():
            prop_name = prop_cls_name[:-4]
            try:
                tp_to_create = getattr(cls, prop_cls_name)
                obj = tp_to_create(self)
                if hasattr(obj, 'given_a_board'):
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

    @classonlymethod
    def get_test_api_class_names(cls):
        return filter(lambda name: name.endswith('_cls'), dir(cls))

    @classonlymethod
    def get_test_api_classes(cls):
        return map(
            lambda name: getattr(cls, name),
            cls.get_test_api_class_names())

    @classonlymethod
    def start_liveserver_if_needed(cls):
        cls.liveserver_url = None
        for api_cls in cls.get_test_api_classes():
            if not getattr(api_cls, 'needs_live_server', False):
                continue
            if cls.liveserver_url is None:
                LiveServerTestCase.setUpClass()
                cls.selenium = WebDriver()
                # inlined from LiveServerTestCase
                cls.liveserver_url = 'http://%s:%s' % (
                    LiveServerTestCase.server_thread.host, LiveServerTestCase.server_thread.port)
            api_cls.server_thread = LiveServerTestCase.server_thread
            api_cls.selenium = cls.selenium
            api_cls.liveserver_url = cls.liveserver_url
        cls.has_liveserver = cls.liveserver_url is not None
        
    @classonlymethod
    def stop_liveserver_if_needed(cls):
        if cls.has_liveserver:
            LiveServerTestCase.tearDownClass()
            cls.selenium.quit()

    @classonlymethod
    def reset_webdriver_if_needed(cls):
        if cls.has_liveserver:
            cls.selenium.get('about:blank')


class BoardApi(BaseBoardTestCaseMixin):
    def get_tasks_for(self, owner, status):
        return self.getter.get_tasks_for(owner, status)

    def get_owners(self):
        return self.getter.get_owners()

    def get_states(self):
        return self.getter.get_states()

    def given_a_board(self, owners, states, with_tasks=None):
        self.builder.given_a_board(owners, states, with_tasks)
