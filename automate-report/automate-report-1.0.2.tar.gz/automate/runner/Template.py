# coding=utf-8

# 测试报告HTML 模板类,  %{} 表示需要输入的变量

# ------------------------------------------------------------------------
# HTML Template

# <!-- 样式 -->
# <link type="text/css" rel="stylesheet" href="http://192.168.19.97:7777/styles/pyunit.css" />
#
# <script type="text/javascript" src="http://192.168.19.97:7777/scripts/jquery.min.js"></script>
# <script type="text/javascript" src="http://192.168.19.97:7777/scripts/pyunit.js"></script>

HTML_TMPL = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

<head>
    <title>%(title)s</title>
    <meta name="generator" content="%(generator)s"/>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <link type="text/css" rel="stylesheet" href="https://cdn.bootcss.com/jquery/3.4.1/jquery.js" />
    <link type="text/css" rel="stylesheet" href="http://qa-demo.web.sdp.101.com/assets/pyunit.css" />
    <link type="text/css" rel="stylesheet" href="http://qa-demo.beta.web.sdp.101.com/css/bootstrap/v3.3.5/bootstrap.min.css" />

    <script type="text/javascript" src="http://qa-demo.web.sdp.101.com/assets/jquery.min.js"></script>
    <script type="text/javascript" src="http://qa-demo.web.sdp.101.com/assets/pyunit.js"></script>
    <script type="text/javascript" src="http://qa-demo.beta.web.sdp.101.com/assets/report.js"></script>

    %(stylesheet)s
</head>

<body style="text-align:center;" onload="init()">

%(heading)s

%(test_case_dir)s

%(report)s

%(ending)s
<script>
     function init(){
       $(".shrink").each(function (index, element) {
        var len = 10;      //默认显示字数
        var ctn =  (element);  //获取div对象
        var content = element.innerHTML;    //获取div里的内容

        //alert(shrink);
        var span = document.createElement("span");     //创建<span>元素
        var shrink_text = document.createElement("shrink_text");           //创建<shrink_text>元素
        span.innerHTML = content.substring(0,len);     //span里的内容为content的前len个字符

        shrink_text.innerHTML = content.length>len?"... 展开":"";  //判断显示的字数是否大于默认显示的字数    来设置a的显示
        shrink_text.href = "javascript:void(0)";

        shrink_text.onclick = function(){
            if(shrink_text.innerHTML.indexOf("展开")>0){      //如果shrink_text中含有"展开"则显示"收起"
              shrink_text.innerHTML = "<<&nbsp;收起";
              span.innerHTML = content;
            }else{
                shrink_text.innerHTML = "... 展开";
                span.innerHTML = content.substring(0,len);
            }
        }
        // 设置div内容为空，span元素 shrink_text元素加入到div中
        ctn.innerHTML = "";
        ctn.appendChild(span);
        ctn.appendChild(shrink_text);
       });
     }
     function showClassDetail(cid, count) {
        var id_list = Array(count);
        var toHide = 1;
        for (var i = 0; i < count; i++) {
            tid0 = 't' + cid.substr(1) + '.' + (i + 1);
            tid = 'f' + tid0;
            tr = document.getElementById(tid);
            if (!tr) {
                tid = 'p' + tid0;
                tr = document.getElementById(tid);
            }
            id_list[i] = tid;
            if (tr.className != "none" && tr.className != '') {
                toHide = 0;
            }
        }
        for (var i = 0; i < count; i++) {
            tid = id_list[i];
            if (toHide) {
                try {
                    document.getElementById('div_' + tid).style.display = 'hiddenRow'
                } catch (e) {}
                document.getElementById(tid).className = 'hiddenRow';
            } else {
                document.getElementById(tid).className = '';
            }
        }
    }
  </script>
  
    <style>
    shrink_text {
      text-decoration: none;
      color: #3498db;
    }
    .table_text   { line-height: 40px;}
    .table_text2   { line-height: 20px;}
    </style>
</body>
</html>
"""

# variables: (title, generator, stylesheet, heading, report, ending)

# ------------------------------------------------------------------------
# Stylesheet
#
# alternatively use a <link> for external style sheet, e.g.
#   <link rel="stylesheet" href="$url" type="text/css">
# 样式模板
STYLESHEET_TMPL = ""

# ------------------------------------------------------------------------
# Heading
#
# 描述
# ------------------------------------------------------------------------
# variables: (title, parameters, description)
HEADING_TMPL = """
<div class='heading'>

<!-- 测试报告标题 -->
<h3>%(title)s</h3>

<!-- 测试整体信息 -->
%(parameters)s

<div class="contact">
    %(contact)s
</div>

<div class='description'>
    %(description)s
</div>

</div>

"""

# variables: (name, value)
# 属性：运行时间 通过数
HEADING_ATTRIBUTE_TMPL = """
<p class='attribute'>
<strong>%(name)s:</strong>
%(value)s
</p>
"""

# 用例路径
TEST_CASES_DIR = """
<p class='attribute'>
用例路径&emsp; %(dir)s
</p>
"""

# ------------------------------------------------------------------------
# Report
# ------------------------------------------------------------------------
REPORT_TMPL = """
<p id='show_detail_line'>显示：
<a href='javascript:showCase(0)'>概要信息</a>
<a href='javascript:showCase(1)'>失败的测试</a>
<a href='javascript:showCase(2)'>所有测试</a>
</p>

<table id='result_table' class="table" style="margin: 0 auto">
<colgroup>
<col align='left' />
<col align='right' />
<col align='right' />
<col align='right' />
<col align='right' />
<col align='right' />
</colgroup>

<tr id='header_row'>
    <td>测试套件集/测试用例</td>
    <td>统计</td>
    <td>通过</td>
    <td>失败</td>
    <td>错误</td>
    <td>更多</td>
</tr>

%(test_list)s

<!-- 统计信息 -->
<tr id='total_row'>
    <td>Total</td>
    <td>%(count)s</td>
    <td>%(Pass)s</td>
    <td>%(fail)s</td>
    <td>%(error)s</td>
    <td>&nbsp;</td>
</tr>
</table>
"""

# 使用的变量variables: (test_list, count, Pass, fail, error)
# 测试类结果
REPORT_CLASS_TMPL = r"""
<tr class='%(style)s'>
    <td>%(desc)s</td>
    <td>%(count)s</td>
    <td>%(Pass)s</td>
    <td>%(fail)s</td>
    <td>%(error)s</td>
    <td>
        <a href="javascript:showClassDetail('%(cid)s',%(count)s)" class="detail-link">查看详情
        </a>
    </td>
</tr>
"""
# variables: (style, desc, count, Pass, fail, error, cid)

# tid - case 标号
REPORT_TEST_WITH_OUTPUT_TMPL = r"""
<tr id='%(tid)s' class='%(Class)s'>
    <td class='%(style)s'>

    <div class='table_text'>%(desc)s</div>

    </td>

    <td colspan='4' align='center'>
    <!--css div popup start-->

    <a style='line-height: 40px;' class="popup_link" onfocus='this.blur();' href="javascript:showTestDetail('div_%(tid)s')" >
        %(status)s
    </a>

    <div id='div_%(tid)s' class="popup_window" align="center">

        <div style='text-align: right; color:red;cursor:pointer;line-height: 40px;' >

        <!-- 关闭测试用例详情 -->
        <a onfocus='this.blur();' onclick="document.getElementById('div_%(tid)s').style.display = 'none' " >
           [x]
        </a>

        </div>

        <div class="error-info" align="center">
        %(script)s
        </div>

    </div>
    <!--css div popup end-->
    </td>
    
    <td width = 300px>
    <div class="table_text%(spend_time_type)s">%(spend_time)s</div>
    <div class="shrink" style='line-height: %(details_px)s;'>%(details)s</div>
    </td>
</tr>
"""
# variables: (tid, Class, style, desc, status)

# 报告
# variables: (tid, Class, style, desc, status)
REPORT_TEST_NO_OUTPUT_TMPL = r"""
<tr id='%(tid)s' class='%(Class)s'>
    <td class='%(style)s'>
    <!-- -->
    <div class='table_text'>
        %(desc)s
    </div>
    </td>

    <td colspan='4' >
    <div class='table_text'>%(status)s</div>
    </td>
    <td width = 300px>
    <div class="table_text%(spend_time_type)s">%(spend_time)s</div>
    <div class="shrink" style='line-height: %(details_px)s;'>%(details)s</div>
    </td>
</tr>
"""

REPORT_TEST_OUTPUT_TMPL = r"""
%(id)s: %(output)s
"""  # variables: (id, output)

# ------------------------------------------------------------------------
# ENDING
#
# ENDING_TMPL = """<div id='ending'>&nbsp;</div>"""
ENDING_TMPL = ""


# -------------------- The end of the Template class -------------------
# 模板类定义结束

def main():
    fp = open("tpl.html", "w")
    fp.write(HTML_TMPL)
    fp.write(ENDING_TMPL)
    fp.close()

    fp = open("report.html", "w")
    fp.write(HEADING_TMPL)
    fp.write(HEADING_ATTRIBUTE_TMPL)
    fp.write(REPORT_TMPL)
    fp.write(REPORT_TEST_WITH_OUTPUT_TMPL)
    fp.close()
    print(HTML_TMPL)
    print(ENDING_TMPL)


if __name__ == '__main__':
    main()
