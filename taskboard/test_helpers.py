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


class DjangoClientHtmlViewBoardGetter(WithTestClient, HtmlSoupBoardGetter):

    class urls:
        urlpatterns = patterns('',
            (r'^$', TaskBoardView.as_view()),
        )

    def get_html(self):
        return self.client.get('/').content


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

class HttpTaskMover(WithTestClient, BaseGetter):
    # TODO: convert it into a proper form (new view) with form
    #       to make sure we can get there from the form (second link?)
    #       also, consider a suite of helper cls-s that can be run at 
    #       once (and thus restricting the possible combos - the string
    #       rendering only makes sense for displaying, but not for moving)

    class urls:
        urlpatterns = patterns('',
            (r'^move/$', MoveTaskView.as_view(), {'success_url_reverse_name': 'move_success'}, 'move_task'),
            (r'^success/$', lambda *a, **kw: HttpResponse('OK'), {}, 'move_success'),
        )

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
