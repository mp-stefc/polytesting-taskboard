from django import template
from django.template.loader import render_to_string

register = template.Library()

class TbTaskNode(template.Node):
    def __init__(self, board, owner, status):
        self.board = template.Variable(board)
        self.owner = template.Variable(owner)
        self.status = template.Variable(status)

    def render(self, context):
        board, owner, status = (x.resolve(context) for x in [self.board, self.owner, self.status])
        try:
            tasks = board.get_tasks_for(owner=owner, status=status)
        except Exception as e:
            raise template.TemplateSyntaxError('no matches found for owner %r and status %r - %s %s' % (owner, status, e, type(e)))
        res = render_to_string('taskboard/tasks.html', dict(tasks=tasks, owner=owner, status=status))
        return res

@register.tag('tb_tasks')
def do_tb_tasks(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, board, owner, status = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires 3 arguments: board, owner, name" % token.contents.split()[0])
    return TbTaskNode(board, owner, status)
