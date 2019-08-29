# -*- coding: utf-8 -*-
import os
import subprocess

from univider.logger import Logger

class Render():

    logger = Logger(__name__).getlogger()

    def getDom(self, url, loadImages, timeout):
        path =os.path.dirname(__file__)
        cmd = 'phantomjs ' + path + '/render.js "%s" %s %s '% (url, loadImages, timeout)
        # self.logger.info('cmd:',cmd)
        stdout,stderr = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
        # print stdout
        # print stderr
        return stdout