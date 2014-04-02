from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.conf.urls import patterns
from django.http import HttpResponse
from taskboard.views import TaskBoardView, MoveTaskView
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    (r'^$', TaskBoardView.as_view()),
    (r'^move/$', MoveTaskView.as_view(), {'success_url_reverse_name': 'move_success'}, 'move_task'),
    (r'^success/$', lambda *a, **kw: HttpResponse('OK'), {}, 'move_success'),
)
