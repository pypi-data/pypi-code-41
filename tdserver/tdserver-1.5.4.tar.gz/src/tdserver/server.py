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
            image, res = self.build_image(req)
            res = self.algorithm(req, image)
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

    def algorithm(self, req, image):
        """
        define you algorithm to do somthing
        """

        ret = "hello tornado!"

        return self.build_resp((True, ret))

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


class BinaHandler(tornado.web.RequestHandler):
    def initialize(self, app_name):
        self.dlog = dlogger(app_name)

    def post(self):
        files = self.request.files
        # 默认取第一张图片
        try:
            img = np.asarray(bytearray(files['img_raw'][0]['body']), dtype=np.uint8)
            image = cv2.imdecode(img, cv2.IMREAD_COLOR)
            ret = self.algorithm(image)
            self.write(json.dumps(ret, ensure_ascii=False))
        except Exception as e:
            return BaseHandler.build_resp((False, str(e)))

    def algorithm(self, image):
        """
        alporithm process
        :param image: is good image
        :return:
        """
        return BaseHandler.build_resp((True, "process success"))


def deploy(port, handler):

    app_name = getattr(handler, '__name__')
    base = str(getattr(handler, '__bases__')[0])
    use_bs64 = False
    if 'BaseHandler' in base:
        handlers = [
            (r"/health", HealthHandler),
            (r"/inference", handler, dict(app_name=app_name)),
            (r"/(.*)", tornado.web.StaticFileHandler, {'path': __PAGE__})
        ]
        use_bs64 = True
    else:
        handlers = [
            (r"/health", HealthHandler),
            (r"/inference", handler, dict(app_name=app_name)),
            (r"/(.*)", tornado.web.StaticFileHandler, {'path': __PAGE__})
        ]
    app = tornado.web.Application(handlers=handlers)
    sockets = tornado.netutil.bind_sockets(port)

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.add_sockets(sockets)
    print("webapp:{} start listening port {} use_bs64 {}".format(app_name, port, str(use_bs64)))
    tornado.ioloop.IOLoop.instance().start()

