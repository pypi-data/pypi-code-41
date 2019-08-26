#!/usr/bin/env python

# This file is part of Pymetrick.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

import sys
import os
import re
import urllib
import urllib2


# Available Sitemap types
SITEMAP_TYPES = ['web', 'mobile', 'news']
# General Sitemap tags
GENERAL_SITEMAP_TAGS = ['loc', 'changefreq', 'priority', 'lastmod']

# News specific tags
NEWS_SPECIFIC_TAGS = ['keywords', 'publication_date', 'stock_tickers']

# News Sitemap tags
NEWS_SITEMAP_TAGS = GENERAL_SITEMAP_TAGS + NEWS_SPECIFIC_TAGS

# Maximum number of urls in each sitemap, before next Sitemap is created
MAXURLS_PER_SITEMAP = 50000

# Suffix on a Sitemap index file
SITEINDEX_SUFFIX = '_sitemap.xml'

# Regular expressions tried for extracting URLs from access logs.
ACCESSLOG_CLF_PATTERN = re.compile(r'.+\s+"([^\s]+)\s+([^\s]+)\s+HTTP/\d+\.\d+"\s+200\s+.*')

# XML formats
GENERAL_SITEINDEX_HEADER = \
  '<?xml version="1.0" encoding="UTF-8"?>\n' \
  '<sitemapindex\n' \
  ' xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n' \
  ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n' \
  ' xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9\n' \
  ' http://www.sitemaps.org/schemas/sitemap/0.9/' \
  'siteindex.xsd">\n'

NEWS_SITEINDEX_HEADER = \
  '<?xml version="1.0" encoding="UTF-8"?>\n' \
  '<sitemapindex\n' \
  ' xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n' \
  ' xmlns:news="http://www.google.com/schemas/sitemap-news/0.9"\n' \
  ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n' \
  ' xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9\n' \
  ' http://www.sitemaps.org/schemas/sitemap/0.9/' \
  'siteindex.xsd">\n'

SITEINDEX_FOOTER = '</sitemapindex>\n'
SITEINDEX_ENTRY = \
  ' <sitemap>\n' \
  ' <loc>%(loc)s</loc>\n' \
  ' <lastmod>%(lastmod)s</lastmod>\n' \
  ' </sitemap>\n'
GENERAL_SITEMAP_HEADER = \
  '<?xml version="1.0" encoding="UTF-8"?>\n' \
  '<urlset\n' \
  ' xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n' \
  ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n' \
  ' xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9\n' \
  ' http://www.sitemaps.org/schemas/sitemap/0.9/' \
  'sitemap.xsd">\n'

NEWS_SITEMAP_HEADER	= \
  '<?xml version="1.0" encoding="UTF-8"?>\n' \
  '<urlset\n' \
  ' xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n' \
  ' xmlns:news="http://www.google.com/schemas/sitemap-news/0.9"\n' \
  ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n' \
  ' xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9\n' \
  ' http://www.sitemaps.org/schemas/sitemap/0.9/' \
  'sitemap.xsd">\n'

MOBILE_SITEMAP_HEADER = \
  '<?xml version="1.0" encoding="UTF-8" ?>\n' \
  '<urlset\n' \
  ' xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n' \
  ' xmlns:mobile="http://www.google.com/schemas/sitemap-mobile/1.0">\n' \
  ' <url>\n' \
  '     <loc>%(loc)s</loc>\n' \
  '     <mobile:mobile/>\n' \
  ' </url>\n' \
  '</urlset>\n'

def buscar(proxyAuth=None,proxyPasswd=None):
    try:

        if proxyAuth is not None and proxyPasswd is not None:
            proxy = urllib2.ProxyHandler({'http': 'http://%s:%s@proxyinternet.tesa:8080' % (proxyAuth,proxyPasswd)})
            auth = urllib2.HTTPBasicAuthHandler()
            opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler)
            urllib2.install_opener(opener)

        url = "http://www.garrachon.es"
        site = urllib2.urlopen(url)
        html_string = site.read()
        site.close()
        print (html_string)

        match = re.findall(r'href=[\'"]?([^\'" >]+)', html_string)
        for n in match:
            n = n.replace('http://','').replace('https://','')
            if n.startswith(url.replace('http://','')):
                print(n)
            elif n.startswith('/'):
                print (n)

	    # Open our local file for writing
        """local_file = open(file_name, "w" + file_mode)
	    #Write to our local file
	    local_file.write(f.read())
	    local_file.close()"""

    #handle errors
    except urllib2.HTTPError as e:
        print (e.code)
    except urllib2.URLError as e:
        print (e.args)

def getgoogleurl(search,siteurl=False):
    if siteurl==False:
        return 'http://www.google.com/search?q='+urllib2.quote(search)+'&oq='+urllib2.quote(search)
    else:
        return 'http://www.google.com/search?q=site:'+urllib2.quote(siteurl)+'%20'+urllib2.quote(search)+'&oq=site:'+urllib2.quote(siteurl)+'%20'+urllib2.quote(search)

def getgooglelinks(search,siteurl=False,proxyAuth=None,proxyPasswd=None):
   #google devolvera 403 si no se envia un user-agent valido
   headers = {'User-agent':'Mozilla/11.0'}
   if proxyAuth is not None and proxyPasswd is not None:
       proxy = urllib2.ProxyHandler({'http': 'http://%s:%s@proxyinternet.tesa:8080' % (proxyAuth,proxyPasswd)})
       auth = urllib2.HTTPBasicAuthHandler()
       opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler)
       urllib2.install_opener(opener)

   req = urllib2.Request(getgoogleurl(search,siteurl),None,headers)
   site = urllib2.urlopen(req)
   data = site.read()
   site.close()

   #no beatifulsoup because google html is generated with javascript
   start = data.find('<div id="res">')
   end = data.find('<div id="foot">')
   if data[start:end]=='':
      #error, no links to find
      return False
   else:
      links =[]
      data = data[start:end]
      start = 0
      end = 0
      while start>-1 and end>-1:
          #get only results of the provided site
          if siteurl==False:
            start = data.find('<a href="/url?q=')
          else:
            start = data.find('<a href="/url?q='+str(siteurl))
          data = data[start+len('<a href="/url?q='):]
          end = data.find('&amp;sa=U&amp;ei=')
          if start>-1 and end>-1:
              link =  urllib2.unquote(data[0:end])
              data = data[end:len(data)]
              if link.find('http')==0:
                  links.append(link)
      return links

if __name__ == "__main__":
    """Ejemplos"""


