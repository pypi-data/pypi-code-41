import math


def solve(*coefficients):
    sp = []
    for elem in coefficients:
        sp.append(elem)
    if len(sp) == 0 or len(sp) > 3:
        return None
    elif len(sp) == 1:
        if sp[0] == 0:
            result = ['all']
            return result
        else:
            result = []
            return result
    elif len(sp) == 2:
        b = sp[0]
        c = sp[1]
        if c == 0:
            result = [0.0]
            return result
        result = [(c / b) * -1]
        return result
    b = sp[1]
    a = sp[0]
    c = sp[2]
    D_1 = b ** 2 - 4 * a * c
    if D_1 < 0:
        return []
    D = math.sqrt(D_1)
    result_1 = (-b + D) / (2 * a)
    result_2 = (-b - D) / (2 * a)
    if result_1 == result_2:
        return [result_1]
    return [result_1, result_2]



