from unittest import TestCase
from enhance_exception import enhance_exception
import traceback
import sys


class TestException(Exception):
    pass


class EnhancingExceptionsTests(TestCase):

    def test_if_there_is_no_error_nothing_is_raised(self):
        x = False
        with enhance_exception(lambda: 'extra info'):
            x = True
        self.assertTrue(x)

    def test_message_is_appended_after_original_stacktrace(self):
        def try_block():
            raise TestException('some exception')

        orig_format_exc, final_format_exc = self.run_with_enhanced_exception(
            extra_msg_fn=lambda: 'some more information',
            try_block_fn=try_block,
            expected_exc_type=TestException)

        self.assert_contains(needle=orig_format_exc, haystack=final_format_exc)
        self.assert_contains(needle='some exception', haystack=final_format_exc)
        self.assert_contains(needle='some more information', haystack=final_format_exc)

    def test_if_the_extra_msg_fn_raises_an_exception_of_orig_type_both_stacktraces_contained(self):
        def try_block():
            raise TestException('some exception')

        def extra_msg_fn():
            raise ValueError('something went wrong')

        orig_format_exc, final_format_exc = self.run_with_enhanced_exception(
            extra_msg_fn=extra_msg_fn,
            try_block_fn=try_block,
            expected_exc_type=TestException)

        self.assert_contains(needle='some exception', haystack=final_format_exc)
        self.assert_contains(needle='TestException', haystack=final_format_exc)
        self.assert_contains(needle='something went wrong', haystack=final_format_exc)
        self.assert_contains(needle='ValueError', haystack=final_format_exc)

    def test_if_extra_msg_fn_returns_non_str_it_is_handled_gracefully(self):
        def try_block():
            raise TestException('some exception')

        orig_format_exc, final_format_exc = self.run_with_enhanced_exception(
            extra_msg_fn=lambda: {'foo': 'bar'},
            try_block_fn=try_block,
            expected_exc_type=TestException)

        self.assert_contains(needle='some exception', haystack=final_format_exc)
        self.assert_contains(needle=repr({'foo': 'bar'}), haystack=final_format_exc)

    def run_with_enhanced_exception(self, extra_msg_fn, try_block_fn, expected_exc_type=None):
        expected_exc_type = expected_exc_type or TestException
        orig_format_exc = None
        with self.assertRaises(expected_exc_type) as ex:
            with enhance_exception(extra_msg_fn):
                try:
                    try_block_fn()
                except:
                    orig_format_exc = traceback.format_exc()
                    raise
        final_format_exc = traceback.format_exc()
        self.assertNotEqual(None, orig_format_exc, 'did not run')
        self.assert_contains(needle=orig_format_exc, haystack=final_format_exc, msg='orig format is always contained')
        return orig_format_exc, final_format_exc

    def assert_contains(self, haystack, needle, msg=None):
        failure_msg ="needle (%s) wasn't found in haystack (%s)" % (needle, haystack) 
        if msg is not None:
            failure_msg += ' %s' % msg
        self.assertTrue(needle in haystack, failure_msg)
