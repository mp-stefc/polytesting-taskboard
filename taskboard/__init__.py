from collections import OrderedDict as od


class TaskBoard(object):

    def __init__(self, owners, states):
        self.data = od((o, od((s, []) for s in states)) for o in owners)

    def get_tasks_for(self, owner, status):
        return list(map(dict, self._get_tasklist_for(owner, status)))
    
    def add_task(self, owner, name, href, status):
        self._get_tasklist_for(owner=owner, status=status).append(
            {'name': name, 'href': href})

    def get_owners(self):
        return self.data.keys()

    def get_states(self):
        return self.data.values()[0].keys()

    def _get_tasklist_for(self, owner, status):
        return self.data[owner][status]
