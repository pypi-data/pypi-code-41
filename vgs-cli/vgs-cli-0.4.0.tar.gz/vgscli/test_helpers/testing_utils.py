import sys
from io import StringIO


def assert_output(run, assertion, ignore_exit=False):
    saved_stdout = sys.stdout
    try:
        out = StringIO()
        sys.stdout = out

        if ignore_exit:
            try:
                run()
            except SystemExit:
                pass
        else:
            run()

        assert assertion(out.getvalue().strip())
    finally:
        sys.stdout = saved_stdout
