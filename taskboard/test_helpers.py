# TODO: clean up imports
import json
from django.core.urlresolvers import clear_url_caches, set_urlconf, reverse
from django.http import HttpResponse
from django.conf.urls import patterns
from django.template.loader import render_to_string
from taskboard.views import TaskBoardView, MoveTaskView
import taskboard
from enhance_exception import enhance_exception
from polytesting import SoupSelectionList, WithTestClient, JsonLoader

class BaseGetter(object):

    def __init__(self, testcase):
        pass

    def get_board(self):
        return taskboard.board_loader.get_board()


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


class DjangoClientJsonViewBoardGetter(WithTestClient, JsonLoader, BaseGetter):

    class urls:
        urlpatterns = patterns('',
            # TODO: I'm kinda torn here. I would prefer single url
            # with HTTP_ACCEPT headers, but that might make easy
            # debugging of the app (by inspecting the response in the
            # browser hard
            (r'^json/$', TaskBoardView.as_view(response_format='json')),
        )

    def get_owners(self):
        return self._get_from_parsed_json(
            lambda parsed: parsed.keys())

    def get_states(self):
        return self._get_from_parsed_json(
            lambda parsed: parsed.values()[0].keys())

    def get_tasks_for(self, owner, status):
        return self._get_from_parsed_json(
            lambda parsed: parsed[owner][status])

    def _get_from_parsed_json(self, map_fn):
        parsed = self.json_loads(self.client.get('/json/').content)
        with enhance_exception(lambda: parsed):
            return map_fn(parsed)
