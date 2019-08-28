def addFractions(list1, list2):
    deno = int(list1[1]) * int(list2[1])
    num1 = int(list1[0]) * int(list2[1])
    num2 = int(list2[0]) * int(list1[1])
    result = [num1 + num2, deno]
    print('(', int(list1[0]), '/', int(list1[1]), ')', '+', '(', int(list2[0]), '/', int(list2[1]), ')')
    print('(', num1, '/', deno, ')', '+', '(', num2, '/', deno, ')', '=', result[0], '/', result[1])
    return result

    
    
