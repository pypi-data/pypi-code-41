# -*- coding: utf-8 -*-
"""
Call this method from the terminal to analyse and print a profiler result file 
created using cProfile:
    
    >>> python -m cProfile -o <name_of_profile_file> <name_of_script>
    
The name of the profile can be parsed using the --name option, other options is
--totnum, that is, if --totnum=10, the 
first 10 slowest processes will be printed.
"""

import pstats
from optparse import OptionParser
from os.path import exists

opts = OptionParser(usage='')
opts.add_option('--name', dest="name", default=None)
opts.add_option('--totnum', dest="totnum", default=20)

if __name__ == "__main__":
    (options, args) = opts.parse_args()
    name = options.name
    if name is None or not exists(name):
        name = str(input("Enter name of profile file in this directory\n"))
        if not exists(name):
            raise IOError("File %s not found.." % opts.name)

    stats = pstats.Stats(name)
    stats.sort_stats("tottime")

    stats.print_stats(options.totnum)
