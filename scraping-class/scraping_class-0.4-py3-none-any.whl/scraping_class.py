import datetime
import requests
import os
import pandas as pd
import re
import time
import urllib
from functools import wraps


class BaseMetaClass(type):
    def __new__(cls, name, bases, body):
        # def url_wrapper(method):
        #     @wraps(method)
        #     def wrapped(*args, **kwargs):
        #         res = method(*args, **kwargs)
        #         if not re.match(regex, res):
        #             raise ValueError("Not a valid url")
        #         return res
        #     return wrapped

        def get_wrapper(method):
            @wraps(method)
            def wrapped(*args, **kwargs):
                self = args[0]
                time_began = time.time()
                time_ = []
                n_attempts = 0
                err = None
                for _ in range(self.n_tries):
                    with Timer() as t:
                        ratelimit(self.call_rate)
                        try:
                            res = method(*args, **kwargs)
                        except Exception as e:
                            err = str(e)
                            res = None
                    time_.append(round(t.interval, 3))
                    n_attempts += 1
                    if res:
                        break
                        
                d = {
                    "content_size": len(res.text) if hasattr(res, "text") else None,
                    "error": err,
                    "status_code": res.status_code
                    if hasattr(res, "status_code")
                    else None,
                    "success": res.status_code == 200
                    if hasattr(res, "status_code")
                    else False,
                    "time": time_began,
                    "time_avg": round(sum(time_) / len(time_), 3),
                    "n_attempts": n_attempts,
                    "url": res.url if hasattr(res, "url") else None,
                }
                print(d)
                return res

            return wrapped

        overwrite_methods = {"get": get_wrapper}
        body = {
            k: v if k not in overwrite_methods.keys() else overwrite_methods[k](v)
            for k, v in body.items()
        }
        return super().__new__(cls, name, bases, body)


class Base(metaclass=BaseMetaClass):
    def __init__(
        self,
        logfile=None,
        datafile=None,
        overwrite_log=False,
        overwrite_data=False,
        session=None,
        n_tries=5,
        timeout=30,
        call_rate=0.5,
    ):
        file_validator("logfile", logfile)
        file_validator("datafile", datafile)
        self.logfile = logfile
        self.datafile = datafile
        self.overwrite_log = overwrite_log
        self.overwrite_data = overwrite_data
        self.session = session or requests.session()
        self.n_tries = n_tries
        self.timeout = timeout
        self.call_rate = call_rate

    def construct_url(self, url):
        """
        INPUT: DOESNT MATTER
        OUTPUT: URL (STRING)
        """
        return url

    def get(self, url, params=None):
        """
        INPUT: URL, PARAMS
        OUTPUT: REQUESTS RESPONSE
        """
        url = self.construct_url(url)
        response = self.session.get(url, params=params, timeout=self.timeout)
        return response

    def parser(self, response):
        """
        INPUT: REQUESTS RESPONSE
        OUTPUT: DATAFRAME
        """
        pass


class CSV:
    def data_reader(self):
        """
        INPUT: NO INPUTS
        OUTPUT: DATAFRAME
        """
        return pd.read_csv(self.datafile)

    def data_writer(self, df):
        """
        INPUT: DATAFRAME
        OUTPUT: NONE
        """
        pd.to_csv(self.datafile)


class ScrapingClass(Base, CSV):
    pass

class Timer:    
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.interval = self.end - self.start


def file_validator(name, filepath):
    if not filepath:
        raise ValueError(f"{name} must be provided with a path")


def url_validator(url):
    regex = re.compile(
        r"^(?:http)s?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    if not re.match(regex, res):
        raise ValueError("Not a valid url")
    return url


def ratelimit(duration=0.5):
    "A function that handles the rate of your calls."
    time.sleep(duration)


class LogFile:
    def __init__(self, file, mode):
        self.file = file
        self.mode = mode

    def __str__(self):
        return f"Logfile {self.file}"

    def __repr__(self):
        return f"Logfile {self.file} in mode {self.mode}"

    def write(self, content):
        with open(self.file, self.mode) as f:
            f.write(content)

    def read(self):
        with open(self.file, "r") as f:
            content = f.read()
        return content


def construct_query(url, params=None):
    "Function to construct a url from a url and parameters as a dict. Can handle urls with existing parameters"
    result = urllib.parse.urlparse(url)
    if params:
        join_char = (
            "&" if result[4] else "?"
        )  # Picks the join_char based on whether url parameter string is empty
        return result.geturl() + "{0}{1}".format(
            join_char, "&".join("{0}={1}".format(k, v) for (k, v) in params.items())
        )
    return result.geturl()


class Connector:
    def __init__(
        self,
        logfile,
        overwrite_log=False,
        connector_type="requests",
        session=False,
        path2selenium="",
        n_tries=5,
        timeout=30,
    ):
        """This Class implements a method for reliable connection to the internet 
            and monitoring. It handles simple errors due to connection problems, and logs 
            a range of information for basic quality assessments

        Keyword arguments:
        logfile -- path to the logfile
        overwrite_log -- bool, defining if logfile should be cleared (rarely the case). 
        connector_type -- use the 'requests' module or the 'selenium'. 
                          Will have different since the selenium webdriver does not have a 
                          similar response object when using the get method, and 
                          monitoring the behavior cannot be automated in the same way.
        session -- requests.session object. For defining custom headers and proxies.
        path2selenium -- str, sets the path to the geckodriver needed when using selenium.
        n_tries -- int, defines the number of retries the *get* method will try to avoid 
                   random connection errors.
        timeout -- int, seconds the get request will wait for the server to respond, 
                   again to avoid connection errors.
        """

        # Initialization function defining parameters.
        # For avoiding triviel error e.g. connection errors, this defines how many times it will retry.
        self.n_tries = n_tries
        # Defining the maximum time to wait for a server to response.
        self.timeout = timeout
        # not implemented here, if you use selenium.
        if connector_type == "selenium":
            assert (
                path2selenium != ""
            ), "You need to specify the path to you geckodriver if you want to use Selenium"
            from selenium import webdriver

            # HIN download the latest geckodriver here: https://github.com/mozilla/geckodriver/releases

            assert os.path.isfile(
                path2selenium
            ), "You need to insert a valid path2selenium the path to your geckodriver. You can download the latest geckodriver here: https://github.com/mozilla/geckodriver/releases"
            # start the browser with a path to the geckodriver.
            self.browser = webdriver.Firefox(executable_path=path2selenium)

        self.connector_type = connector_type  # set the connector_type

        if session:  # set the custom session
            self.session = session
        else:
            self.session = requests.session()
        self.logfilename = logfile  # set the logfile path
        # define header for the logfile
        header = [
            "id",
            "project",
            "connector_type",
            "t",
            "delta_t",
            "url",
            "redirect_url",
            "response_size",
            "response_code",
            "success",
            "error",
        ]

        if os.path.isfile(logfile):
            if overwrite_log == True:
                self.log = LogFile(logfile, "w")
                self.log.write(";".join(header))
                self.log.mode = "a"
            else:
                self.log = LogFile(logfile, "a")
        else:
            self.log = LogFile(logfile, "w")
            self.log.write(";".join(header))
            self.log.mode = "a"

        # load log
        l = self.log.read().split("\n")
        if len(l) <= 1:
            self.id = 0
        else:
            self.id = int(l[-1][0]) + 1

    def get(self, url, project_name, params=None):
        """Method for connector reliably to the internet, with multiple tries and simple 
            error handling, as well as default logging function.
        Input url and the project name for the log (i.e. is it part of mapping the domain, 
        or is it the part of the final stage in the data collection).

        Keyword arguments:
        url -- str, url
        project_name -- str, Name used for analyzing the log. Use case could be the 
                            'Mapping of domain','Meta_data_collection','main data collection'. 
        params -- dict, Mapping of parameters to be used in the url.
        """

        # make sure the default csv seperator is not in the project_name.
        project_name = project_name.replace(";", "-")
        if self.connector_type == "requests":  # Determine connector method.
            # for loop defining number of retries with the requests method.
            for _ in range(self.n_tries):
                ratelimit()
                t = time.time()
                try:  # error handling
                    response = self.session.get(
                        url, params=params, timeout=self.timeout
                    )  # make get call

                    # define python error variable as empty assumming success.
                    err = ""
                    success = True  # define success variable
                    redirect_url = (
                        response.url
                    )  # log current url, after potential redirects
                    # define delta-time waiting for the server and downloading content.
                    dt = t - time.time()
                    # define variable for size of html content of the response.
                    size = len(response.text)
                    response_code = response.status_code  # log status code.
                    # log...
                    call_id = self.id  # get current unique identifier for the call
                    self.id += 1  # increment call id
                    # ['id','project_name','connector_type','t', 'delta_t', 'url', 'redirect_url','response_size', 'response_code','success','error']
                    # define row to be written in the log.
                    row = [
                        call_id,
                        project_name,
                        self.connector_type,
                        t,
                        dt,
                        url,
                        redirect_url,
                        size,
                        response_code,
                        success,
                        err,
                    ]
                    self.log.write("\n" + ";".join(map(str, row)))  # write log.
                    # return response and unique identifier.
                    return response, call_id

                except Exception as e:  # define error condition
                    err = str(e)  # python error
                    response_code = ""  # blank response code
                    success = False  # call success = False
                    size = 0  # content is empty.
                    redirect_url = ""  # redirect url empty
                    dt = t - time.time()  # define delta t

                    # log...
                    call_id = self.id  # define unique identifier
                    self.id += 1  # increment call_id

                    row = [
                        call_id,
                        project_name,
                        self.connector_type,
                        t,
                        dt,
                        url,
                        redirect_url,
                        size,
                        response_code,
                        success,
                        err,
                    ]  # define row
                    # write row to log.
                    self.log.write("\n" + ";".join(map(str, row)))
        else:
            t = time.time()
            ratelimit()
            url = construct_query(url, params=params)
            self.browser.get(url)  # use selenium get method
            # log
            call_id = self.id  # define unique identifier for the call.
            self.id += 1  # increment the call_id
            err = ""  # blank error message
            success = ""  # success blank
            redirect_url = self.browser.current_url  # redirect url.
            # get time for get method ... NOTE: not necessarily the complete load time.
            dt = t - time.time()
            # get size of content ... NOTE: not necessarily correct, since selenium works in the background, and could still be loading.
            size = len(self.browser.page_source)
            response_code = ""  # empty response code.
            row = [
                call_id,
                project_name,
                self.connector_type,
                t,
                dt,
                url,
                redirect_url,
                size,
                response_code,
                success,
                err,
            ]  # define row
            # write row to log file.
            self.log.write("\n" + ";".join(map(str, row)))
            # Using selenium it will not return a response object, instead you should call the browser object of the connector.
            # connector.browser.page_source will give you the html.
            return None, call_id
