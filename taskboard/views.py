from django.views.generic import TemplateView
from django.views.generic import FormView
from django import forms
from django.core.urlresolvers import reverse
import taskboard


class TaskBoardView(TemplateView):

    template_name = 'taskboard/board.html'

    def get_context_data(self, **kwargs):
        return super(TaskBoardView, self).get_context_data(
            board=taskboard.board_loader.get_board(),
            **kwargs
        )


class MoveTaskView(FormView):
    def dispatch(self, request, success_url_reverse_name):
        self.success_url = reverse(success_url_reverse_name)
        return super(MoveTaskView, self).dispatch(request)

    class form_class(forms.Form):
        # TODO: why do I need to specify it here?
        url = forms.CharField(max_length=255)
        to_owner = forms.CharField(max_length=255)
        to_status = forms.CharField(max_length=255)

        # wouldn't it be nicer if form __init__ kwargs were like get_context in
        # TemplateViews, having the basics and the rest be put into
        # params - and then the form could provide a virtual method
        # override to call, e.g.: _init_extra_params or sg.

    def form_valid(self, form):
        board = taskboard.board_loader.get_board()
        post_data = dict(form.cleaned_data)
        post_data['href'] = post_data.pop('url')  # TODO: unify 
        board.move(**post_data)
        return super(MoveTaskView, self).form_valid(form)
