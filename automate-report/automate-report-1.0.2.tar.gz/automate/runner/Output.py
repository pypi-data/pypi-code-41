# coding=utf-8

# ------------------------------------------------------------------------
# The redirectors below are used to capture output during testing.
#
# Output
# sent to sys.stdout and sys.stderr are automatically captured.
#
# However
# in some cases sys.stdout is already cached before HTMLTestRunner is
# invoked (e.g. calling logging.basicConfig).
#
# In order to capture those
# output, use the redirectors for the cached stream.
#
# e.g.
# 使得日志输出
#
#   >>> logging.basicConfig(stream=HTMLTestRunner.stdout_redirector)
#   >>>
#
# 下面的redirectors用于在测试期间捕获输出。输出发送到系统。
# stdout和系统。stderr自动捕获。
# 然而在某些情况下，sys。在HTMLTestRunner被调用之前，stdout已经被缓存了(例如，调用logger . basicconfig)。
# 为了捕获这些输出，请使用缓存流的redirector。


import sys

# 该类实现跳过不用看,重定向输出流和错误流
class OutputRedirector(object):
    """
    Wrapper to redirect stdout or stderr

    重定向输出，用于捕获unittest的输出，方便重定向到不同的介质
    """
    def __init__(self, fp):
        self.fp = fp

    def write(self, s):
        self.fp.write(s)

    def writelines(self, lines):
        self.fp.writelines(lines)

    def flush(self):
        self.fp.flush()

stdout_redirector = OutputRedirector(sys.stdout)  #重定向标准输出
stderr_redirector = OutputRedirector(sys.stderr) #重定向自动捕获标准的错误
