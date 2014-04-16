from django.test import TestCase
from taskboard.test_helpers import (
    PurePythonBoardBuilder, PurePythonBoardGetter,
    TemplateRenderingBoardGetter, DjangoClientHtmlViewBoardGetter,
    SeleniumHtmlViewBoardGetter,
    DjangoClientJsonViewBoardGetter, PurePythonTaskMover, HttpTaskMover,
    SeleniumTaskMover,
)
from taskboard.tests.displaying_tasks import DisplayingTasks
from taskboard.tests.moving_tasks import MovingSingleTaskOnTwoByTwoBoard


class DisplayingTasksPurePythonBoard(DisplayingTasks, TestCase):
    builder_cls = PurePythonBoardBuilder
    getter_cls = PurePythonBoardGetter


class DisplayingTasksHtmlTemplateRenderingPurePythonBoard(DisplayingTasks, TestCase):
    builder_cls = PurePythonBoardBuilder
    getter_cls = TemplateRenderingBoardGetter


class DisplayingTasksHtmlViewViaDjangoClientPurePythonBoard(DisplayingTasks, TestCase):

    urls = True  # TODO: hack - to ensure that root url conf will be stored by the testcase
    builder_cls = PurePythonBoardBuilder
    getter_cls = DjangoClientHtmlViewBoardGetter


class DisplayingTasksHtmlViewViaSeleniumPurePythonBoard(DisplayingTasks, TestCase):

    urls = True  # TODO: hack - to ensure that root url conf will be stored by the testcase
    builder_cls = PurePythonBoardBuilder
    getter_cls = SeleniumHtmlViewBoardGetter


class DisplayingTasksJsonViewViaDjangoClientPurePythonBoard(DisplayingTasks, TestCase):

    urls = True  # TODO: hack - to ensure that root url conf will be stored by the testcase
    builder_cls = PurePythonBoardBuilder
    getter_cls = DjangoClientJsonViewBoardGetter


class MovingTasksPurePythonBoard(MovingSingleTaskOnTwoByTwoBoard, TestCase):
    builder_cls = PurePythonBoardBuilder
    getter_cls = PurePythonBoardGetter
    mover_cls = PurePythonTaskMover


class MovingTasksHtmlViaDjangoClientViewPurePythonBoard(MovingSingleTaskOnTwoByTwoBoard, TestCase):

    urls = True  # TODO: hack - to ensure that root url conf will be stored by the testcase
    builder_cls = PurePythonBoardBuilder
    getter_cls = DjangoClientHtmlViewBoardGetter
    mover_cls = HttpTaskMover


class MovingTasksHtmlViaSeleniumViewPurePythonBoard(MovingSingleTaskOnTwoByTwoBoard, TestCase):

    urls = True  # TODO: hack - to ensure that root url conf will be stored by the testcase
    builder_cls = PurePythonBoardBuilder
    getter_cls = SeleniumHtmlViewBoardGetter
    mover_cls = SeleniumTaskMover
