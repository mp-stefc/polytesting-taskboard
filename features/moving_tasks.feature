
Feature: Moving Tasks
	MovingSingleTaskOnTwoByTwoBoard

	Background: Init board
		Given this board 
          | owner  | status  | 
          | Alice  | Open    | 
          | Bob    | Done    | 

	Scenario: Board initialization
		Given the initial task
		  | owner  | status  | name | href  |
          | Alice  | Open    | task | /task |
        Then the single task location is owner='Alice' with status='Open'

    @wip
	Scenario Outline: move single task on 2x2 board
		Given there is a task called <task_name> and <task_href> owned by <prev_owner> with the status <prev_status>
		When I move the task with <task_href> to <new_owner> with <new_status>
        Then the single task location is owner=<new_owner> with status=<new_status>
    
    Examples:
    	|task_name 	|task_href  | prev_owner| prev_status | new_owner	|new_status|
    	|'task'		|'/task'	|'Alice'	|'Open'		  |'Bob'		|'Open'|
    	|'task'		|'/task'	|'Alice'	|'Open'		  |'Alice'		|'Done'|
    	|'task'		|'/task'	|'Alice'	|'Open'		  |'Bob'		|'Done'|
    	|'task'		|'/task'	|'Alice'	|'Open'		  |'Alice'		|'Open'|
    			

