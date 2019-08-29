def  printlol2(thelist):
    for item in thelist:
        if isinstance(item,list):
            printlol2(item)
        else:
            print(item)