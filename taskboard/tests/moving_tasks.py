from taskboard.tests.lib import BoardApi


class MovingSingleTaskOnTwoByTwoBoard(BoardApi):

    def setUp(self):
        super(MovingSingleTaskOnTwoByTwoBoard, self).setUp()
        self.given_a_board(
            owners=['Alice', 'Bob'], states=['Open', 'Done'],
            with_tasks=[{
                'owner': 'Alice', 'status': 'Open',
                'name': 'task', 'href': '/task'
            }]
        )
        self.assert_single_tasks_location_is(owner='Alice', status='Open')

    def test_can_move_to_same_status_different_person(self):
        self.move_task('/task', to_owner='Bob', to_status='Open')
        self.assert_single_tasks_location_is(owner='Bob', status='Open')

    def test_can_move_to_different_status_same_person(self):
        self.move_task('/task', to_owner='Alice', to_status='Done')
        self.assert_single_tasks_location_is(owner='Alice', status='Done')

    def test_can_move_to_differnt_status_different_person(self):
        self.move_task('/task', to_owner='Bob', to_status='Done')
        self.assert_single_tasks_location_is(owner='Bob', status='Done')

    def test_moving_to_self_does_not_move(self):
        self.move_task('/task', to_owner='Alice', to_status='Open')
        self.assert_single_tasks_location_is(owner='Alice', status='Open')

    def test_can_move_multiple_times(self):
        self.move_task('/task', to_owner='Bob', to_status='Done')
        # TODO: this assert is only here to deal with timing issues
        #       in selenium tests. Since it's a selenium issue, and
        #       the purpose of this project is to demonstrate polytesting
        #       I'm OK with this HACK
        self.assert_single_tasks_location_is(owner='Bob', status='Done')
        self.move_task('/task', to_owner='Alice', to_status='Open')
        self.assert_single_tasks_location_is(owner='Alice', status='Open')

###

    def move_task(self, url, to_owner, to_status):
        self.mover.move_task(url, to_owner, to_status)

    def assert_single_tasks_location_is(self, owner, status):
        # TODO: this is pretty inefficient in its current form,
        #   wonder whether 
        #   a) this neccessiates using caching headers
        #   b) makes me "cache" in the test - self.change_... method
        #      resets self.actual_board and this method only initializes
        expected = {}
        actual = {}
        for owner_l in self.get_owners():
            expected.setdefault(owner_l, {})
            actual.setdefault(owner_l, {})
            for status_l in self.get_states():
                expected[owner_l][status_l] = []
                actual[owner_l][status_l] = self.get_tasks_for(owner_l, status_l)
        expected[owner][status] = [{'name': 'task', 'href': '/task'}]
        self.assertEquals(expected, actual)
