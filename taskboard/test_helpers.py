import json
from django.core.urlresolvers import clear_url_caches, set_urlconf, reverse
from django.http import HttpResponse
from django.conf.urls import patterns
from django.template.loader import render_to_string
from taskboard.views import TaskBoardView, MoveTaskView
import taskboard
from enhance_exception import enhance_exception
from polytesting import SoupSelectionList, WithTestClient, WithWebdriver, JsonLoader


class BaseGetter(object):

    def __init__(self, testcase):
        pass

    def get_board(self):
        return taskboard.board_loader.get_board()


class PurePythonBoardBuilder(BaseGetter):

    def given_a_board(self, owners, states, with_tasks=None):
        if with_tasks is None:
            with_tasks = []
        self.board = taskboard.TaskBoard(owners=owners, states=states)
        for task_kwargs in with_tasks:
            self.board.add_task(**task_kwargs)

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


class DjangoClientHtmlViewBoardGetter(WithTestClient, HtmlSoupBoardGetter):

    class urls:
        urlpatterns = patterns('',
            (r'^$', TaskBoardView.as_view()),
        )

    def get_html(self):
        return self.client.get('/').content


class SeleniumHtmlViewBoardGetter(WithWebdriver):
    class urls:
        urlpatterns = patterns('',
            (r'^$', TaskBoardView.as_view()),
        )

    def get_owners(self):
        return self.filter_map(
            'td.owner',
            lambda td: td.text
        )

    def get_states(self):
        return self.filter_map(
            'th',
            lambda th: th.text
        )

    def get_tasks_for(self, owner, status):
        def to_href(a):
            href = a.get_attribute('href')
            if href.startswith(self.liveserver_url):
                href = href[len(self.liveserver_url):]
            return href

        return self.filter_map(
            self.get_tasks_selector_css_for(owner, status),
            lambda a: dict(name=a.text, href=to_href(a))
        )

    def get_tasks_selector_css_for(self, owner, status):
        return 'td[owner=%s][state=%s] a' % (owner, status)

    def filter_map(self, css_selector, map_fn):
        full_url = '%s%s' % (self.liveserver_url, '/')
        if self.selenium.current_url != full_url:
            self.selenium.get(full_url)
            self.selenium.implicitly_wait(0.05)
        matches = self.selenium.find_elements_by_css_selector(css_selector)
        return map(map_fn, matches)


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


class PurePythonTaskMover(BaseGetter):

    def move_task(self, url, to_owner, to_status):
        self.get_board().move(url, to_owner, to_status)

class HttpTaskMover(WithTestClient, BaseGetter):

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

from selenium.webdriver.common.action_chains import ActionChains


class SeleniumTaskMover(WithWebdriver):

    class urls:
        urlpatterns = patterns('',
            (r'^move/$', MoveTaskView.as_view(), {'success_url_reverse_name': 'move_success'}, 'move_task'),
            (r'^success/$', lambda *a, **kw: HttpResponse('OK'), {}, 'move_success'),
        )

    def move_task(self, url, to_owner, to_status):
        source = self.selenium.find_element_by_css_selector('a[href="%s"]' % url)
        target = self.selenium.find_element_by_css_selector('td[owner="%s"][state="%s"]' % (to_owner, to_status))
        # TODO: use webelement.is_displayed!
        ActionChains(self.selenium).drag_and_drop(source, target).perform()
