from django.views.generic import TemplateView


class TaskBoardView(TemplateView):

    template_name = 'taskboard/board.html'

    def get_context_data(self, **kwargs):
        return super(TaskBoardView, self).get_context_data(
            board=self.get_board(),
            **kwargs
        )

    def get_board(self):
        pass
