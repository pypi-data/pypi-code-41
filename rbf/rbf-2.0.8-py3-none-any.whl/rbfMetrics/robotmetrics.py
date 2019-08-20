import os
import math
import smtplib
import time
import logging
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timedelta
from robot.api import ExecutionResult
from .test_stats import TestStats
from .keyword_stats import KeywordStats
from .suite_results import SuiteResults
from .test_results import TestResults
from .keyword_results import KeywordResults

try:
    from gevent.pool import Group

    FAILED_IMPORT = False

except ImportError:
    FAILED_IMPORT = True

IGNORE_LIBRARIES = ['BuiltIn', 'SeleniumLibrary', 'String', 'Collections', 'DateTime']
IGNORE_TYPES = ['foritem', 'for']


def generate_report(opts):
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    group = Group() if not FAILED_IMPORT else ''

    # START OF CUSTOMIZE REPORT
    # URL or filepath of your company logo
    logo = opts.logo

    # Ignores following library keywords in metrics report
    ignore_library = IGNORE_LIBRARIES
    if opts.ignore:
        ignore_library.extend(opts.ignore)

    # Ignores following type keywords in metrics report
    ignore_type = IGNORE_TYPES
    if opts.ignoretype:
        ignore_type.extend(opts.ignoretype)

    # END OF CUSTOMIZE REPORT
    # Report to support file location as arguments
    # Source Code Contributed By : Ruud Prijs
    # input directory
    path = os.path.abspath(os.path.expanduser(opts.path))

    # output.xml files
    output_names = []
    for curr_name in opts.output.split(","):
        curr_path = os.path.join(path, curr_name)
        output_names.append(curr_path)
    
    # log.html file
    log_name = opts.log_name

    # copy the list of output_names onto the one of required_files; the latter may (in the future) 
    # contain files that should not be processed as output_names
    required_files = list(output_names) 
    missing_files = [filename for filename in required_files if not os.path.exists(filename)]
    if missing_files:
        # We have files missing.
        exit("output.xml file is missing: {}".format(", ".join(missing_files)))

    mt_time = datetime.now().strftime('%Y%m%d-%H%M%S')

    # Output result file location
    result_file_name = 'metrics-' + mt_time + '.html'
    result_file = os.path.join(path, result_file_name)

    # Read output.xml file
    result = ExecutionResult(*output_names)
    result.configure(stat_config={'suite_stat_level': 2,
                                  'tag_stat_combine': 'tagANDanother'})

    logging.info("Converting .xml to .html file. This may take few minutes...")

    head_content = """
    <!doctype html><html lang="en">
    <head>
        <link rel="shortcut icon" href="https://png.icons8.com/windows/50/000000/bot.png" type="image/x-icon" />
        <title>rbf Metrics</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.datatables.net/1.10.19/css/jquery.dataTables.min.css" rel="stylesheet"/>
        <link href="https://cdn.datatables.net/buttons/1.5.2/css/buttons.dataTables.min.css" rel="stylesheet"/>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.1.3/css/bootstrap.min.css" rel="stylesheet"/>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css" rel="stylesheet">

       <script src="https://code.jquery.com/jquery-3.3.1.js" type="text/javascript"></script>

        <!-- Bootstrap core Googleccharts -->
       <script src="https://www.gstatic.com/charts/loader.js" type="text/javascript"></script>
       <script type="text/javascript">google.charts.load('current', {packages: ['corechart']});</script>

       <!-- Bootstrap core Datatable-->
        <script src="https://cdn.datatables.net/1.10.19/js/jquery.dataTables.min.js" type="text/javascript"></script>
        <script src="https://cdn.datatables.net/buttons/1.5.2/js/dataTables.buttons.min.js" type="text/javascript"></script>
        <script src="https://cdn.datatables.net/buttons/1.5.2/js/buttons.flash.min.js" type="text/javascript"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.1.3/jszip.min.js" type="text/javascript"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.36/pdfmake.min.js" type="text/javascript"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.36/vfs_fonts.js" type="text/javascript"></script>
        <script src="https://cdn.datatables.net/buttons/1.5.2/js/buttons.html5.min.js" type="text/javascript"></script>
        <script src="https://cdn.datatables.net/buttons/1.5.2/js/buttons.print.min.js" type="text/javascript"></script>

        <style>
            body {
                font-family: -apple-system,sans-serif;
            }

            .sidenav {
                height: 100%;
                width: 220px;
                position: fixed;
                z-index: 1;
                top: 0;
                left: 0;
                background-color: white;
                overflow-x: hidden;
                border-style: ridge;
            }

            .sidenav a {
                padding: 12px 10px 8px 12px;
                text-decoration: none;
                font-size: 18px;
                color: Black;
                display: block;
            }

            .main {
                padding-top: 10px;
            }

            @media screen and (max-height: 450px) {
                .sidenav {padding-top: 15px;}
                .sidenav a {font-size: 18px;}
            }

            .tile {
                width: 100%;
                float: left;
                margin: 0px;
                list-style: none;
                font-size: 30px;
                color: #FFF;
                -moz-border-radius: 5px;
                -webkit-border-radius: 5px;
                margin-bottom: 5px;
                position: relative;
                text-align: center;
                color: white!important;
            }

            .tile.tile-fail {
                background: #f44336!important;
            }
            .tile.tile-pass {
                background: #4CAF50!important;
            }
            .tile.tile-info {
                background: #009688!important;
            }
            .tile.tile-head {
                background: #616161!important;
            }
            .dt-buttons {
                margin-left: 5px;
            }
            
            .loader {
                position: fixed;
                left: 0px;
                top: 0px;
                width: 100%;
                height: 100%;
                z-index: 9999;
                background: url('https://www.downgraf.com/wp-content/uploads/2014/09/02-loading-blossom-2x.gif') 
                    50% 50% no-repeat rgb(249,249,249);
            }

        </style>
    </head>
    """

    soup = BeautifulSoup(head_content, "html.parser")
    body = soup.new_tag('body')
    soup.insert(20, body)
    icons_txt = """
    <div class="loader"></div>
    <div class="sidenav">
        <a> <img src="%s" style="max-height:20vh;max-width:98%%;"/> </a>
        <a class="tablink" href="#" id="defaultOpen" onclick="openPage('dashboard', this, 'orange')"><i class="fa fa-dashboard"></i> Dashboard</a>
        <a class="tablink" href="#" onclick="openPage('suiteMetrics', this, 'orange'); executeDataTable('#sm',5)"><i class="fa fa-th-large"></i> Test Suites</a>
        <a class="tablink" href="#" onclick="openPage('testMetrics', this, 'orange'); executeDataTable('#tm',3)"><i class="fa fa-list-alt"></i> Test Cases</a>
        <a class="tablink" href="#" onclick="openPage('keywordMetrics', this, 'orange'); executeDataTable('#km',3)"><i class="fa fa-table"></i> Keywords</a>
        <a class="tablink" href="#" onclick="openPage('log', this, 'orange');"><i class="fa fa-wpforms"></i> Test Logs</a>
    </div>
    """ % logo

    body.append(BeautifulSoup(icons_txt, 'html.parser'))

    page_content_div = soup.new_tag('div')
    page_content_div["class"] = "main col-md-9 ml-sm-auto col-lg-10 px-4"
    body.insert(50, page_content_div)

    logging.info("1 of 4: Capturing dashboard content...")
    test_stats = TestStats()
    result.visit(test_stats)

    total_suite = test_stats.total_suite
    passed_suite = test_stats.passed_suite
    failed_suite = test_stats.failed_suite

    suitepp = math.ceil(passed_suite * 100.0 / total_suite)
    elapsedtime = datetime(1970, 1, 1) + timedelta(milliseconds=result.suite.elapsedtime)
    elapsedtime = elapsedtime.strftime("%X")
    my_results = result.generated_by_robot

    if my_results:
        generator = "Robot"
    else:
        generator = "Rebot"

    stats = result.statistics
    total = stats.total.all.total
    passed = stats.total.all.passed
    failed = stats.total.all.failed

    testpp = round(passed * 100.0 / total, 2)

    kw_stats = KeywordStats(ignore_library, ignore_type)
    result.visit(kw_stats)

    total_keywords = kw_stats.total_keywords
    passed_keywords = kw_stats.passed_keywords
    failed_keywords = kw_stats.failed_keywords

    # Handling ZeroDivisionError exception when no keywords are found
    if total_keywords > 0:
        kwpp = round(passed_keywords * 100.0 / total_keywords, 2)
    else:
        kwpp = 0

    dashboard_content = """
    <div class="tabcontent" id="dashboard">

                    <div class="d-flex flex-column flex-md-row align-items-center p-1 mb-3 bg-light 
                        border-bottom shadow-sm">
                      <h5 class="my-0 mr-md-auto font-weight-normal"><i class="fa fa-dashboard"></i> Dashboard</h5>
                      <nav class="my-2 my-md-0 mr-md-3" style="color:red">
                        <a class="p-2"><b style="color:black;">Execution Time: </b>%s h</a>
                        <a class="p-2"><b style="color:black;cursor: pointer;">Generated By: </b>%s</a>
                      </nav>                  
                    </div>

                    <div class="row">
                        <div class="col-md-3"  onclick="openPage('suiteMetrics', this, '')" data-toggle="tooltip" 
                            title="Click to view Test Suite metrics" style="cursor: pointer;">                        
                            <a class="tile tile-head">
                                Test Suites
                                <p style="font-size:12px">Statistics</p>
                            </a>
                        </div>
                        <div class="col-md-3">                        
                            <a class="tile tile-info">
                                %s
                                <p style="font-size:12px">Total</p>
                            </a>
                        </div>
                        <div class="col-md-3">                        
                            <a class="tile tile-pass">
                                %s
                                <p style="font-size:12px">Pass</p>
                            </a>
                        </div>                        
                        <div class="col-md-3">                        
                            <a class="tile tile-fail">
                                %s
                                <p style="font-size:12px">Fail</p>
                            </a>
                        </div>
                    </div>

                    <div class="row">
                        <div class="col-md-3"  onclick="openPage('testMetrics', this, '')" data-toggle="tooltip" 
                        title="Click to view Test Case metrics" style="cursor: pointer;">                        
                            <a class="tile tile-head">
                                Test Cases
                                <p style="font-size:12px">Statistics</p>
                            </a>
                        </div>
                        <div class="col-md-3">                        
                            <a class="tile tile-info">
                                %s
                                <p style="font-size:12px">Total</p>
                            </a>
                        </div>
                        <div class="col-md-3">                        
                            <a class="tile tile-pass">
                                %s
                                <p style="font-size:12px">Pass</p>
                            </a>
                        </div>                        
                        <div class="col-md-3">                        
                            <a class="tile tile-fail">
                                %s
                                <p style="font-size:12px">Fail</p>
                            </a>
                        </div>
                    </div>

                    <div class="row">
                        <div class="col-md-3"  onclick="openPage('keywordMetrics', this, '')" data-toggle="tooltip" 
                            title="Click to view Keyword metrics" style="cursor: pointer;">                        
                            <a class="tile tile-head">
                                Keywords
                                <p style="font-size:12px">Statistics</p>
                            </a>
                        </div>
                        <div class="col-md-3">                        
                            <a class="tile tile-info">
                                %s
                                <p style="font-size:12px">Total</p>
                            </a>
                        </div>
                        <div class="col-md-3">                        
                            <a class="tile tile-pass">
                                %s
                                <p style="font-size:12px">Pass</p>
                            </a>
                        </div>                        
                        <div class="col-md-3">                        
                            <a class="tile tile-fail">
                                %s
                                <p style="font-size:12px">Fail</p>
                            </a>
                        </div>
                    </div>

                    <hr></hr>
                    <div class="row">
                        <div class="col-md-4" style="background-color:white;height:280px;width:auto;border:groove;">
                            <span style="font-weight:bold">Test Suite Status:</span>
                            <div id="suiteChartID" style="height:250px;width:auto;"></div>
                        </div>
                        <div class="col-md-4" style="background-color:white;height:280px;width:auto;border:groove;">
                            <span style="font-weight:bold">Test Case Status:</span>
                            <div id="testChartID" style="height:250px;width:auto;"></div>
                        </div>
                        <div class="col-md-4" style="background-color:white;height:280px;width:auto;border:groove;">
                            <span style="font-weight:bold">Keyword Status:</span>
                            <div id="keywordChartID" style="height:250px;width:auto;"></div>
                        </div>
                    </div>

                    <hr></hr>
                    <div class="row">
                        <div class="col-md-12" style="background-color:white;height:450px;width:auto;border:groove;">
                            <span style="font-weight:bold">Test Suite Performance Statistics - Top 10 (in sec):</span>
                            <div id="suiteBarID" style="height:400px;width:auto;"></div>
                        </div>
                        <div class="col-md-12" style="background-color:white;height:450px;width:auto;border:groove;">
                            <span style="font-weight:bold">Test Case Performance Statistics - Top 10 (in sec):</span>
                            <div id="testsBarID" style="height:400px;width:auto;"></div>
                        </div>
                        <div class="col-md-12" style="background-color:white;height:450px;width:auto;border:groove;">
                            <span style="font-weight:bold">Keywords Performance Statistics - Top 10 (in sec):</span>
                            <div id="keywordsBarID" style="height:400px;width:auto;"></div>
                        </div>
                    </div>

       <script>
        window.onload = function(){
        executeDataTable('#sm',5);
        executeDataTable('#tm',3);
        executeDataTable('#km',3);
        createPieChart(%s,%s,'suiteChartID','Test Suite Status:');
        createBarGraph('#sm',0,5,10,'suiteBarID','Elapsed Time(s): ','Suite');    
        createPieChart(%s,%s,'testChartID','Test Case Status:');    
        createBarGraph('#tm',1,3,10,'testsBarID','Elapsed Time(s): ','Test'); 
        createPieChart(%s,%s,'keywordChartID','Keyword Status:');
        createBarGraph('#km',1,3,10,'keywordsBarID','Elapsed Time(s): ','Keyword');
        };
       </script>
       <script>
    function openInNewTab(url,element_id) {
      var element_id= element_id;
      var win = window.open(url, '_blank');
      win.focus();
      $('body').scrollTo(element_id); 
    }
    </script>
      </div>
    """ % (elapsedtime, generator, total_suite, passed_suite, failed_suite, total, passed, failed, total_keywords,
           passed_keywords, failed_keywords, passed_suite, failed_suite, passed, failed, passed_keywords,
           failed_keywords)

    page_content_div.append(BeautifulSoup(dashboard_content, 'html.parser'))

    ### ============================ END OF DASHBOARD ============================================ ####
    logging.info("2 of 4: Capturing test suite metrics...")
    ### ============================ START OF SUITE METRICS ======================================= ####

    # Tests div
    suite_div = soup.new_tag('div')
    suite_div["id"] = "suiteMetrics"
    suite_div["class"] = "tabcontent"
    page_content_div.insert(50, suite_div)

    test_icon_txt = """
                    <h4><b><i class="fa fa-table"></i> Test Suites</b></h4>
                    <hr></hr>
                    """
    suite_div.append(BeautifulSoup(test_icon_txt, 'html.parser'))

    # Create table tag
    table = soup.new_tag('table')
    table["id"] = "sm"
    table["class"] = "table table-striped table-bordered"
    suite_div.insert(10, table)

    thead = soup.new_tag('thead')
    table.insert(0, thead)

    tr = soup.new_tag('tr')
    thead.insert(0, tr)

    th = soup.new_tag('th')
    th.string = "Suite Name"
    tr.insert(0, th)

    th = soup.new_tag('th')
    th.string = "Status"
    tr.insert(1, th)

    th = soup.new_tag('th')
    th.string = "Total"
    tr.insert(2, th)

    th = soup.new_tag('th')
    th.string = "Pass"
    tr.insert(3, th)

    th = soup.new_tag('th')
    th.string = "Fail"
    tr.insert(4, th)

    th = soup.new_tag('th')
    th.string = "Time (s)"
    tr.insert(5, th)

    suite_tbody = soup.new_tag('tbody')
    table.insert(11, suite_tbody)

    # GET SUITE METRICS
    if group:
        group.spawn(result.visit, SuiteResults(soup, suite_tbody, log_name))
    else:
        result.visit(SuiteResults(soup, suite_tbody, log_name))

    test_icon_txt = """
    <div class="row">
    <div class="col-md-12" style="height:25px;width:auto;">
    </div>
    </div>
    """
    suite_div.append(BeautifulSoup(test_icon_txt, 'html.parser'))

    ### ============================ END OF SUITE METRICS ============================================ ####
    logging.info("3 of 4: Capturing test case metrics...")
    ### ============================ START OF TEST METRICS ======================================= ####

    # Tests div
    tm_div = soup.new_tag('div')
    tm_div["id"] = "testMetrics"
    tm_div["class"] = "tabcontent"
    page_content_div.insert(100, tm_div)

    test_icon_txt = """
    <h4><b><i class="fa fa-table"></i> Test Cases</b></h4>
    <hr></hr>
    """
    tm_div.append(BeautifulSoup(test_icon_txt, 'html.parser'))

    # Create table tag
    table = soup.new_tag('table')
    table["id"] = "tm"
    table["class"] = "table table-striped table-bordered"
    tm_div.insert(10, table)

    thead = soup.new_tag('thead')
    table.insert(0, thead)

    tr = soup.new_tag('tr')
    thead.insert(0, tr)

    th = soup.new_tag('th')
    th.string = "Suite Name"
    tr.insert(0, th)

    th = soup.new_tag('th')
    th.string = "Test Case"
    tr.insert(1, th)

    th = soup.new_tag('th')
    th.string = "Status"
    tr.insert(2, th)

    th = soup.new_tag('th')
    th.string = "Time (s)"
    tr.insert(3, th)

    th = soup.new_tag('th')
    th.string = "Error Message"
    tr.insert(4, th)

    test_tbody = soup.new_tag('tbody')
    table.insert(11, test_tbody)

    # GET TEST METRICS
    if group:
        group.spawn(result.visit, TestResults(soup, test_tbody, log_name))
    else:
        result.visit(TestResults(soup, test_tbody, log_name))

    test_icon_txt = """
    <div class="row">
    <div class="col-md-12" style="height:25px;width:auto;">
    </div>
    </div>
    """
    tm_div.append(BeautifulSoup(test_icon_txt, 'html.parser'))
    
    ### ============================ END OF TEST METRICS ============================================ ####
    logging.info("4 of 4: Capturing keyword metrics...")
    ### ============================ START OF KEYWORD METRICS ======================================= ####

    # Keywords div
    km_div = soup.new_tag('div')
    km_div["id"] = "keywordMetrics"
    km_div["class"] = "tabcontent"
    page_content_div.insert(150, km_div)

    keyword_icon_txt = """
    <h4><b><i class="fa fa-table"></i> Keywords</b></h4>
      <hr></hr>
    """
    km_div.append(BeautifulSoup(keyword_icon_txt, 'html.parser'))

    # Create table tag
    # <table id="myTable">
    table = soup.new_tag('table')
    table["id"] = "km"
    table["class"] = "table table-striped table-bordered"
    km_div.insert(10, table)

    thead = soup.new_tag('thead')
    table.insert(0, thead)

    tr = soup.new_tag('tr')
    thead.insert(0, tr)

    th = soup.new_tag('th')
    th.string = "Test Case"
    tr.insert(1, th)

    th = soup.new_tag('th')
    th.string = "Keyword"
    tr.insert(1, th)

    th = soup.new_tag('th')
    th.string = "Status"
    tr.insert(2, th)

    th = soup.new_tag('th')
    th.string = "Time (s)"
    tr.insert(3, th)

    kw_tbody = soup.new_tag('tbody')
    table.insert(1, kw_tbody)

    if group:
        group.spawn(result.visit, KeywordResults(soup, kw_tbody, ignore_library, ignore_type))
        group.join()
    else:
        result.visit(KeywordResults(soup, kw_tbody, ignore_library, ignore_type))

    test_icon_txt = """
    <div class="row">
    <div class="col-md-12" style="height:25px;width:auto;">
    </div>
    </div>
    """
    km_div.append(BeautifulSoup(test_icon_txt, 'html.parser'))
    # END OF KEYWORD METRICS

    # START OF LOGS

    # Logs div
    log_div = soup.new_tag('div')
    log_div["id"] = "log"
    log_div["class"] = "tabcontent"
    page_content_div.insert(200, log_div)

    test_icon_txt = """
        <p style="text-align:right">** <b>log.html</b> and <b>report.html</b> need to be in current folder in order to be displayed in the metrics</p>
      <div class="embed-responsive embed-responsive-4by3">
        <iframe class="embed-responsive-item" src=%s></iframe>
      </div>
    """ % log_name
    log_div.append(BeautifulSoup(test_icon_txt, 'html.parser'))

    # END OF LOGS

    # EMAIL STATISTICS
    # Statistics div
    statisitcs_div = soup.new_tag('div')
    statisitcs_div["id"] = "statistics"
    statisitcs_div["class"] = "tabcontent"
    page_content_div.insert(300, statisitcs_div)

    emailStatistics="""
    <h4><b><i class="fa fa-envelope-o"></i> Email Statistics</b></h4>
    <hr></hr>
    <button id="create" class="btn btn-primary active inner" role="button" onclick="updateTextArea();this.style.visibility= 'hidden';"><i class="fa fa-cogs"></i> Generate Statistics Email</button>
    <a download="message.eml" class="btn btn-primary active inner" role="button" id="downloadlink" style="display: none; width: 300px;"><i class="fa fa-download"></i> Click Here To Download Email</a>
    <script>
    function updateTextArea() {
        try{
            var suite = "<b>Top 10 Suite Performance:</b><br><br>" + $("#suiteBarID table")[0].outerHTML;
        } catch(err) {
            var suite = ""
        }
        try{
            var test = "<b>Top 10 Test Performance:</b><br><br>" + $("#testsBarID table")[0].outerHTML;
        } catch(err) {
            var test = ""
        }
        try{
            var keyword ="<b>Top 10 Keyword Performance:</b><br><br>" + $("#keywordsBarID table")[0].outerHTML;
        } catch(err) {
            var keyword = ""
        }
        var saluation="<pre><br>Please refer RF Metrics Report for detailed statistics.<br><br>Regards,<br>QA Team</pre></body></html>";
        document.getElementById("textbox").value += "<br>" + suite + "<br>" + test + "<br>" + keyword + saluation;
        $("#create").click(function(){
        $(this).remove();
        });
    }
    </script>
    
<textarea id="textbox" class="col-md-12" style="height: 400px; padding:1em;">
To: myemail1234@email.com
Subject: Automation Execution Status
X-Unsent: 1
Content-Type: text/html
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>Test Email Sample</title>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta http-equiv="X-UA-Compatible" content="IE=edge" />
<meta name="viewport" content="width=device-width, initial-scale=1.0 " />
        <style>
            body {
                background-color:#F2F2F2; 
            }
            body, html, table,pre,b {
                font-family: Courier New, Arial, sans-serif;
                font-size: 1em; 
            }
            .pastdue { color: crimson; }
            table {
                border: 1px solid silver;
                padding: 6px;
                margin-left: 30px;
                width: 600px;
            }
            thead {
                text-align: center;
                font-size: 1.1em;        
                background-color: #B0C4DE;
                font-weight: bold;
                color: #2D2C2C;
            }
            tbody {
            text-align: center;
            }
            th {
            width: 25%%;
            word-wrap:break-word;
            }
        </style>
    </head>
    <body><pre>Hi Team,
Following are the last build execution statistics.

<b>Metrics:<b>

</pre>
        <table>
            <thead>
            <th style="width: 25%%;">Statistics</th>
            <th style="width: 25%%;">Total</th>
            <th style="width: 25%%;">Pass</th>
            <th style="width: 25%%;">Fail</th>
            </thead>
            <tbody>
            <tr>
                <td style="text-align: left;font-weight: bold;"> SUITE </td>
                <td style="background-color: #F5DEB3;text-align: center;">%s</td>
                <td style="background-color: #90EE90;text-align: center;">%s</td>
                <td style="background-color: #F08080;text-align: center;">%s</td>
            </tr>
            <tr>
                <td style="text-align: left;font-weight: bold;"> TESTS </td>
                <td style="background-color: #F5DEB3;text-align: center;">%s</td>
                <td style="background-color: #90EE90;text-align: center;">%s</td>
                <td style="background-color: #F08080;text-align: center;">%s</td>
            </tr>
            <tr>
                <td style="text-align: left;font-weight: bold;"> KEYWORDS </td>
                <td style="background-color: #F5DEB3;text-align: center;">%s</td>
                <td style="background-color: #90EE90;text-align: center;">%s</td>
                <td style="background-color: #F08080;text-align: center;">%s</td>
            </tr>
            </tbody>
        </table>
</textarea>
    
    """ % (total_suite,passed_suite,failed_suite,total,passed,failed,total_keywords,passed_keywords,failed_keywords)
    statisitcs_div.append(BeautifulSoup(emailStatistics, 'html.parser'))

    # END OF EMAIL STATISTICS
    script_text = """
        <script>
            (function () {
            var textFile = null,
              makeTextFile = function (text) {
                var data = new Blob([text], {type: 'text/plain'});
                if (textFile !== null) {
                  window.URL.revokeObjectURL(textFile);
                }
                textFile = window.URL.createObjectURL(data);
                return textFile;
              };

              var create = document.getElementById('create'),
                textbox = document.getElementById('textbox');
              create.addEventListener('click', function () {
                var link = document.getElementById('downloadlink');
                link.href = makeTextFile(textbox.value);
                link.style.display = 'block';
              }, false);
            })();
        </script>
        <script>
            function createPieChart(passed_count,failed_count,ChartID,ChartName){
            var status = [];
            status.push(['Status', 'Percentage']);
            status.push(['PASS',parseInt(passed_count)],['FAIL',parseInt(failed_count)]);
            var data = google.visualization.arrayToDataTable(status);

            var options = {
            pieHole: 0.6,
            legend: 'none',
            chartArea: {width: "95%",height: "90%"},
            colors: ['green', 'red'],
            };

            var chart = new google.visualization.PieChart(document.getElementById(ChartID));
            chart.draw(data, options);
        }
        </script>
        <script>
           function createBarGraph(tableID,keyword_column,time_column,limit,ChartID,Label,type){
            var status = [];
            css_selector_locator = tableID + ' tbody >tr'
            var rows = $(css_selector_locator);
            var columns;
            var myColors = [
                '#4F81BC',
                '#C0504E',
                '#9BBB58',
                '#24BEAA',
                '#8064A1',
                '#4AACC5',
                '#F79647',
                '#815E86',
                '#76A032',
                '#34558B'
            ];
            status.push([type, Label,{ role: 'annotation'}, {role: 'style'}]);
            for (var i = 0; i < rows.length; i++) {
                if (i == Number(limit)){
                    break;
                }
                //status = [];
                name_value = $(rows[i]).find('td'); 

                time=($(name_value[Number(time_column)]).html()).trim();
                keyword=($(name_value[Number(keyword_column)]).html()).trim();
                status.push([keyword,parseFloat(time),parseFloat(time),myColors[i]]);
              }
              var data = google.visualization.arrayToDataTable(status);

              var options = {
                legend: 'none',
                chartArea: {width: "92%",height: "75%"},
                bar: {
                    groupWidth: '90%'
                },
                annotations: {
                    alwaysOutside: true,
                    textStyle: {
                    fontName: 'Comic Sans MS',
                    fontSize: 13,
                    bold: true,
                    italic: true,
                    color: "black",     // The color of the text.
                    },
                },
                hAxis: {
                    textStyle: {
                        fontName: 'Arial',
                        fontSize: 10,
                    }
                },
                vAxis: {
                    gridlines: { count: 10 },
                    textStyle: {                    
                        fontName: 'Comic Sans MS',
                        fontSize: 10,
                    }
                },
              };  

                // Instantiate and draw the chart.
                var chart = new google.visualization.ColumnChart(document.getElementById(ChartID));
                chart.draw(data, options);
             }

        </script>

     <script>
      function executeDataTable(tabname,sortCol) {
        var fileTitle;
        switch(tabname) {
            case "#sm":
                fileTitle = "SuiteMetrics";
                break;
            case "#tm":
                fileTitle =  "TestMetrics";
                break;
            case "#km":
                fileTitle =  "KeywordMetrics";
                break;
            default:
                fileTitle =  "metrics";
        }

        $(tabname).DataTable(
            {
                retrieve: true,
                "order": [[ Number(sortCol), "desc" ]],
                dom: 'l<".margin" B>frtip',
                buttons: [
                    'copy',
                    {
                        extend: 'csv',
                        filename: function() {
                            return fileTitle + '-' + new Date().toLocaleString();
                        },
                        title : '',
                    },
                    {
                        extend: 'excel',
                        filename: function() {
                            return fileTitle + '-' + new Date().toLocaleString();
                        },
                        title : '',
                    },
                    {
                        extend: 'pdf',
                        filename: function() {
                            return fileTitle + '-' + new Date().toLocaleString();
                        },
                        title : '',
                    },
                    {
                        extend: 'print',
                        title : '',
                    },
                ],
            } 
        );
    }
     </script>
     <script>
      function openPage(pageName,elmnt,color) {
        var i, tabcontent, tablinks;
        tabcontent = document.getElementsByClassName("tabcontent");
        for (i = 0; i < tabcontent.length; i++) {
            tabcontent[i].style.display = "none";
        }
        tablinks = document.getElementsByClassName("tablink");
        for (i = 0; i < tablinks.length; i++) {
            tablinks[i].style.backgroundColor = "";
        }
        document.getElementById(pageName).style.display = "block";
        elmnt.style.backgroundColor = color;

    }
    // Get the element with id="defaultOpen" and click on it
    document.getElementById("defaultOpen").click();
     </script>
     <script>
     // Get the element with id="defaultOpen" and click on it
    document.getElementById("defaultOpen").click();
     </script>
     <script>
    $(window).on('load',function(){$('.loader').fadeOut();});
    </script>
    """

    body.append(BeautifulSoup(script_text, 'html.parser'))

    # WRITE TO RF_METRICS_REPORT.HTML

    # Write output as html file
    with open(result_file, 'w') as outfile:
        outfile.write(soup.prettify())

    logging.info("rbf metrics created successfully and can be found at {}".format(result_file))
    # ==== END OF EMAIL CONTENT ====== #