from bs4 import BeautifulSoup
import tempfile
from collections import OrderedDict as od
import os
import json
from django.core.urlresolvers import clear_url_caches, set_urlconf, reverse
from django.conf import settings
from django.http import HttpResponse
from django.conf.urls import patterns
from django.template.loader import render_to_string
from taskboard.views import TaskBoardView, MoveTaskView
import taskboard
import traceback


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
            return traceback.format_exc()
        finally:
            try:
                fd.flush()
                fd.close()
            except UnboundLocalError:
                pass

class BaseGetter(object):

    def __init__(self, testcase):
        pass

    def get_board(self):
        return taskboard.board_loader.get_board()


class PurePythonBoardBuilder(BaseGetter):

    def a_board(self, owners, states):
        self.board = taskboard.TaskBoard(owners=owners, states=states)

    def with_task(self, owner, name, href, status):
        self.board.add_task(owner=owner, name=name, href=href, status=status)

    def get_board(self):
        return self.board


class PurePythonBoardGetter(BaseGetter):

    def get_tasks_for(self, owner, status):
        return self.get_board().get_tasks_for(owner, status)

    def get_owners(self):
        return self.get_board().get_owners()

    def get_states(self):
        return self.get_board().get_states()


class HtmlSoupBoardGetter(BaseGetter):

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


class TemplateRenderingBoardGetter(HtmlSoupBoardGetter):

    def get_html(self):
        return render_to_string('taskboard/board.html', {'board': self.get_board()})


def change_root_urlconf_to(urls):
    # TODO: copied from django.test.SimpleTestCase._urlconf_setup - PR upstairs to make it availabel outside testing too?
    set_urlconf(None)
    settings.ROOT_URLCONF = urls
    clear_url_caches() 


class DjangoClientHtmlViewBoardGetter(HtmlSoupBoardGetter):

    class urls:
        urlpatterns = patterns('',
            (r'^$', TaskBoardView.as_view()),
        )

    def __init__(self, testcase):
        self.client = testcase.client
        change_root_urlconf_to(self.urls)

    def get_html(self):
        return self.client.get('/').content


class DjangoClientJsonViewBoardGetter(BaseGetter):

    class urls:
        urlpatterns = patterns('',
            (r'^json/$', TaskBoardView.as_view(response_format='json')),
        )

    def __init__(self, testcase):
        self.client = testcase.client
        change_root_urlconf_to(self.urls)

    def get_parsed_json(self):
        # TODO: I'm kinda torn here. I would prefer single url
        # with HTTP_ACCEPT headers, but that might make easy
        # debugging of the app (by inspecting the response in the
        # browser hard
        response_body = self.client.get('/json/').content
        try:
            return json.loads(response_body, object_pairs_hook=od)
        except ValueError:
            raise ValueError('%s\n---\n%s' % (traceback.format_exc(), response_body))
    
    def get_owners(self):
        parsed = self.get_parsed_json()
        try:
            return parsed.keys()
        except AttributeError:
            raise AttributeError('\n\n%r\n%s' % (parsed, traceback.format_exc()))

    def get_states(self):
        parsed = self.get_parsed_json()
        try:
            return parsed.values()[0].keys()
        except AttributeError:
            raise AttributeError('\n\n%r\n%s' % (parsed, traceback.format_exc()))

    def get_tasks_for(self, owner, status):
        parsed = self.get_parsed_json()
        try:
            return parsed[owner][status]
        except KeyError:
            raise KeyError('\n\n%r\n%s' % (parsed, traceback.format_exc()))

class PurePythonTaskMover(BaseGetter):

    def move_task(self, url, to_owner, to_status):
        self.get_board().move(url, to_owner, to_status)

class HttpTaskMover(BaseGetter):

    class urls:
        urlpatterns = patterns('',
            (r'^move/$', MoveTaskView.as_view(), {'success_url_reverse_name': 'move_success'}, 'move_task'),
            (r'^success/$', lambda *a, **kw: HttpResponse('OK'), {}, 'move_success'),
        )

    def __init__(self, testcase):
        self.client = testcase.client
        change_root_urlconf_to(self.urls)

    def move_task(self, url, to_owner, to_status):
        post_data = dict(
            url=url, to_owner=to_owner, to_status=to_status)
        url_to_post_to = reverse('move_task')
        response = self.client.post(url_to_post_to, post_data)
        if response.status_code != 302:
            # TODO: introduce a better exception
            raise Exception('expected HTTP 302 on successful post, got %(status)s while posting %(payload)r to %(url)s ' % dict(
                status=response.status_code,
                payload=post_data,
                url=url_to_post_to
            ))
