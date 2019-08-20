#######################################################################
#
#       COPYRIGHT 2005 MAYA DESIGN, INC., ALL RIGHTS RESERVED.
#
# ALL INTELLECTUAL PROPERTY RIGHTS IN THIS PROGRAM ARE OWNED BY MAYA DESIGN.
# THIS PROGRAM CONTAINS CONFIDENTIAL AND PROPRIETARY INFORMATION OWNED BY MAYA
# DESIGN AND MAY NOT BE DISCLOSED TO ANY THIRD PARTY WITHOUT THE PRIOR CONSENT
# OF MAYA DESIGN.  THIS PROGRAM MAY ONLY BE USED IN ACCORDANCE WITH THE TERMS
# OF THE APPLICABLE LICENSE AGREEMENT FROM MAYA DESIGN. THIS LEGEND MAY NOT BE
# REMOVED FROM THIS PROGRAM BY ANY PARTY.
#
# THIS LEGEND AND ANY MAYA DESIGN LICENSE DOES NOT APPLY TO ANY OPEN SOURCE
# SOFTWARE THAT MAY BE PROVIDED HEREIN.  THE LICENSE AGREEMENT FOR ANY OPEN
# SOURCE SOFTWARE, INCLUDING WHERE APPLICABLE, THE GNU GENERAL PUBLIC LICENSE
# ("GPL") AND OTHER OPEN SOURCE LICENSE AGREEMENTS, IS LOCATED IN THE SOURCE
# CODE FOR SUCH SOFTWARE.  NOTHING HEREIN SHALL LIMIT YOUR RIGHTS UNDER THE
# TERMS OF ANY APPLICABLE LICENSE FOR OPEN SOURCE SOFTWARE.
#######################################################################
"""
"""

###############################################################################
#
###############################################################################
from xml.sax import saxutils
import urllib
from Parsers.TextScrapParser import TextScrapParser
from MAYA.VIA import uuid, uform





###############################################################################
#
###############################################################################
class TextScrap2Html(TextScrapParser):
    
    _TAG_ = {"bold": "b",
             "italic": "i",
             "underline" : "u",
             "strike" : "strike",
             "text_color" : ("span", "color"),
             "font" : ("span", "font-family"),
             "size" : ("span", "font-size"),
             "link" : ("a", "href"),
             "back_color" : ("span", "background-color")}
             
             
    def __init__(self, url_fmt=None, constructor_url=None):
        self._html = ""        
        self._tags = []
        self._url_fmt = url_fmt or "%s?concept=%s"
        self._contructor_url = constructor_url or "/"
        
    def convert(self, uf):
        self._html = ""
        self._tags = []
        self.parse(uf)
        # get the title
        
        return self._html
    
    def onEvent(self, event, param=None):
        
        if event == "text":
            self._html = "%s%s"%(self._html,
                                 (((saxutils.escape(param)).replace("\n", "<br />")).replace("  ", " &nbsp;")))
        elif event == "style on":
            tag = self._TAG_[param[0]]

            if type(tag) == type(()):
                if tag[0] == "a":
                    bp_uuid = param[1][1]
                    concept = param[1][0]
                    if uform.isa(concept):
                        concept = concept.uuid
                    if uform.isa(bp_uuid):
                        bp_uuid = bp_uuid.uuid
                        
                    if bp_uuid: # has blueprint:
                        val = self._url_fmt%(urllib.quote_plus(bp_uuid.toString(),safe=""),
                                             urllib.quote_plus(concept.toString(),safe=""))
                                             
                    else: # only concept
                        val = self._url_fmt%(self._constructor_url,
                                             urllib.quote_plus(concept.toString(),safe=""))
                else:
                    val = str(param[1])
                try:
                    tag_html = """%s %s="%s" """%(tag[0],
                                                  tag[1],
                                                  saxutils.escape(val))
                except IndexError:
                    tag_html = tag[0]
                tag_name = tag[0]
            else:
                tag_html = tag
                tag_name = tag
                
            self._html = "%s<%s>"%(self._html,
                                   tag_html)
            
            self._tags.append((tag_name, tag_html))
            # print self._tags
        elif event == "style off":
            tag = self._TAG_[param[0]]

            if type(tag) == type(()):
                tag = tag[0]
                    
            # to create well-formed HTML we need to make sure we're not
            # closing tags in wacked out order. so we close all the
            # nested one, close this one, then reopen the nested ones
            last_tag, last_tag_html = self._tags.pop()


            if last_tag != tag:
                nested_tags = []
                # print "Want to close %s, so closing %s first"%(tag, last_tag)
                # close the nested ones
                while last_tag != tag:
                    self._html = "%s</%s>"%(self._html, last_tag)
                    nested_tags.append((last_tag, last_tag_html))
                    last_tag, last_tag_html = self._tags.pop()
                    
                # close this one
                self._html = "%s</%s>"%(self._html,
                                        tag)
                
                # reopen the nested ones
                for i in range(len(nested_tags)):
                    self._html = "%s<%s>"%(self._html,
                                           nested_tags[i][1])
                    self._tags.append(nested_tags[i])
                    
            else:
                self._html = "%s</%s>"%(self._html,
                                        tag)
        elif event == "done":
            pass

