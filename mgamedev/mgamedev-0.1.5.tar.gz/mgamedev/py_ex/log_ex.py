#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------
# Log extends
# ----------------------------------------------------------------------------

# public functions
# +===================================Dict========================================
# 格式化打印字典


def printTable(tarDict):
    import json
    strdump = json.dumps(tarDict, sort_keys=True, indent=4)
    print(strdump)
