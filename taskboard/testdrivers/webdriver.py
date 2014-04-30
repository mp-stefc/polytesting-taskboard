from polytesting import SoupSelectionList, WithTestClient, WithWebdriver, JsonLoader
from selenium.webdriver.common.action_chains import ActionChains
from taskboard.testdrivers import businesslogiconly
from django.conf.urls import patterns
from taskboard.views import TaskBoardView, MoveTaskView
# TODO: if this import is missing, we get a really nasty 500 exception
#       from selenium while dragging the task
#       1) add form_invalid
#       2) enhance javascript failure message to contain more details
#       3) blog about the importance of not hiding error messages
from django.http import HttpResponse


# for now, it's NotImplemented
# TaskAdder = businesslogiconly.TaskAdder
BoardInitializer = businesslogiconly.BoardInitializer

class BoardReader(WithWebdriver):
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


class TaskMover(WithWebdriver):

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
        # TODO: we get the UnexpectedAlertPresentException, but it doesn't 
        #       contain the actual message text there :( look at source code
        #       and contribute if needed...
