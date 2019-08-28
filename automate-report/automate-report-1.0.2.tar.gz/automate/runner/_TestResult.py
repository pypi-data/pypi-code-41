# coding=utf-8
import time
from unittest import TestResult
import io  # 用来作字符串的缓
import sys

from .Output import stderr_redirector, stdout_redirector


# 该类实现跳过不用看,仅仅覆盖系统api回调方法而已,实现自定义的测试用例结果统计
class _TestResult(TestResult):
    # note: _TestResult is a pure representation of results.
    # It lacks the output and reporting ability compares to unittest._TextTestResult.
    # 注:_TestResult是结果的纯表示。它缺少与unittest._TextTestResult相比的输出和报告能力。

    def __init__(self, verbosity=1):  # 类实例初始化函数
        TestResult.__init__(self)

        self.stdout0 = None
        self.stderr0 = None
        self.success_count = 0
        self.failure_count = 0
        self.error_count = 0
        self.verbosity = verbosity

        # result is a list of result in 4 tuple
        # (
        #   result code (0: success; 1: fail; 2: error),
        #    TestCase object,
        #   Test output (byte string),
        #   stack trace,
        # )
        self.result = []

    def startTest(self, test):
        TestResult.startTest(self, test)
        # just one buffer for both stdout and stderr
        self.outputBuffer = io.StringIO()
        stdout_redirector.fp = self.outputBuffer
        stderr_redirector.fp = self.outputBuffer
        self.stdout0 = sys.stdout
        self.stderr0 = sys.stderr
        sys.stdout = stdout_redirector
        sys.stderr = stderr_redirector
        test.spend_time = time.time()  # 运行时间
        test.complete = 0  # 完成执行几次，避免重复调用 # by yanxuwen

    def complete_output(self, test):
        """
        Disconnect output redirection and return buffer.
        Safe to call multiple times.
        # 断开输出重定向和返回缓冲区。安全呼叫多次。
        """
        test.complete = test.complete + 1
        if test.complete > 1:
            return
        test.spend_time = time.time() - test.spend_time  # 运行时间
        if self.stdout0:
            sys.stdout = self.stdout0
            sys.stderr = self.stderr0
            self.stdout0 = None
            self.stderr0 = None
        return self.outputBuffer.getvalue()

    def stopTest(self, test):
        # Usually one of addSuccess, addError or addFailure would have been called.
        # But there are some path in unittest that would bypass this.
        # We must disconnect stdout in stopTest(), which is guaranteed to be called.
        # 通常会调用一个addSuccess、addError或addFailure。但是在unittest中有一些路径可以绕过这个。我们必须在stopTest()
        # 中断开stdout，这是保证被调用的。
        self.complete_output(test)

    def addSuccess(self, test):  # 计算成功数总和
        self.success_count += 1
        TestResult.addSuccess(self, test)
        output = self.complete_output(test)
        self.result.append((0, test, output, ''))
        if self.verbosity > 1:
            sys.stderr.write('ok ')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('.')

    def addError(self, test, err):
        self.error_count += 1
        TestResult.addError(self, test, err)
        _, _exc_str = self.errors[-1]
        output = self.complete_output(test)
        self.result.append((2, test, output, _exc_str))
        if self.verbosity > 1:
            sys.stderr.write('E  ')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('E')

    def addFailure(self, test, err):
        # 错误数+1
        self.failure_count += 1

        # 测试结果
        TestResult.addFailure(self, test, err)

        _, _exc_str = self.failures[-1]

        output = self.complete_output(test)

        self.result.append((1, test, output, _exc_str))

        if self.verbosity > 1:
            sys.stderr.write('失败\n  ')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('失败\n')
