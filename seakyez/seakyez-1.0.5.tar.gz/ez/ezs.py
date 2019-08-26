import math, random, ez, itertools
from decimal import Decimal
from functools import reduce

def argmax(obj, key = None, returnObj = True):
    '''Input obj type can be array-like or a dict.
    Return a list of indices/keys with the maximum value.
    If returnObj, return the first max object. Otherwise, return a list obj max objects.'''
    res = __arghelper(obj, lambda v, value: v > value, key)
    return res[0] if returnObj else res

def argmin(obj, key = None, returnObj = True):
    '''Input obj type can be array-like or a dict.
    Return a list of indices/keys with the minimum value.
    If returnObj, return the first min object. Otherwise, return a list obj min objects.'''
    res = __arghelper(obj, lambda v, value: v < value, key)
    return res[0] if returnObj else res

def __arghelper(obj, booleanExpression, keyFunc) -> list:
    if not obj:
        raise TypeError('Expect Non-empty object.')
    if not isinstance(obj, dict):
        obj = dict(enumerate(obj))
    if not keyFunc:
        keyFunc = lambda x: x
    keys, value = [], None
    for k, v in obj.items():
        V = keyFunc(v)
        Value = keyFunc(value) if value != None else None
        if not keys:
            keys.append(k)
            value = v
        elif booleanExpression(V, Value):
            keys = [k]
            value = v
        elif V == Value:
            keys.append(k)
    return keys

def npMatrixToLatex(matrix, newline = False, printResult = True, copy = True):
    '''Matrix can be any 2d iterable'''
    r = len(matrix)
    c = len(matrix[0])
    result = ml(r, c, ' '.join(str(entry) for row in matrix for entry in row))
    if copy:
        ez.copyToClipboard(result)
    if printResult:
        print(result)
    else:
        return result

##abbreviation
nl = npMatrixToLatex

def product(iterable):
    ''' (Deprecated) Use math.prod (new function of python 3.8) instead.
    Return the numerical product of numbers.
    For Cartesian Product, please use itertools.product instead.'''
    return reduce(lambda x, y: x * y, iterable)

def accurateCalculation(formula = '', scin = False):
    '''Function calls not supported.
        Set scin to True to use scientific notation.
        Abbreviation: ac'''
    def get_result():
        ni = '' ## new i
        try:
            nf = formula.replace('^', '**').lower() ## new formula
        except AttributeError:
            raise Exception('Input formula should be a string.')
        num = ''
        try:
            for i, ch in enumerate(nf):
                if ch.isnumeric() or \
                   (ch == '-' and (i == 0 or nf[i-1] == 'e')) or \
                   (ch == ' + ' and (i == 0 or nf[i-1] == 'e')) or \
                   (ch == 'e' and (nf[i + 1].isnumeric() or nf[i + 1] in [' + ', '-'])) or \
                   (ch == '.' and nf[i + 1].isnumeric()):
                    num += ch
                elif ch == ' ':
                    pass
                else:
                    if num:
                        ni += f'Decimal("{num}")'
                        num = ''
                    ni += ch
            if num:
                ni += f'Decimal("{num}")'
        except:
            raise Exception('Invalid expression: ' + num)
        result = eval(repr(eval(ni))[9:-2])
        return result

    if formula:
        result = get_result()
        if scin:
            result = scin(result, 0)
        return result
    while True:
        formula = input('Input the formula below. Empty input will exit.\n>>> ')
        if formula == '':
            return
        flag = 'scin = '
        if formula.startswith(flag):
            scin = eval(ez.find(formula).after(flag))
            continue
        result = get_result()
        if scin:
            result = scin(result, 0)
        print(result)

##abbreviation
ac = accurateCalculation

def scientificNotation(num, pr = True):
    '''Abbreviation: scin'''
    result = '%e' % num
    if pr:
        print(result)
    else:
        return result

##abbreviation
scin = scientificNotation

def nmb(n, m): ## nmb does not mean nimabi
## This function gives an algorithm which returns all the method
## that you can put n identical balls into m identical boxes
    def recursive(n, m, lst, method = ''):
        if m>1:
            startIdx = 0
            if method != '':
                startIdx = int(method[-2])
            for i in range(startIdx, n//m + 1):
                recursive(n-i, m-1, lst, method + str(i) + '-')
            method = ''
        elif m == 1:
            lst.append(method + str(n))

    methodlst = []
    recursive(n, m, methodlst)
    print(methodlst, len(methodlst), sep = '\n')

def congruenceEquation(a, b, m):
    ''' Find the least positive integer x that satisfies ax≡b(mod m).
        Abbreviation: cE.'''
    if b<0:
        b %= m
    for i in range(m):
        if (a * i) % m == b:
            return i

##abbreviation
cE = congruenceEquation

def chineseRemainderTheorem():
    '''Find solutions to the system of congruences by typing the a, b, m of ax≡b(mod m).
        If a is 1, only b and m are needed.
        Abbrevation: crt.'''
    number = ()
    divisor_dict = {}
    print('Type the a, b, m of ax≡b(mod m). If a is 1, only b and m are needed.')
    while True:
        s = input('Please seperate a, b, m or b, m by space. Order matters. Press Enter to stop.\n>>> ')
        if s and s.find(' ') == -1:
            print('No space detected! Please type again! Correct form: >>> 7 3 15')
            continue
        elif s == '':
            break
        dr = s.split()
        ## x≡dr[0](mod dr[1]) or
        ## dr[0]*x≡dr[1](mod dr[2])
        try:
            dr[0] = int(dr[0])
            dr[1] = int(dr[1])
            if len(dr) == 3:
                dr[2] = int(dr[2])
                dr[0] = congruenceEquation(dr[0], dr[1], dr[2])
                dr[1], dr[2] = dr[2], dr[1]
        except:
            print('Invalid input! Please try again!')
            continue
        if dr[1] <= 0:
            print('Positive divisor only! Please try again!')
            continue
        elif dr[1] in divisor_dict and divisor_dict[dr[0]] != dr[1]:
            print('Inconsistent remainder! Please try again!')
            continue
        elif dr[0]<0 or dr[0]>dr[1]:
            print('Remainder automatically adjusted.')
            dr[0] = dr[0]%dr[1]
        divisor_dict[dr[1]] = [dr[0]]
        if number == ():
            number = (dr[1], dr[0])
        else:
            divisor, remainder = number
            dr[0] = (dr[0] - remainder) % dr[1]
            for i in range(dr[1]):
                if (divisor*i)%dr[1] == dr[0]:
                    number = (lcm(divisor, dr[1]), remainder + i * divisor)
                    break
            else:
                yn = input('Such number doesn\'t exist! Did you just make a typo?\nInput "y" for yes to delete the previous input, "r" to restart. Other input will be regarded as no.\n>>> ').lower()
                if yn == 'y':
                    del divisor_dict[dr[1]]
                    continue
                elif yn == 'r':
                    divisor_dict = {}
                    continue
                else:
                    ## do something?
                    return

    if number == ():
        return
    n0, n1 = number
    formula = 'x'
    if n0 != 1:
        formula = str(n0) + 'x'
    natural_num = 'positive integer'
    if n1 and n0 != n1:
        formula += ' + ' + str(n1)
        n0 = n1
        natural_num = 'natural number'
    print('The least satisfying postive integer is {}.'.format(n0))
    print('All the satifying numbers are in the form: {}, where x is any {}.'.format(formula, natural_num))

##abbreviation
crt = chineseRemainderTheorem

def pH(concentration):
    '''Support pH, pOH and any pK values'''
    return -math.log(concentration, 10)

def titration(volume, molarity1, molarity2, pk, product_basic = 0):
    '''Support weak acid or weak base only'''
    n1 = volume * molarity1
    mol = n1 / (volume + n1 / molarity2)
    h = (mol * 10 ** (pk - 14)) ** 0.5
    if product_basic:
        h = 10 ** (-14) / h
    return pH(h)

def burn_equation(formula):
    '''Please enter a formula like C8H16O2'''
    d = {}
    length = len(formula)
    parentheses = False
    d_ = {}

    def judge(i, ch, dictionary):
        if ch.isalpha():
            if i + 1 == length:
                dictionary[ch] = dictionary.get(ch, 0) + 1
            elif formula[i + 1].isnumeric():
                num = ''
                while i + 1 < length and formula[i + 1].isnumeric():
                    num += formula[i + 1]
                    i += 1
                dictionary[ch] = dictionary.get(ch, 0) + eval(num)
            else:
                dictionary[ch] = dictionary.get(ch, 0) + 1

    for i, ch in enumerate(formula):
        if ch == '(':
            parentheses = True
        elif ch == ')':
            if i + 1<length and formula[i + 1].isnumeric():
                multiple = eval(formula[i + 1])
            for element in d_:
                d[element] = d.get(element, 0) + d_[element] * multiple
            parentheses = False
        if parentheses:
            judge(i, ch, d_)
        else:
            judge(i, ch, d)

    new_d = {}
    new_d[formula] = 1
    new_d['CO2'] = max([d.get('C', 0), d.get('c', 0)])
    new_d['H2O'] = max([d.get('H', 0), d.get('h', 0)])//2
    new_d['O'] = 2*new_d['CO2'] + new_d['H2O']-max([d.get('O', 0), d.get('o', 0)])
    multiple = [1, 2][new_d['O']%2]
    for compound in new_d:
        new_d[compound] *= multiple
    new_d['O2'] = new_d['O']//[2, 1][new_d['O']%2]

    for compound in new_d:
        if new_d[compound] == 1:
            new_d[compound] = ' + ' + compound
        elif new_d[compound] == 0:
            new_d[compound] = ''
        else:
            new_d[compound] = ' + {}{}'.format(new_d[compound], compound)
    reactant = '{}{}→'.format(new_d[formula], new_d['O2'])[1:]
    product = '{}{}'.format(new_d['CO2'], new_d['H2O'])[1:]
    print(reactant + product)

def truth_table(formula, output= 'a', saveAsFile = False):
    '''Please enter the formula in terms of a string.
       Use "=>" or "->" for "imply".
       Please use () for precendence in case of miscalculations.
       Default output table will be of Ts and Fs.
       Change the value of output to "full" to output a complete table,
       to "num" to output a table of 1s and 0s.
       Abbreviation: tt'''
    TF = [True, False]
    keyword = ['and', 'or', 'not', 'True', 'False']

    new = '' ## new formula
    var_lst = []  ## for p, q, r
    compound_dict = {} ## for (p and q): "method['p'] and method['q']"
    col_lst = []  ## for display
    parentheses_stack = []  ## put parentheses' indice
    corresponding_stack = [] ## put parentheses' indice of new_formula
    variable = ''
    compound = ''
    isCompound = False

    formula = formula.strip()
    if formula[-1].isalpha():
        formula += ' '
    for i, ch in enumerate(formula):
        if ch.isalpha():
            variable += ch
            continue
        elif ch == '(':
            parentheses_stack.append(i)
            corresponding_stack.append(len(new) + 1)
        elif ch == ')':
            try:
                start = parentheses_stack.pop() + 1
            except:
                print('The numbers of left and right parentheses do not match!')
                return
            compound = formula[start:i].strip()
            if compound not in compound_dict:
                isCompound = True
        if variable:
            if variable in keyword:
                new += variable
            else:
                if variable not in var_lst:
                    var_lst.append(variable)
                new += f'method[\'{variable}\']'
            variable = ''
        if isCompound:
            compound_dict[compound] = new[corresponding_stack.pop():]
            isCompound = False
        if ch in ['=', '-'] and formula[i + 1] == '>':
            if len(corresponding_stack) == 0:
                left_p = new.find('(')
                if left_p == -1:
                    new = f'not {new} or '
                else:
                    prev = new[left_p:].strip()
                    new = new[:left_p] + f'not {prev} or '
            else:
                idx = corresponding_stack[-1]
                prev = new[idx:].strip()
                new = new[:idx] + f'not {prev} or '
            continue
        elif ch == '>':
            continue
        new += ch

    var_num = len(var_lst)
    col_lst = var_lst + list(compound_dict.keys()) + [formula]
    var_len = {}
    first_line = ''
    for col in col_lst:
        length = (len(col) + 1) if len(col) > 5 else 6
        var_len[col] = length
        first_line += ('{:%d}' % length).format(col)
    print(first_line)

    printout = ''
    file_content = ', '.join(col_lst) + '\n'
    table = []

    ##assign values
    def recursive(method = {}):
        length = len(method)
        if length < var_num:
            for tf in TF:
                method[var_lst[length]] = tf
                if length == var_num - 1:   ## after appending if length == var_num
                    table.append(repr(method))
                recursive()
                del method[var_lst[length]]

    recursive()
    for method in table:
        method = eval(method)
        row = []
        for col in col_lst:
            if col in compound_dict:
                row.append((eval(compound_dict[col]), var_len[col]))
            elif col == formula:
                row.append((eval(new), var_len[col]))
            else:
                row.append((eval(f'method[\'{col}\']'), var_len[col]))
        for tf, length in row:
            printout += ('{:%d}' % length).format(repr(tf))
            file_content += f'{tf}, '
        printout += '\n'
        file_content = file_content[:-1] + '\n'
    printout = printout[:-1]
    file_content = file_content[:-1]
    print(printout)
    if output == 'num':
        file_content = ez.sub(file_content, 'True', '1', 'False', '0')
    elif output != 'full':
##        file_content = ez.sub(file_content, 'and', '∧', 'or', '∨', 'not', '￢')
        file_content = ez.sub(file_content, 'True', 'T', 'False', 'F')

    if saveAsFile:
        try: ez.fwrite(ez.desktop + 'TruthTable.csv', file_content)
        except: print('傻逼关进程啊！')
## Abbreviation: tt
tt = truth_table

def Int(number: str) -> int:
    '''Convert a str to an int if it is a string literal of integer. Otherwise returns 0.'''
    return int(number) if number.isnumeric() else 0

def integer(number: float):
    '''Convert a float to an int if they have the same value.
       For example convert 1.0 to 1.'''
    try:
        int_n = int(number)
        return int_n if number == int_n else number
    except:
        return number

def isNumeric(obj):
    '''Check whether obj is an int or a float.'''
    return isinstance(obj, (int, float))

def numEval(obj):
    '''Convert a string to an number.
       Expressions will not be converted.'''
    if isNumeric(obj) or not isinstance(obj, str):
        return obj
    number = ''
    for i, ch in enumerate(obj):
        number += ch
        if isNumeric(ez.Eval(number)) or \
           i == 0 and ch in ['+', '-'] or \
           ch in ['e']:
            continue
        else:
            return obj
    return integer(eval(number))

def noExpressionEval(obj):
    '''Eval a string without eval expressions.'''
    if isinstance(obj, str):
        return obj
    result = ez.Eval(obj)
    string = str(result)
    if string == obj:
        return result
    if isNumeric(result):
        return obj
    # It's too hard to do. I give up.
    if isinstance(result, list):
        return result
    return result

def get24(a, b = -1, c = -1, d = -1):
    if 1000 <= a<10000 and b == c == d == -1:
        a, b, c, d = map(int, str(a))
    elif not 0 < a < 10 or not 0 < b < 10 or not 0 < c < 10 or not 0 < d < 10:
        print('Numbers should be greater than 0 and less than 10.')
        return
    operators = [' + ', '-', '*', '/']
    for p in permutations(str(a), str(b), str(c), str(d)):
        for o1 in operators:
            for o2 in operators:
                for o3 in operators:
                    calculations = ['{}{}{}{}{}{}{}'.format(p[0], o1, p[1], o2, p[2], o3, p[3]), \
                                    '({}{}{}){}{}{}{}'.format(p[0], o1, p[1], o2, p[2], o3, p[3]), \
                                    '{}{}{}{}({}{}{})'.format(p[0], o1, p[1], o2, p[2], o3, p[3]), \
                                    '({}{}{}{}{}){}{}'.format(p[0], o1, p[1], o2, p[2], o3, p[3]), \
                                    '({}{}{}){}({}{}{})'.format(p[0], o1, p[1], o2, p[2], o3, p[3]), \
                                    '(({}{}{}){}{}){}{}'.format(p[0], o1, p[1], o2, p[2], o3, p[3])]
                    for c in calculations:
                        try:
                            if eval(c) == 24:
                                print(c)
                                break
                        except ZeroDivisionError:
                            pass

def permutation(n, m):
    '''factorial(n)/factorial(n-m)
        n!/(n-m)!'''
    return factorial(n) // factorial(n - m)

##abbreviation
a = permutation

def permutations(*args):
    '''Calls function: itertools.permuations'''
    return list(itertools.permutations(args))
    # methods = []
    # length = len(args)
    # def recursive(p = ()):
    #     if len(p) == length and p not in methods:
    #         methods.append(p)
    #         return
    #     for n in args:
    #         if n not in p:
    #             recursive(p + (n, ))
    # recursive()
    # return methods

def combination(n, m):
    ''' n choose m
        factorial(n)/(factorial(m)*factorial(n-m))
        n!/(m!*(n-m)!)'''
    if m > n:
        return 0
    if m > n // 2:
        return combination(n, n - m)
    num = 1
    for i in range(n - m + 1, n + 1):
        num *= i
    num //= factorial(m)
    return num

##abbreviation
c = combination

def npickm(n, m):
    '''Calls function: itertools.combinations.'''
    return len(list(itertools.combinations(range(n), m)))
    # methods = []
    # def recursive(method = set()):
    #     for item in n:
    #         if item not in method:
    #             recursive(method.union({item}))
    #         if len(method) == m:
    #             if method not in methods:
    #                 methods.append(method)
    #             return

    # recursive()
    # return methods

def fraction(n, m, add = 0):
    '''Reduce n/m.
       If add, reduce n/m + add, which is (n + m * add) / m'''
    add_sign = '+' if add > 0 else ''
    output = f'{n}/{m}{add_sign}{add}'
    n += add * m
    negative = ''
    if n * m < 0:
        negative = '-'
        n = abs(n)
        m = abs(m)
    if type(n) == float or type(m) == float:
        while int(n) != n or int(m) != m:
            n *= 10
            m *= 10
        n = int(n)
        m = int(m)
    new_n = n
    new_m = m
    if n % m == 0:
        new_n = n // m
        new_m = 1
        output += ' = {}{}/1'.format(negative, new_n)
    elif m % n == 0:
        new_n = 1
        new_m = m // n
        output += ' = {}1/{}'.format(negative, new_m)
    else:
        for i in range(2, int(min(n, m) ** 0.5) + 1):
            while new_n % i == 0 and new_m % i == 0:
                new_n //= i
                new_m //= i
        if new_n != n:
            output += ' = {}{}/{}'.format(negative, new_n, new_m)
    quotient = ac(repr(n / m))
    if quotient == int(quotient):
        quotient = int(quotient)
        output += ' = '
    elif set(findPrimeFactors(new_m, False)).issubset({2, 5}):
        output += ' = '
    else:
        output += ' ≈ '
    output += negative + repr(quotient)
    print(output)

##abbreviation
frac = fraction

def factorial(n):
    '''Return n!'''
    product = 1
    for i in range(1, n + 1):
        product *= i
    return product

##abbreviation
fact = factorial

def factorialSkip(n):
    if n in [0, 1]:
        return 1
    return n * factorialSkip(n - 2)

def isPrime(n):
    return type(n) == int and all(n % i for i in range(2, int(n ** 0.5) + 1))

def findPrimeFactors(number, printResult = True, return_dict = False):
    '''Automatically Converts to Non-Negative.
       Abbreviation: fpf'''
    number = abs(number)
    if number in [0, 1] or isPrime(number) :
        return [number]
    i = number
    d = {}
    for k in range(2, number // 2 + 1):
        while i % k == 0:
            d[k] = d.get(k, 0) + 1
            i /= k
    s = ''
    if d != {}:
        for key in d:
            if d[key] == 1:
                s += f'{key}*'
            else:
                s += f'({key}^{d[key]})*'
    if printResult:
        print(f'{number} = {s[:-1]}')
    if return_dict:
        return d
    else:
        return list(d.keys())

##abbreviation
fpf = findPrimeFactors

def findAllFactors(number):
    '''Return all the factors of the number.
       Abbreviation: faf'''
    if number in [0, 1]: return [number]
    smallFactors = [i for i in range(1, int(number ** 0.5) + 1) if number % i == 0]
    bigFactors = [number // i for i in reversed(smallFactors)]
    return smallFactors + bigFactors

##abbreviation
faf = findAllFactors

def findCofactors(*numbers):
    '''Return a list of cofactors.
       Abbreviation: fc'''
    if 0 in numbers: return [0]
    return [i for i in findAllFactors(min(numbers)) if all(num % i == 0 for num in numbers) ]

##abbreviation
fc = findCofactors

def gcd(*numbers):
    '''Greatest Common Divisor.'''
    return reduce(lambda n1, n2: findCofactors(n1, n2)[-1], sorted(numbers))

def lcm(*numbers):
    '''Least Common Multiple.'''
    if 0 in numbers: return 0
    def lcm2(n1, n2):
        if n2 % n1 == 0:
            return n2
        elif gcd(n1, n2) == 1:
            return n1 * n2
        n1_dict = findPrimeFactors(n1, printResult = 0, return_dict = 1)
        n2_dict = findPrimeFactors(n2, printResult = 0, return_dict = 1)
        for factor in n2_dict:
            n1_dict[factor] = max(n2_dict[factor], n1_dict.get(factor, 0))
        return product(factor ** n1_dict[factor] for factor in n1_dict)
    return reduce(lcm2, sorted(numbers))

formLst = ['a', 'l', 's', 'b']

def matrixLaTeX(row, column, entries, determinant = False, newline = False, parentheses = False):
    '''
    Arguments:
    row: int row number
    column: int column number
    entries: string matrix entries separated by space
    determinant: if True print Determinant else Matrix
    newline: new line ending after each row
    paretheses: if True use () False else [].
    Abbreviation: ml.'''
    matrix = advancedSplit(entries)
    expected = row * column
    if len(matrix) != expected:
        print('{} entr{} expected. Found {}.'.format(expected, 'y' if expected == 1 else 'ies', len(matrix)))
        return
    else:
        output = ('\\\\' + ('\n' if newline else '')).join([
            '&'.join([matrix[i * column + j] for j in range(column)])
            for i in range(row)
        ])
        header = '{array}' if parentheses else '{%smatrix}' % ('v' if determinant else 'b')
        begin_header = header + '{%s}' % ('c' * column) if parentheses else header
        end_header = header
        output = f'\\begin{begin_header}{output}\\end{end_header}'
        if parentheses:
            output = f'\\left({output}\\right)'
        return output

##abbreviation
ml = matrixLaTeX

def matrixArray(row, column, entries, newline = False):
    '''Abbreviation: ma'''
    return matrixConvert(form = 'a', matrix = matrixLaTeX(row, column, entries, newline = False))

##abbreviation
ma = matrixArray

def formJudge(m):
    if type(m) != str:
        return False
    if m.startswith('\\begin{bmatrix}') and m.endswith('\\begin{bmatrix}'):
        return 'l'
    elif m.startswith('\\begin{vmatrix}') and m.endswith('\\begin{vmatrix}'):
        return 'dl'
    elif m.find(' ') > 0:
        for i in m.split():
            if not i.isalnum():
                return False
        return 's'
    elif type(eval(m)) == list:
        for item in eval(m):
            if type(item) != list:
                return False
        return 'a'
    elif m.find(' ') == -1:
        if m.isalnum():
            return 's'
        return False
    elif m.count('|')%2 == 0 and m.count('\n') == m.count('|')/2-1:
        return 'b'
    else:
        return False

def matrixConvert(form, matrix):
    judgeForm = formJudge(matrix)
    if form.lower() not in formLst or judgeForm == False:
        raise Exception('Unsupport Matrix Form')
    if judgeForm == form:
        return matrix
    newMat = ''
    if judgeForm == 'a':
        if form == 'l':
            matrix = ez.substitute(matrix, '[[', '\\begin{bmatrix}', ']]', '\\end{bmatrix}', '], [', '\\\\')
            for ch in matrix:
                if ch == ', ':
                    ch = '&'
                newMat += ch
        elif form == 'b':
            matrix = ez.substitute(matrix, '[[', '|', ']]', '|', '], [', '|\n|', ', ', ' ')
            newMat = formatBMat(matrix)
        else:
            matrix = ez.substitute(matrix, '[[', '', ']]', '', '], [', ' ')
            for ch in matrix:
                if ch == ', ':
                    ch = ' '
                newMat += ch
    elif judgeForm == 'l' or 'dl':
        if judgeForm == 'dl':
            matrix = matrix.replace('vmatrix', 'bmatrix')
        if form == 'a':
            matrix = matrix.replace('\\begin{bmatrix}', '[[')
            matrix = matrix.replace('\\end{bmatrix}', ']]')
            for i, ch in enumerate(matrix):
                if ch == '&':
                    ch = ', '
                elif ch == '\\' and matrix[i + 1] == '\\':
                    ch = '], ['
                elif ch == '\\' and matrix[i-1] == '\\':
                    ch = ''
                newMat += ch
        elif form == 'b':
            matrix = ez.substitute(matrix, '\\begin{bmatrix}', '|', '\\end{bmatrix}', '|', '\\\\', '|\n|', '&', ' ')
            newMat = formatBMat(matrix)
        else:
            matrix = matrix[18:-15]
            for ch in matrix:
                if not ch.isalnum():
                    ch = ' '
                newMat += ch
            newMat = newMat.replace('  ', ' ')
    elif judgeForm == 'b':
        if form == 'a':
            matrix = matrix[1:] + '[['
            matrix = matrix[:-1] + ']]'
            for i, ch in enumerate(matrix):
                if ch == '|' and matrix[i + 1] == '\n':
                    ch = ']'
                elif ch == '\n':
                    ch = ', '
                elif ch == '|' and matrix[i-1] == '\n':
                    ch = '['
                elif ch == ' ':
                    ch = ', '
                newMat += ch
        if form == 'l':
            matrix = matrix[1:] + '\\begin{bmatrix}'
            matrix = matrix[:-1] + '\\end{bmatrix}'
            for ch in matrix:
                if ch == ' ':
                    ch = '&'
                elif ch == '|':
                    ch = '\\'
                elif ch == '\n':
                    ch = ''
                newMat += ch
        else:
            matrix = matrix[1:-1]
            for ch in matrix:
                if not ch.isalnum():
                    ch = ' '
                newMat += ch
            newMat = newMat.replace('  ', ' ')
    return newMat

##abbreviation
mc = matrixConvert

def formatBMat(matrix, foldLine = False):
    if foldLine:
        rm = matrix.replace('|', ' ')
        l = rm.split()
        L = []
        longest = len(l[0])
        newMat = ''
        for item in l:
            if len(item) > longest:
                longest = len(item)
        for item in l:
            L.append(('{:' + str(longest) + '}').format(item))
        r = matrix.count('\n') + 1
        c = int(len(l) / r)
        for i in range(r):
            if i == 0:
                newMat += '┌'
            elif i == r - 1:
                newMat += '└'
            else:
                newMat += ' |'
            for j in range(c):
                newMat += L[i * r + j]
                if j != c - 1:
                    newMat += ' '
            if i == 0:
                newMat += '┐\n'
            elif i == r-1:
                newMat += '┘'
            else:
                newMat += '|\n'
        return newMat
    else:
        rowmatrix = matrix.replace('|', ' ')
        itemlist = rowmatrix.split()
        longest = len(itemlist[0])
        newMat = ''
        for item in itemlist:
            if len(item) > longest:
                longest = len(item)
        L = [('{:' + str(longest) + '}').format(item) for item in itemlist]
        r = matrix.count('\n') + 1
        c = int(len(itemlist) / r)
        for i in range(r):
            newMat += '|'
            for j in range(c):
                newMat += L[i * c + j]
                if j != c-1:
                    newMat += ' '
            newMat += '|\n'
        return newMat[:-1]

def matrixMultiplication():
    rightMat = input('Please type in your right matrix in any form except string form.\n>>>')
    rightPower = 1
    mp = []
    if rightMat.count('^') == 1:
        mp = rightMat.split('^')
        rightPower = eval(mp[1])
    elif rightMat.count('**') == 1:
        mp = rightMat.split('**')
        rightPower = eval(mp[1])
    else:
        mp = [rightMat]
    if type(rightPower) != int:
        print('The exponent must be integers! Please type again!\n')
        matrixMultiplication()
        return
    rightMat = mp[0]
    if formJudge(rightMat) == False:
        print('Your right matrix form is not supported! Please type again!\n')
        matrixMultiplication()
        return
    elif formJudge(rightMat) == 's':
        print('String form is not supported currently. Please type again!\n')
        matrixMultiplication()
        return
    rightMat = eval(matrixConvert('a', rightMat))
    ml = len(rightMat)
    nl = len(rightMat[0])
    if rightPower != 1:
        if ml == nl:
            for power in range(rightPower):
                rightMat = [[sum(rightMat[i][k] * rightMat[k][j] for k in range(ml)) for j in range(ml)] for i in range(ml)]
        else:
            print('This matrix can\'t be powered! Please type again!\n')
            matrixMultiplication()
            return
    while True:
        leftMat = input('Please type in your left matrix in any form besides string form, no input will stop this function.\n>>> ')
        leftPower = 1
        if leftMat == '':
            break
        elif leftMat.count('^') == 1:
            leftPower = int(leftMat.split('^')[1])
            leftMat = leftMat.split('^')[0]
        elif leftMat.count('**') == 1:
            leftPower = int(leftMat.split('**')[1])
            leftMat = leftMat.split('**')[0]
        elif leftPower != 1:
            print('This matrix can\'t be powered! Please type again!\n')
            continue
        if formJudge(leftMat) == False:
            print('Your left matrix form is not supported! Please type again!\n')
            continue
        leftMat = eval(matrixConvert(form = 'a', matrix = leftMat))
        mr = len(leftMat)
        nr = len(leftMat[0])
        if nl != mr:
            print('We can\'t do multiplication with these 2 matrices! Please type again!\n')
            continue
        for power in range(leftPower):
            lst = []
            for i in range(ml):
                l = []
                for j in range(nr):
                    item = 0
                    for k in range(nl):
                        item += leftMat[i][k]*rightMat[k][j]
                    l.append(item)
                lst.append(l)
            rightMat = lst
    if input('Do you want to beautify this matrix? Type \'y\' representing \'yes\', other input will be regarded as \'no\'.\n>>> ').lower() == ( 'y' or 'yes' ):
        print(matrixConvert(form = 'b', matrix = str(rightMat).replace(' ', '')))
    else:
        print('The result matrix is:\n{}'.format(str(rightMat).replace(' ', '')))

##abbreviation
mtp = matrixMultiplication

def determinantCalculation(det):
    '''inputDet can be in LaTeX form or in Array form'''
    assert formJudge(det) in ['dl', 'a'], 'Please type in the correct form!\n'
    def compute(determinant):
        if len(determinant) == 1:
            determinantValue = determinant[0][0]
        else:
            determinantValue = 0
            for i in range(len(determinant)):
                n = [[row[j] for j in range(len(determinant)) if j != i] for row in determinant[1:]]
                if i % 2 == 0:
                    determinantValue += determinant[0][i] * compute(n)
                else:
                    determinantValue -= determinant[0][i] * compute(n)
        return determinantValue
    return compute(eval(matrixConvert('a', det)))

##abbreviation
dc = determinantCalculation

def boldedRLaTeX(n = 0):
    common = '\\mathbb{R}'
    if n:
        return common + f'{n}'
    else:
        n = input('How many dimensions would you like?\n>>> ')
        print(common + f'{n}' if n else '')

##abbreviation
br = boldedRLaTeX

def vectorLaTeX(entries, overRightArrow = True):
    '''entries needs to be a string separted by a comma.
        if overRightArrow, will use \\overrightarrow instead of \\vec'''
    return '\\overrightarrow{%s}' % entries if overRightArrow else '\\vec{%s}' % entries

##abbreviation
vl = vectorLaTeX

def advancedSplit(s):
    lst = []
    d = {'\'':0, '\"':0, '(':0, ')':0, '[':0, ']':0, '{':0, '}':0}
    item = ''
    for i in range(len(s)):
        ch = s[i]
        if ch in d:
            d[ch] += 1
        if ch in [' ', ', '] and s[i - 1] not in [' ', ','] and d['\''] % 2 == 0 and d['\"'] % 2 == 0 and d['('] == d[')'] and d['['] == d[']'] and d['{'] == d['}']:
           lst.append(item)
           item = ''
           ch = ''
        item += ch
        if i == len(s) - 1 and item:
            lst.append(item)
    return lst
