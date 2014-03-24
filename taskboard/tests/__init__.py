from django.test import TestCase
from taskboard.test_helpers import (
    PurePythonBoardBuilder, PurePythonBoardGetter,
    TemplateRenderingBoardGetter, DjangoClientHtmlViewBoardGetter,
    DjangoClientJsonViewBoardGetter, PurePythonTaskMover, HttpTaskMover,
)
from taskboard.tests.displaying_tasks import DisplayingTasks
from taskboard.tests.moving_tasks import MovingSingleTaskOnTwoByTwoBoard
from taskboard.tests.enhancing_exceptions import EnhancingExceptionsTests


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
    getter_cls = PurePythonBoardGetter  # DjangoClientHtmlViewBoardGetter
    mover_cls = HttpTaskMover
