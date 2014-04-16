from collections import OrderedDict as od
import json
import os
import tempfile
import traceback
from bs4 import BeautifulSoup
from enhance_exception import enhance_exception


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
