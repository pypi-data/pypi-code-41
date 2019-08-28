""" Writen by Rafael Rayes, Tangly will help you transforming
a list into a table.
USAGE:


import tangly

my_list = [['this', 'that'],
           ['these', 'those'],]

tangly.table(my_list)
"""
try:
    from . import helping, tablef
    from helping import *
    from tablef import *
except:
    raise Exception('Tangly failed to load.')
name = 'Tangly'
version = '2.1.3'
