"""
Utility classes for common tasks
"""
from .client import Client
from .resources import TaskStatus
from .resources import Url, RasterizeResults, ImageFile
import requests
import time


class RasterizeException(Exception):
     def __init__(self,message):
        super(RasterizeException,self).__init__(message)
        self.message=message


class RasterizeTimeout(RasterizeException):
    def __init__(self,message):
        super(RasterizeTimeout,self).__init__(message)
        self.message=message


class RasterizeAndRetrieveImage(object):
    def __init__(self, client: Client, url: str, timeout=120):
        self.client = client
        self.url = url
        self.timeout = timeout

    def get_screenshot(self):
        """
        raises RasterizeException, RasterizeTimeout
        :return: dict(filename,response)
        """
        url_resource = Url(self.client)
        url_resource.rasterize(self.url)
        res = url_resource.full_request()
        if res["status"] != "Success":
            raise RasterizeException(str(res))
        timeout_start = time.time()
        while True:
            if time.time() > timeout_start + self.timeout:
                raise RasterizeTimeout("Timeout reached" + str(self.timeout))
            status_resource = TaskStatus(self.client)
            status_resource.check(res["data"]["task_hash"])
            res_stat = status_resource.full_request()
            if res_stat["status"] != "Success":
                raise RasterizeException(str(res_stat))
            if res_stat["data"]["task_status"] == "completed":
                image_url_resource = RasterizeResults(self.client)
                image_url_resource.retrieve(task_hash=res_stat["data"]["task_hash"])
                res_image_url = image_url_resource.full_request()
                if res_image_url["status"] != "Success":
                    raise RasterizeException(str(res_image_url))
                else:
                    image_file_resource = ImageFile(self.client)
                    url_png = res_image_url["data"]["results"][0]["page_png"]
                    image_file_resource.retrieve(url_png)
                    res_file = image_file_resource.full_request()
                    if res_file["status"] == "Success":
                        filename = url_png.rsplit("/",1)[1]
                        res_dict = {"filename":filename, "data":res_file["data"]}
                        return res_dict
                    else:
                        raise RasterizeException(str(res_file))
            time.sleep(10)

