"""This is nester.py,which supports a function named print_lol.
This function is to print list, which maybe include another inside list or not"""


def print_lol(the_list,indent=False,level=0):
    """ 这个函数取一个位置参数，名为“the_list”,这可以是任何python列表（也可以是被包含嵌套的列表）。
所指定的列表中的每个数据项会(递归的)输出到屏幕上，各项数据各占一行"""
    for each_item in the_list:
        if isinstance (each_item,list):
                print_lol(each_item,indent,level+1)
        else:
            if indent:
                 for tab_stop in range(level):
                     print ("\t",end='')
            print (each_item)	

		
