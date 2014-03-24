from taskboard.tests.lib import BoardApi


class DisplayingTasks(BoardApi):

    def test_constructing_boards_owner_state_order_is_preserved(self):
        self.a_board(owners=['a', 'b', 'c'], states=['x', 'y'])
        self.assertEquals(['a', 'b', 'c'], self.get_owners())
        self.assertEquals(['x', 'y'], self.get_states())
        self.a_board(owners=['y', 'x'], states=['c', 'b', 'a'])
        self.assertEquals(['y', 'x'], self.get_owners())
        self.assertEquals(['c', 'b', 'a'], self.get_states())

    def test_single_user_single_status_single_task_placed_correctly(self):
        self.a_board(owners=['Alice'], states=['Open'])
        self.with_task(owner='Alice', name='Task', href='/1/', status='Open')
        self.assertEquals(
            [{'name': 'Task', 'href': '/1/'}], 
            self.get_tasks_for(owner='Alice', status='Open'))

    def test_two_users_single_status_single_task_placed_correctly(self):
        self.a_board(owners=['Alice', 'Bob'], states=['Open'])
        self.with_task(owner='Alice', name='Task', href='/1/', status='Open')
        self.assertEquals([], self.get_tasks_for(owner='Bob', status='Open'))
        self.assertEquals(
            [{'name': 'Task', 'href': '/1/'}], 
            self.get_tasks_for(owner='Alice', status='Open'))

    def test_single_user_two_statuses_single_task_placed_correctly(self):
        self.a_board(owners=['Cecile'], states=['Open', 'Closed'])
        self.with_task(owner='Cecile', name='Task', href='/1/', status='Open')
        self.assertEquals([], self.get_tasks_for(owner='Cecile', status='Closed'))
        self.assertEquals(
            [{'name': 'Task', 'href': '/1/'}],
            self.get_tasks_for(owner='Cecile', status='Open'))

    def test_two_users_two_statuses_two_tasks_same_owner_same_status(self):
        self.a_board(owners=['Dan', 'Emilia'], states=['Open', 'Closed'])
        self.with_task(name='First', href='1', status='Closed', owner='Dan')
        self.with_task(name='Second', href='2', status='Closed', owner='Dan')
        self.assertEquals([], self.get_tasks_for(owner='Emilia', status='Open'))
        self.assertEquals([], self.get_tasks_for(owner='Emilia', status='Closed'))
        self.assertEquals([], self.get_tasks_for(owner='Dan', status='Open'))
        self.assertEquals(
            [{'name': 'First', 'href': '1'}, {'name': 'Second', 'href': '2'}],
            self.get_tasks_for(owner='Dan', status='Closed'))
