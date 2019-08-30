# cp---copy command
# importing required in-built modules
import os
import shutil


def run(srcfile, destfile, symlinks=False, ignore=None):
    """ this function is called when cp along with
    required arguments are entered in PyShell"""

    # if source is a file
    # defining chunksize to capture at a time, if file is large
    if os.path.isfile(srcfile):
        CHUNK_SIZE = 15000
        try:
            with open(srcfile, "rb") as infile, \
                 open(destfile, "wb") as outfile:
                while True:
                    chunk = infile.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    outfile.write(chunk)
        except Exception:
            print("File not found")

    else:
        try:                               # if source is a directory
            if not os.path.exists(destfile):
                os.mkdir(destfile)
            for item in os.listdir(srcfile):
                s = os.path.join(srcfile, item)
                d = os.path.join(destfile, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, symlinks, ignore)
                else:
                    if not ((os.path.exists(d)) or
                            (os.stat(s).st_mtime - os.stat(d).st_mtime > 1)):
                        run(s, d, False, None)
        except Exception as e:
            print(e)
