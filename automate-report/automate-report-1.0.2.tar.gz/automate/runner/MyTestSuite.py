# coding=utf-8
import unittest
from unittest.suite import _isnotsuite


# 该类实现跳过不用看,仅仅覆盖系统api回调方法而已,实现自定义的测试用例集
class MyTestSuite(unittest.TestSuite):

    def run(self, result, debug=False):
        topLevel = False

        if getattr(result, '_testRunEntered', False) is False:
            result._testRunEntered = topLevel = True

        for test in self:
            test_cls = test.__class__
            dir_detail = dir(test)
            test_cases = test._tests

            if result.shouldStop:
                break

            if _isnotsuite(test):
                self._tearDownPreviousClass(test, result)
                self._handleModuleFixture(test, result)
                self._handleClassSetUp(test, result)
                result._previousTestClass = test.__class__

                if (getattr(test.__class__, '_classSetupFailed', False) or
                        getattr(result, '_moduleSetUpFailed', False)):
                    continue

            if not debug:
                test(result)
            else:
                test.debug()

        if topLevel:
            self._tearDownPreviousClass(None, result)
            self._handleModuleTearDown(result)
            result._testRunEntered = False
        return result

    def addTest(self, test):
        super(MyTestSuite, self).addTest(test)
