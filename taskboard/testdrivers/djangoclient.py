from django.conf.urls import patterns
from django.core.urlresolvers import reverse
from polytesting import SoupSelectionList, WithTestClient
from taskboard.views import TaskBoardView, MoveTaskView
from django.http import HttpResponse
from taskboard.testdrivers import businesslogiconly


BoardInitializer = businesslogiconly.BoardInitializer


class BoardReader(WithTestClient):

    class urls:
        urlpatterns = patterns('',
            (r'^$', TaskBoardView.as_view()),
        )

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

    def get_html(self):
        return self.client.get('/').content


class TaskMover(WithTestClient):
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
