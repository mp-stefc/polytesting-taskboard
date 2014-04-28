from taskboard.tests.lib import BoardApi


class AddingTasks(BoardApi):

    def test_single_cell_board_adding_one_new_task(self):
        self.given_a_board(owners=['Jane'], states=['Open'])
        self.add_task(owner='Jane', name='Task I.', href='/123', status='Open')
        self.assertEquals(
            [{'name': 'Task I.', 'href': '/123'}], 
            self.get_tasks_for(owner='Jane', status='Open'))

    def test_single_cell_board_adding_two_new_tasks(self):
        self.given_a_board(owners=['Jack'], states=['Todo'])
        self.add_task(owner='Jack', name='First Task', href='/1', status='Todo')
        self.add_task(owner='Jack', name='Second Task', href='/2nd', status='Todo')
        self.assertEquals(
            [{'name': 'First Task', 'href': '/1'}, 
             {'name': 'Second Task', 'href': '/2nd'}], 
            self.get_tasks_for(owner='Jack', status='Todo'))

    def test_multiple_owners_and_states_createing_tasks_to_multiple(self):
        self.given_a_board(owners=['Alice', 'Bob', 'Cecile'], states=['Open', 'Done'])
        # TODO: does add really need a href param?
        self.add_task(owner='Cecile', name='first', href='/1', status='Open')
        self.add_task(owner='Alice', name='second', href='/2', status='Open')
        self.add_task(owner='Cecile', name='third', href='/3', status='Done')
        self.add_task(owner='Bob', name='fourth', href='/4', status='Done')
        self.add_task(owner='Bob', name='fifth', href='/5', status='Open')
        self.add_task(owner='Bob', name='sixth', href='/6', status='Open')

        self.assertEquals(
            [{'name': 'second', 'href': '/2'}], 
            self.get_tasks_for(owner='Alice', status='Open'))
        self.assertEquals(
            [], 
            self.get_tasks_for(owner='Alice', status='Done'))

        self.assertEquals(
            [{'name': 'fifth', 'href': '/5'}, 
             {'name': 'sixth', 'href': '/6'}], 
            self.get_tasks_for(owner='Bob', status='Open'))
        self.assertEquals(
            [{'name': 'fourth', 'href': '/4'}], 
            self.get_tasks_for(owner='Bob', status='Done'))

        self.assertEquals(
            [{'name': 'first', 'href': '/1'}], 
            self.get_tasks_for(owner='Cecile', status='Open'))
        self.assertEquals(
            [{'name': 'third', 'href': '/3'}], 
            self.get_tasks_for(owner='Cecile', status='Done'))
