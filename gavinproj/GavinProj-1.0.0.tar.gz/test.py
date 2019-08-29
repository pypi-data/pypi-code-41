def  printlol(thelist):
    for item in thelist:
        if isinstance(item,list):
            printlol(item)
        else:
            print(item)



