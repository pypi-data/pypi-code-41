import os
import shutil
import pkg_resources
import argparse
from efdir import fs
import sys
import pyminiproj




TEM = pkg_resources.resource_filename("pyminiproj","proj-tem.zip")





PARAMS = ["projname","username","email","scheme","author"]





parser = argparse.ArgumentParser()
parser.add_argument('-projname','--projname', default="",help="git repository names")
parser.add_argument('-username','--username', default="",help="git config --local user.name")
parser.add_argument('-password','--password', default="",help="git password")
parser.add_argument('-email','--email', default="",help="git config --local user.email")
parser.add_argument('-scheme','--scheme', default="https",help="https or git")
parser.add_argument('-author','--author', default="",help="used in setup.py")


ARGS = parser.parse_args()

if(ARGS.author == ""):
    ARGS.author = ARGS.username
else:
    pass

shutil.copy(TEM,"proj-tem.zip")
fs.unzip("proj-tem.zip")
os.system('mv @PROJNAME@ '+ARGS.projname)
os.system('rm proj-tem.zip')
os.system('mv '+ARGS.projname+'/main '+ ARGS.projname+'/'+ARGS.projname)

def replace_each(fn):
    s = fs.rfile(fn)
    for each in PARAMS:
        s = s.replace("@"+each+"@",ARGS.__getattribute__(each))
    fs.wfile(fn,s)

def creat_proj():
    files = fs.walkf(ARGS.projname)
    for fn in files:
        replace_each(fn)

def main():
    creat_proj()
    if(sys.platform == "linux"):
        CHMOD = "chmod 777 -R ./"+ARGS.projname+"/*.sh"
        os.system(CHMOD)
        CHMOD = "chmod 777 -R ./"+ARGS.projname+"/INIT/*.sh"
        os.system(CHMOD)
    else:
        pass

