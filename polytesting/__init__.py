from collections import OrderedDict as od
import json
import os
import tempfile
import traceback
from bs4 import BeautifulSoup
from enhance_exception import enhance_exception
from django.utils.decorators import classonlymethod
from django.conf import settings
from django.test import LiveServerTestCase
from django.core.urlresolvers import clear_url_caches, set_urlconf
from django.conf.urls import patterns
from selenium.webdriver.phantomjs.webdriver import WebDriver


class SoupSelectionList(list):
    def __init__(self, html, filter_, map_):
        """ A list with a custom __repr__ to be used in unittest assertions
            the first call to __repr__ dumps the list's content to a file
            and thus potentially giving better debug diagnostics for the
            test failure.

            Usage:
            >>> repr(SoupSelectionList(
            '<li><a href="/home'>Home</a></li><li><a class="current" href="/buy">Buy</a></li>',
            ... lambda soup: soup.find_all('a', class_='current'),
            ... lambda a: a.string))
            /path/to/file [u'Buy']
        """
        self.html = html
        self.soup = BeautifulSoup(self.html)
        self.extend(map(map_, filter_(self.soup)))
        self.dumped_file_name = None

    def __repr__(self):
        """ this is only called when the comparison failes, 
            so in a way it is lazy. However, unittest.util.safe_repr
            (used in assertSequenceEqual
            will truncate it at _MAX_LENGTH, and if we prefix the
            list with text will mess with the standard output
            of the test diff - e.g.:

                - [{'href': '/1/', 'name': 'Task'}]
                + /path/to/html/file [{'href': u'/1/', 'name': u'Task'}, 1]

            or

                - [{'href': '/1/', 'name': 'Task'}]
                + /path/to/file [{'href': u'/1/', 'name': u'Task'}, 1]
                ? ++++++++++++++          +               +       +++

            vs.

                - [{'href': '/1/', 'name': 'Task'}]
                + [{'href': u'/1/', 'name': u'Task'}, 1]
                ?           +               +       +++
        """
        # TODO: extract to own project and test above behavior
        return self._dump_to_file() + list.__repr__(self)

    def _dump_to_file(self):
        if self.dumped_file_name is None:
            self.dumped_file_name = self._do_dump_to_file()
        return self.dumped_file_name

    def _do_dump_to_file(self):
        # TODO: encoding
        try:
            f, fname = tempfile.mkstemp()
            fd = os.fdopen(f, 'w')
            # TODO: use some reflection to include the filter/map lambdas in the output
            fd.write(self.html)
            return fname + ' '
        except Exception:
            return traceback.format_exc()
        finally:
            try:
                fd.flush()
                fd.close()
            except UnboundLocalError:
                pass


class WithTestClient(object):

    def __init__(self, testcase):
        self.client = testcase.client


class WithWebdriver(object):
    needs_live_server = True
    liveserver_url = None

    def __init__(self, testcase):
        pass


class JsonLoader(object):

    def json_loads(self, content):
        with enhance_exception(lambda: content):
            return json.loads(content, object_pairs_hook=od)

class AllowRichEqualityAssertions(object):
    def _getAssertEqualityFunc(self, first, second):
        """ see  http://bugs.python.org/issue2578 - by design it
            only uses rich assertion if the two objects are the
            exact same type """
        if isinstance(second, type(first)): # I use the expected, actual convention
            asserter = self._type_equality_funcs.get(type(first))
            if asserter is not None and isinstance(asserter, basestring):
                    return getattr(self, asserter)
        return super(AllowRichEqualityAssertions, self)._getAssertEqualityFunc(first, second)


class PolyTestCase(AllowRichEqualityAssertions):
    @classonlymethod
    def setUpClass(cls):
        super(PolyTestCase, cls).setUpClass()
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
        super(PolyTestCase, cls).tearDownClass()
        cls.stop_liveserver_if_needed()

    @classonlymethod
    def get_test_api_class_names(cls):
        return filter(lambda name: name.endswith('_cls'), dir(cls))

    def setUp(self):
        super(PolyTestCase, self).setUp()
        cls = type(self)
        cls.reset_webdriver_if_needed()
        polytest_created_objects = []
        for prop_cls_name in cls.get_test_api_class_names():
            prop_name = prop_cls_name[:-4]
            try:
                tp_to_create = getattr(cls, prop_cls_name)
                obj = tp_to_create(self)
                if hasattr(obj, 'given_a_board'):
                    polytest_created_objects.append(obj)
            except TypeError as e:
                raise TypeError(
                    'could not create instance of %s (from %s.%s) - %s' % (
                        tp_to_create, cls, prop_cls_name, e
                    )
                )
            setattr(self, prop_name, obj)
        self.polytest_created_objects = polytest_created_objects 

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
