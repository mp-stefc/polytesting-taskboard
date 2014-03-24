import sys
import traceback as tb_mod


class enhance_exception(object):
    def __init__(self, extra_msg_fn):
        self.extra_msg_fn = extra_msg_fn

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            return
        orig_format_exc = tb_mod.format_exc()
        try:
            extra_msg = self.extra_msg_fn()
        except:
            extra_msg = 'Error while trying to enahnce exception:\n%s' % tb_mod.format_exc()
        raise exc_type('\n===\n'.join([orig_format_exc, extra_msg]))
