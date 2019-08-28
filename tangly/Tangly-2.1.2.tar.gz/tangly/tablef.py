# table function for tanly

def printar(your_list, first_column, second_column, third_column):
    pa = []
    pa.append('┌')
    pa.append('─'*(len(first_column)+3))
    pa.append('┬')
    pa.append('─'*(len(second_column)+3))
    if any(len(i) == 3 for i in your_list):
        pa.append('┬')
        pa.append('─'*(len(third_column)+3))
    pa.append('┐')
    print(''.join(pa))
    if any(len(i) == 3 for i in your_list):
        print("│",first_column," │", second_column, " │", third_column, " │")
    else:
        print("│",first_column," │", second_column, " │")
    pa[0] = '├'
    pa.reverse()
    pa[0] = '┤'
    pa.reverse()
    pa[2] = '┼'
    if any(len(i) == 3 for i in your_list):
        pa[4] = '┼'
    else:
        pa[4] = '┤'
    print(''.join(pa))
    
    for i in your_list:
        try:
            print("│",i[0], " "*(len(first_column)-len(i[0])), "│",
                i[1], " "*(len(second_column)-len(i[1])), "│",
                i[2], " "*(len(third_column)-len(i[2])), "│",)
        except:
            print("│",i[0], " "*(len(first_column)-len(i[0])), "│",
            i[1], " "*(len(second_column)-len(i[1])), "│",)
            
    pa[0] = '└'
    pa[2] = '┴'
    pa[4] = '┴'
    pa.reverse()
    pa[0] = '┘'
    pa.reverse()
    print(''.join(pa))
def aumentar(your_list, first_column, second_column, third_column='third'):
    for item in your_list:
        while len(item[0]) > len(first_column):
            first_column = first_column + ' '
        while len(item[1]) > len(second_column):
            second_column = second_column + ' '
        try:
            while len(item[2]) > len(third_column):
                third_column = third_column + ' '
        except:
            pass
    printar(your_list, first_column, second_column, third_column)

def checar(your_list, first_column, second_column, third_column):
    for i in your_list:
        if len(i) > 2:
            global c
            c = 3
            aumentar(your_list, first_column, second_column, third_column) 
            break
        elif len(i) == 1:
            print("your list must have at least 2 columns")
            break
        else:
            aumentar(your_list, first_column, second_column)
            break
def table(your_list, first_column = 'first', second_column='second', third_column = 'third'):
    checar(your_list, first_column, second_column, third_column)
