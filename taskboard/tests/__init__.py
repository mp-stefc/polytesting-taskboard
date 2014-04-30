from django.test import TestCase
from taskboard.test_helpers import (
    TemplateRenderingBoardGetter,
    DjangoClientJsonViewBoardGetter,
)
from taskboard.testdrivers import businesslogiconly, webdriver, djangoclient
from taskboard.tests.displaying_tasks import DisplayingTasks
from taskboard.tests.moving_tasks import MovingSingleTaskOnTwoByTwoBoard
from taskboard.tests.adding_tasks import AddingTasks


class DisplayingTasksBusinessLogicOnlyBoard(DisplayingTasks, TestCase):
    builder_cls = businesslogiconly.BoardInitializer
    getter_cls = businesslogiconly.BoardReader


class DisplayingTasksHtmlTemplateRenderingBusinessLogicOnlyBoard(DisplayingTasks, TestCase):
    builder_cls = businesslogiconly.BoardInitializer
    getter_cls = TemplateRenderingBoardGetter


class DisplayingTasksHtmlViewViaDjangoClientBusinessLogicOnlyBoard(DisplayingTasks, TestCase):

    urls = True  # TODO: hack - to ensure that root url conf will be stored by the testcase
    builder_cls = djangoclient.BoardInitializer
    getter_cls = djangoclient.BoardReader


class DisplayingTasksHtmlViewViaSeleniumBusinessLogicOnlyBoard(DisplayingTasks, TestCase):

    urls = True  # TODO: hack - to ensure that root url conf will be stored by the testcase
    builder_cls = businesslogiconly.BoardInitializer
    getter_cls = webdriver.BoardReader


class DisplayingTasksJsonViewViaDjangoClientBusinessLogicOnlyBoard(DisplayingTasks, TestCase):

    urls = True  # TODO: hack - to ensure that root url conf will be stored by the testcase
    builder_cls = businesslogiconly.BoardInitializer
    getter_cls = DjangoClientJsonViewBoardGetter


class MovingTasksBusinessLogicOnlyBoard(MovingSingleTaskOnTwoByTwoBoard, TestCase):
    builder_cls = businesslogiconly.BoardInitializer
    getter_cls = businesslogiconly.BoardReader
    mover_cls = businesslogiconly.TaskMover


class MovingTasksHtmlViaDjangoClientViewBusinessLogicOnlyBoard(MovingSingleTaskOnTwoByTwoBoard, TestCase):

    urls = True  # TODO: hack - to ensure that root url conf will be stored by the testcase
    builder_cls = djangoclient.BoardInitializer
    getter_cls = djangoclient.BoardReader
    mover_cls = djangoclient.TaskMover


class MovingTasksHtmlViaSeleniumViewBusinessLogicOnlyBoard(MovingSingleTaskOnTwoByTwoBoard, TestCase):

    urls = True  # TODO: hack - to ensure that root url conf will be stored by the testcase
    builder_cls = businesslogiconly.BoardInitializer
    getter_cls = webdriver.BoardReader
    mover_cls = webdriver.TaskMover


class AddingTasksBusinessLogicOnlyBoard(AddingTasks, TestCase):
    builder_cls = businesslogiconly.BoardInitializer
    getter_cls = businesslogiconly.BoardReader
    adder_cls = businesslogiconly.TaskAdder


