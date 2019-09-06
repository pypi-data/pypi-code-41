#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys
# import xytool.packagePB.platform.brew_package
import xytool.packagePB.platform.pypi_package
from xytool.xylog import warninglog,faillog

__all__ = ['pypi','brew','all']

def main():
    platform = sys.argv[1]
    if platform not in __all__:
        faillog("please an platform in pypi,brew and all!")
        sys.exit()
    

if __name__ == '__main__':
    main()
    