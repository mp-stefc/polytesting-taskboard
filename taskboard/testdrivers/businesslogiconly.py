import taskboard


class BaseGetter(object):

    def __init__(self, testcase):
        pass

    def get_board(self):
        return taskboard.board_loader.get_board()


class BoardInitializer(BaseGetter):

    def given_a_board(self, owners, states, with_tasks=None):
        if with_tasks is None:
            with_tasks = []
        self.board = taskboard.TaskBoard(owners=owners, states=states)
        for task_kwargs in with_tasks:
            self.board.add_task(**task_kwargs)

    def get_board(self):
        return self.board


class TaskAdder(BaseGetter):
    def __init__(self, testcase):
        pass

    def add_task(self, href, owner, status, name):
        self.get_board().add_task(href=href, owner=owner, status=status, name=name)


class BoardReader(BaseGetter):

    def get_tasks_for(self, owner, status):
        return self.get_board().get_tasks_for(owner, status)

    def get_owners(self):
        return self.get_board().get_owners()

    def get_states(self):
        return self.get_board().get_states()


class TaskMover(BaseGetter):

    def move_task(self, url, to_owner, to_status):
        self.get_board().move(url, to_owner, to_status)
