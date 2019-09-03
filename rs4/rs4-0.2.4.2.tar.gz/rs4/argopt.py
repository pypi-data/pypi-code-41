import getopt as optparse
import sys

long_opts = []
short_opts = []

def add_option (lname = None, sname = None):
    global long_opts, short_opts    
    if lname:
        if lname.startswith ("--"):
            lname = lname [2:]
        long_opts.append (lname)

    if sname:
        if sname.startswith ("-"):
            sname = sname [1:]        
        short_opts.append (sname)

def add_options (*names):
    for name in names:
        assert name and name [0] == "-"
        if name.startswith ("--"):
            add_option (name [2:])
        else:
            add_option (None, name [1:])

class ArgumentOptions:
    def __init__ (self, kopt = {}, argv = []):
        self.__kopt = kopt
        self.argv = argv

    def items (self):
        return self.__kopt.items ()

    def __contains__ (self, k):
        return k in self.__kopt

    def get (self, k, v = None):
        return self.__kopt.get (k, v)

    def set (self, k, v = None):
        self.__kopt [k] = v

    def remove (self, k):
        try:
            del self.__kopt [k]
        except KeyError:
            pass  

def options ():
    global long_opts, short_opts
    
    argopt = optparse.getopt (sys.argv [1:], "".join (short_opts).replace ("=", ":"), long_opts)
    kopts_ = {}
    for k, v in argopt [0]:
        if k in kopts_:
            if not isinstance (kopts_ [k], list):
                kopts [k] = {kopts [k]}
            kopts_ [k].add (v)
        else:
            kopts_ [k] = v
    return ArgumentOptions (kopts_, argopt [1])

