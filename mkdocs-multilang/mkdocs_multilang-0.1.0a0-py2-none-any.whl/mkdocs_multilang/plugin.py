import os
import sys
import re
import mkdocs
import pprint

from timeit import default_timer as timer
from datetime import datetime, timedelta

from mkdocs import utils as mkdocs_utils
from mkdocs.config import config_options, Config
from mkdocs.plugins import BasePlugin

class MultiLang(BasePlugin):

    config_scheme = (
        ('param', config_options.Type(mkdocs_utils.string_types, default='')),
    )

    def _init_(self):
        self.enabled = True
        self.total_time = 0

    def on_page_content(self, markdown, page, config, site_navigation=None, **kwargs):
        # Localize language specific images
        result = re.search('/(_assets\/img.[^\"\)]*)', markdown)

        while result:
          target = result.group(1)
          result = result.group(0)

          if (os.path.exists(config['docs_dir']+'/'+config['locale']+result)):
            markdown = markdown.replace(result, '/'+config['locale']+'/DeleteMarker'+target)
            print("NEW IMAGE: " + '/'+config['locale']+'/DeleteMarker'+target)
          else:
            markdown = markdown.replace(result, '/DeleteMarker'+target)
          result = re.search('/(_assets\/img.[^\"\)]*)', markdown)

        markdown = markdown.replace('DeleteMarker', '')

        regex = '<a href=\"((/(?!http)(?!/'+config['locale']+').*?)/(#.*)?)\">'

        result = re.search(regex, markdown)        

        while result:
          toReplace = result.group(1)
          toReplaceWith = ""
          path = result.group(2)
          filename = result.group(2) + '.md'
          # print(base)
          if os.path.exists(config['docs_dir']+'/'+config['locale']+filename):
            toReplaceWith = '/' + config['locale'] + path;
            print('from: ' + filename + ' to: ' + toReplaceWith)
          else:
            toReplaceWith = toReplace.replace(path, "DeleteMarker" + path)
          markdown = markdown.replace(toReplace, toReplaceWith)
          result = re.search(regex, markdown)
          # print(result.group(0))
        markdown = markdown.replace('DeleteMarker', '')
        return markdown


    def forSection(self,section):
      for el in section.children:
        if isinstance(el, mkdocs.structure.nav.Section):
          el = self.forSection(el)
        else:
          if isinstance(el, mkdocs.structure.nav.Link):
            el.url = self.forLink(el)
      return section

    def forLink(self, link):
      return link.url.replace('.md', '/')

    def on_nav(self,nav, config, files):
      for el in nav:
        if isinstance(el, mkdocs.structure.nav.Section):
          el = self.forSection(el)
        else:
          if isinstance(el, mkdocs.structure.nav.Link):
            el = self.forLink(el)
      return nav

    def getFirst (self, paths, config):
      for f in paths:
        f=f.replace(" ", "");

        if os.path.exists(config['docs_dir']+'/../includes/'+f):
          return f

      print("No file was found! Returning: " + f +" on path: " + config['docs_dir']+'/../includes/'+f)
      return f

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