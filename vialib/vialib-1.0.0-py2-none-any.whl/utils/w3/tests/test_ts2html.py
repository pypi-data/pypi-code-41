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

Seung Chan Lim ( slim@maya.com )
"""

###############################################################################
#
###############################################################################
import sys
sys.path.insert(0, "../")
from MAYA.VIA import uuid, uform, repos
from MAYA.utils.w3.textscrap2html import TextScrap2Html




###############################################################################
#
###############################################################################
if __name__ == "__main__":
    r = repos.Repository("joshua.maya.com:8889")
    uu = uuid.fromString("python-renex")
    uf = r.getAttr(uform.UForm(uu, {"text_content" : "",
                                    "text_bold" : [],
                                    "text_italic" : [],
                                    "text_underline" : [],
                                    "text_strikethrough" : [],
                                    "text_text_colors" : [],
                                    "text_text_color_regions" : [],
                                    "text_back_colors" : [],
                                    "text_back_color_regions" : [],
                                    "text_fonts" : [],
                                    "text_font_regions" : [],
                                    "text_sizes" : [],
                                    "text_size_regions" : [],
                                    "text_link_regions" : [],
                                    "text_link_concepts" : [],
                                    "text_link_blueprint_targets" : [],
                                    }))

    t = TextScrap2Html()
    print "<pre>%s</pre>"%(t.convert(uf))


    
