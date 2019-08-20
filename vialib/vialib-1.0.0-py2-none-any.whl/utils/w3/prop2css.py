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



###############################################################################
#
###############################################################################
def punitToPt(punit):
    """
    1pt = 1/72 inches
    1 inch = 2540 punits
    """
    
    return _PUNIT_TO_PT_FACTOR_ * float(punit)





###############################################################################
#
###############################################################################
_PUNIT_TO_PT_FACTOR_ = (72.0 / 2540.0)

_PROP_ = {"x" : ("left", (punitToPt, "pt")),
          "y" : ("top", (punitToPt, "pt")),
          }


###############################################################################
#
###############################################################################
def translate(prop, val):
    """
    given a property and its value the equivalent CSS syntax is returned
    """

    try:

        css = _PROP_[prop]
    except KeyError:

        raise "Unknown Property"
    else:
        if type(css) == type(()):
            assert(len(css) == 2)
            
            css_syntax = "%s:"%(css[0])

            if type(css[1]) == type(()):
                # conversion
                val = apply(css[1][0], (val,))

                css_syntax = "%s%.2f%s;"%(css_syntax,
                                         val,
                                         css[1][1])


        return css_syntax
