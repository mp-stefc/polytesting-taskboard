from collections import OrderedDict as od

class BoardLoader(object):
    def get_board(self):
        board = TaskBoard(['Jane', 'John'], ['Open', 'Closed'])
        board.add_task(owner='Jane', status='Open', href='/tasks/1/', name='first task')
        return board


board_loader = BoardLoader()


class TaskBoard(object):

    def __init__(self, owners, states):
        self.data = od((o, od((s, []) for s in states)) for o in owners)
        self.href2place = {}
        self.href2name = {}

    def get_tasks_for(self, owner, status):
        return list(map(dict, self._get_tasklist_for(owner, status)))
    
    def add_task(self, owner, name, href, status):
        self._get_tasklist_for(owner=owner, status=status).append(
            {'name': name, 'href': href})
        self.href2place[href] = (owner, status)
        self.href2name[href] = name

    def move(self, href, to_owner, to_status):
        current_pos = self.href2place[href]
        if (to_owner, to_status) == current_pos:
            return
        del self.href2place[href]
        owner, status = current_pos
        tasks = self._get_tasklist_for(owner=owner, status=status)
        task_name = self.href2name[href]
        tasks.remove({'href': href, 'name': task_name})
        self.add_task(owner=to_owner, status=to_status, href=href, name=task_name)

    def get_owners(self):
        return self.data.keys()

    def get_states(self):
        return self.data.values()[0].keys()
        
    def as_nested_dict(self):
        return od((k, od(v)) for (k, v) in self.data.iteritems())

###

    def _get_tasklist_for(self, owner, status):
        return self.data[owner][status]
