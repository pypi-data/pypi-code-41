#!/usr/bin/env python
# todo: ImageHandler process raw image data
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.gen

import json
import os
import time
import uuid
import base64
import requests
import numpy as np
import cv2
from .dlogger import dlogger

cur_path = os.path.dirname(__file__)  # current path
__PAGE__ = os.path.join(cur_path, 'index/')  # storage path for demo page


class HealthHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('OK')


class BaseHandler(tornado.web.RequestHandler):
    def initialize(self, app_name):
        self.dlog = dlogger(app_name)

    @staticmethod
    def decode_image(b64):
        npimage = np.fromstring(b64, np.uint8)
        img_restore = cv2.imdecode(npimage, cv2.IMREAD_COLOR)
        return img_restore

    @tornado.gen.coroutine
    def post(self):

        uid = str(uuid.uuid1())
        self.dlog.debug(uid + ' start...')
        start = time.time()
        self.set_header("Content-Type", "application/json")
        try:
            req = json.loads(self.request.body)
            res = self.algorithm(req)
            self.write(json.dumps(res, ensure_ascii=False))
        except Exception as e:
            self.dlog.debug(uid + ' error: ' + str(e))
            self.write(json.dumps({"success": False, "message": str(e)}))

        estime = round((time.time() - start) * 1000, 2)
        self.dlog.debug(uid + ' end[%.2fms]' % estime)

    @staticmethod
    def build_resp(rst):
        resp = {}
        if rst[0]:
            resp['success'] = True
            resp['message'] = ""
            resp['result'] = rst[1]
        else:
            resp['success'] = False
            resp['message'] = rst[1]
        return resp

    def algorithm(self, req):
        """
        define you algorithm to do somthing
        """
        image, res = self.build_image(req)
        if not res["success"]:
            return res
        
        ret = "hello tarnado!"

        return self.build_resp(True, ret)

    def build_image(self, req):

        image_type = req.get("image_type")
        if not image_type:
            return self.build_resp((False, "missing param: image_type"))
        if image_type == "base64":
            image_b64 = req.get("image_base64")
            if not image_b64:
                return None, self.build_resp((False, "missing param: image_base64"))
            image = base64.b64decode(image_b64)
            npimage = self.decode_image(image)
        elif image_type == "url":
            image_url = req.get("image_url")
            if not image_url:
                return None, self.build_resp((False, "missing param: image_url"))
            try:
                res = requests.get(image_url, timeout=5)
                if res.status_code != 200:
                    return None, self.build_resp((False, "download image failed"))
                image = res.content
                npimage = self.decode_image(image)
            except requests.exceptions.Timeout:
                return None, self.build_resp((False, "download image timeout"))
            except Exception as e:
                return None, self.build_resp((False, "download image failed: " + str(e)))
        else:
            return None, self.build_resp((False, "invalid image_type"))

        return npimage, self.build_resp((True, "check image success"))


def deploy(port, handler):
    app_name = getattr(handler, '__name__')
    app = tornado.web.Application(
        handlers=[
            (r"/health", HealthHandler),
            (r"/inference", handler, dict(app_name=app_name)),
            (r'/(.*)', tornado.web.StaticFileHandler, {'path': __PAGE__})
        ]
    )
    sockets = tornado.netutil.bind_sockets(port)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.add_sockets(sockets)
    print("webapp:{} start listening port {}".format(app_name, port))
    tornado.ioloop.IOLoop.instance().start()
