# coding=utf-8
# 测试报告HTML 模板类, 跳过不用看, 就是HTML标签和内容的字符串拼接


# from common.http import Http
# 先进行导入包调用报告的模板来定义报告的内容描述和连接的信息为空值
import os
import re  # 正则表达式操作   指定一组匹配字符串
from xml.sax import saxutils  # 解析xml 利用SAX解析XML牵涉到两个部分：解析器和事件处理器

import types  # by   中定义了Python中所有的类型 比如整型、浮点型、类等等

# from . import __version__

from automate.runner import __version__, Template
# 避免使用__name__这么明确的名称来代表一个模块的名称。一个模块的名称是由__package__+'.'+__name__来确定的，如果__packege__是None的话，那么这个名称就是__name__了。
# 相对导入使用模块的名称属性来决定模块在包层次结构中的位置，如果模块的名称不包含任何包信息（例如：被设置成‘main’），那么相对导入则被解析为最顶层的位置，不管这个时候这个模块实际上位于文件系统中的什么位置
# 当一个文件被加载进来，它就有一个名称（这个名称存储在__name__属性当中）。
# 如果这个文件被当做一个顶层脚本来进行加载，那么它的名字就是__main__【这就是为什么我们经常会发现这样的语句：if __name__ == "__main__"】
# 当一个模块被当做一个顶层脚本来执行的时候，它原来的名称则会被__main__取代。


# 基础模板

import logging
import importlib

from automate.runner.Base_tpl import Base_tpl

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# 变量 name 的名称就是当前模块的名称。比如，在模块 “foo.bar.my_module” 中调用 logger.getLogger(name) 等价于调用logger.getLogger(“foo.bar.my_module”)
# 如果你的模块的名称是__main__，那么它就不被认为是在一个包当中，因为它的名称当中不含有点，
# 所以你不能在它的里面使用from .. import。如果你使用了这个语句，那么程序就会报“relative-import in non-package"错误
logger.info(__name__)

import sys

importlib.reload(sys)


# sys.setdefaultencoding('utf8')

class Report(Base_tpl):  # 按照定义的基础模板生成报告
    """
    报告生成

    """

    # __init__:类实例初始化函数
    # __str__:类实例字符串化函数
    #  __init__返回结果是存储地址  Friend:0x1d92a70， 想要直接打印出内容可以通过__str__函数  Friend: Liang
    def __init__(self, stream, title, startTime, stopTime):  # 类实例初始化函数
        self.description = ""
        self.contact_info = ""  # 连接的信息
        self.title = title
        self.stopTime = stopTime
        self.startTime = startTime
        self.stream = stream

    def sortResult(self, result_list):
        # unittest does not seems to run in any particular order.unittest  单元测试unittest似乎没有按照任何特定的顺序运行。
        # Here at least we want to group them together by class.  这里至少我们想把它们按类分组。
        # 排序
        rmap = {}
        classes = []
        for n, t, o, e in result_list:  # 测试报告模板由样式表、头部、生成的报告、结束标志4部分组成
            # cls = t.__class__
            cls = t.__class__  # 可以用来传递数据，一个Context是一系列变量和值的集合，它和Python的字典有点相似。
            # context在Django里表现为Context类，在django.template模块里。她的构造函数带有一个可选的参数：一个字典映射变量和它们的值。调用Template对象的render()方法并传递context来填充模板。
            if cls not in rmap:
                rmap[cls] = []
                classes.append(cls)
            rmap[cls].append((n, t, o, e))
        r = [(cls, rmap[cls]) for cls in classes]
        print(r)
        return r

    def getReportAttributes(self, result):  # 获取报告属性
        """
        Return report attributes as a list of (name, value).   返回报告属性作为(名称、值)的列表。
        Override this to add custom attributes.  重写此以添加自定义属性。

        执行时间点
        运行时长
        通过数
        """

        # logger.info("获取报告属性")

        startTime = str(self.startTime)[:19]

        duration = str(self.stopTime - self.startTime)  # 持续时间

        status = []

        if result.success_count:
            status.append('通过 %s' % result.success_count)
        if result.failure_count:
            status.append('失败 %s' % result.failure_count)
        if result.error_count:
            status.append('错误 %s' % result.error_count)

        if status:
            status = ' '.join(status)
        else:
            status = 'none'

        return [
            ('该次测试执行于', startTime),
            ('该次测试总耗时', duration),
            ('状态', status),
        ]

    def generateReport(self, test, result, test_cases_dri, contact=None):  # self  相当于this ，对类实例的引用
        """
        生成报告

        :param test: 用例列表

        :param result: 测试结果

        :param contact: 联系方式

        """
        print("测试生成器", test)

        report_attrs = self.getReportAttributes(result)  # 获得报告的属性

        # logger.info("报告属性-generateReport")
        # logger.info(test)
        # logger.info(report_attrs)

        generator = 'HTMLTestRunner %s' % __version__  # 生产者/版本信息

        # logger.info(generator)

        stylesheet = self._generate_stylesheet()

        heading = self._generate_heading(report_attrs, contact)

        test_case_dir = self._generate_test_cases_dir(test_cases_dri, contact)

        report = self._generate_report(result)

        ending = self._generate_ending()

        # 填充变量
        output = Template.HTML_TMPL % dict(
            title=saxutils.escape(self.title),
            generator=generator,
            stylesheet=stylesheet,
            heading=heading,
            test_case_dir=test_case_dir,
            report=report,
            ending=ending,
        )

        self.stream.write(output.encode('utf8'))

    def _generate_stylesheet(self):
        """
        样式
        """
        return Template.STYLESHEET_TMPL

    def _generate_heading(self, report_attrs, contact=None):
        """
        #. 生成标题
        #.

        """
        a_lines = []

        for name, value in report_attrs:  # 将获得的报告属性按照key : value  的样式以每行展示
            line = Template.HEADING_ATTRIBUTE_TMPL % dict(
                name=saxutils.escape(name),
                value=saxutils.escape(value),
            )

            a_lines.append(line)

        # logger.info("generate heading")
        # logger.info(contact)
        if contact:
            self.contact_info += "<h5>紧急联系人</h5>"
            for k in contact:
                self.contact_info += '<p>'
                self.contact_info += k + '(' + contact[k] + ')'
                self.contact_info += '</p>'

        heading = Template.HEADING_TMPL % dict(
            title=saxutils.escape(self.title),
            parameters=''.join(a_lines),  # 获得的报告属性
            contact=self.contact_info,
            description=saxutils.escape(self.description),
        )

        # logger.info("报告头")
        # logger.info(self.description)

        return heading

    def _generate_test_cases_dir(self, test_cases_dri, contact=None):
        dir = Template.TEST_CASES_DIR % dict(
            dir=saxutils.escape(test_cases_dri),
        )
        return dir

    def _generate_report(self, result):
        """
        生成测试报告

        结果
        """
        # 测试类
        rows = []

        # 对测试结果进行排序
        sortedResult = self.sortResult(result.result)
        # logger.info(sortedResult)

        for cid, (cls, cls_results) in enumerate(sortedResult):

            # subtotal for a class
            np = nf = ne = 0  # 定义成功、失败、错误的用例数

            # format class description  # by yanxuwen
            desc = ""

            for n, t, o, e in cls_results:
                if n == 0:
                    np += 1
                elif n == 1:
                    nf += 1
                else:
                    ne += 1

            # print "type:", str(type(cls))

            if (type(cls) is type):
                desc = cls.__module__
            elif (type(cls) is types.ModuleType):
                desc = cls.__name__
            elif (type(cls) is type):
                if cls.__module__ == "__main__":
                    name = cls.__name__
                else:
                    name = "%s.%s" % (cls.__module__, cls.__name__)
                    doc = cls.__doc__ and cls.__doc__.split("\n")[0] or ""
                    desc = doc and '%s: %s' % (name, doc) or name
            else:
                print("error type")
            # print "dec:", desc
            # 打印出的测试报告表格的对应的key：value说明
            row = Template.REPORT_CLASS_TMPL % dict(
                style=ne > 0 and 'errorClass' or nf > 0 and 'failClass' or 'passClass',  # 显示内容说明
                desc=desc,  # 测试用例/套件集
                count=np + nf + ne,  # 总用例数即统计
                Pass=np,  # 通过数
                fail=nf,  # 失败数
                error=ne,  # 错误数
                cid='c%s' % (cid + 1),  # 更多详情内容展开、
            )

            rows.append(row)

            for tid, (n, t, o, e) in enumerate(cls_results):
                self._generate_report_test(rows, cid, tid, n, t, o, e)

        report = Template.REPORT_TMPL % dict(
            test_list=''.join(rows),
            count=str(result.success_count + result.failure_count + result.error_count),
            Pass=str(result.success_count),
            fail=str(result.failure_count),
            error=str(result.error_count),
        )
        return report

    def _generate_report_test(self, rows, cid, tid, n, t, o, e):
        """
        生成测试报告

        :param rows: 用例表格行

        """
        # e.g. 'pt1.1', 'ft1.1', etc
        # logger.info("generate report test - 生成测试报告")
        # logger.info(n)
        # test cases
        # logger.info(t)

        # logger.info("test cases")
        # logger.info(o)
        # logger.info(e)

        has_output = bool(o or e)

        tid = (n == 0 and 'p' or 'f') + 't%s.%s' % (cid + 1, tid + 1)

        name = t.id().split('.')[-1]

        doc = t.shortDescription() or ""

        """
        desc = doc and ('%s: %s' % (name, doc)) or name
        desc_str = str(t._testMethodDoc)
        desc_str_arr = desc_str.split('\n')
        if len(desc_str_arr) > 1:
           desc += "(" + desc_str_arr[1].strip() + ")"
        else:
           desc += "()"
        """

        desc = name + "(" + doc + ")"  # by yanxuwen

        if hasattr(t, "spend_time"):
            spend_time = t.spend_time  # add by yanxuwen
        else:
            spend_time = 0

        # logger.debug("运行时间: " + str(spend_time))

        tmpl = has_output and Template.REPORT_TEST_WITH_OUTPUT_TMPL or Template.REPORT_TEST_NO_OUTPUT_TMPL

        # output
        # o and e should be byte string because they are collected from stdout and stderr?
        if isinstance(o, str):
            # TODO: some problem with 'string_escape': it escape \n and mess up formating
            # uo = unicode(o.encode('string_escape'))
            # uo = o.decode('latin-1')
            uo = o
        else:
            uo = o

        # error
        if isinstance(e, str):
            # TODO: some problem with 'string_escape': it escape \n and mess up formating
            # ue = unicode(e.encode('string_escape'))
            # ue = e.decode('latin-1')
            ue = e
        else:
            ue = e

        script = Template.REPORT_TEST_OUTPUT_TMPL % dict(
            id=tid,
            output=saxutils.escape(uo + ue),
        )

        script = str(script)

        # 替换为<br>
        script = re.sub('\n', '&lt;br&gt;', script)

        # 描述文案
        doc = t._testMethodDoc
        if doc is None:
            doc = ''
            spend_time_type = '' # 耗时类型，，如果没有描述的话 ，耗时文案 要居中，则设置类型为table_text ，则line-height: 40px; add by yanxuwen
            details_px = '0px' #描述文案的line-height add by yanxuwen
        else:
            doc = "描述：" + doc.strip()
            spend_time_type = '2' # 耗时类型，，如果有描述的话，则设置类型为table_text2 ，则line-height: 20px; add by yanxuwen
            details_px = '20px'

        row = tmpl % dict(
            tid=tid,
            Class=(n == 0 and 'hiddenRow' or 'none'),
            style=n == 2 and 'errorCase' or (n == 1 and 'failCase' or 'none'),
            desc=desc,
            script=script,
            status=self.STATUS[n],
            spend_time="耗时: " + str(round(spend_time, 2)) + " s",  # 单个用例所花费的时间,保留小数点后面2位  add by yanxuwen
            spend_time_type=spend_time_type, # 耗时类型 add by yanxuwen
            details_px=details_px,  # 描述文案line-height的高度  add by yanxuwen
            details=doc  # 描述  add by yanxuwen
        )

        rows.append(row)

        if not has_output:
            return

    def _generate_ending(self):
        return Template.ENDING_TMPL


'''
def get_cs_url(dentry_id):
    """

    :param dentry_id:
    :return:
    """

    host = "plot.qa.sdp.nd"

    http_o = Http(host)

    res = http_o.get("/v1.0/report?dentry_id" + dentry_id)

    logger.info(res)
'''
