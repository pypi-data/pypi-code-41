import os
import sys
import re

from timeit import default_timer as timer
from datetime import datetime, timedelta

from mkdocs import utils as mkdocs_utils
from mkdocs.config import config_options, Config
from mkdocs.plugins import BasePlugin

class FileSelector(BasePlugin):

    config_scheme = (
        ('param', config_options.Type(mkdocs_utils.string_types, default='')),
    )

    def getFirst (self, paths, config):
      for f in paths:
        f=f.replace(" ", "");

        if os.path.exists(config['docs_dir']+'/../includes/'+f):
          return f

      print("No file was found! Returning: " + f +" on path: " + config['docs_dir']+'/../includes/'+f)
      return f

    def _init_(self):
        self.enabled = True
        self.total_time = 0

    def on_page_markdown(self, markdown, page, config, site_navigation=None, **kwargs):
        result = re.search('({\?(.?[^{}?]*)\?})', markdown)

        while result:

          target = result.group(2)
          result = result.group(1)

          paths = str(target).split('|')
          good = self.getFirst(paths, config)

          markdown = markdown.replace(result, "{! " + good + " !}")

          result = re.search('({\?(.?[^{}?]*)\?})', markdown)

        return markdown