from bs4 import BeautifulSoup
import tempfile
import os


class SoupSelectionList(list):
    def __init__(self, html, filter_, map_):
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
        except Exception as e:
            return str(e)
        finally:
            try:
                fd.flush()
                fd.close()
            except UnboundLocalError:
                pass
