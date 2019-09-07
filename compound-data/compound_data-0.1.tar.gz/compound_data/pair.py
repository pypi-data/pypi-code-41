def cons(x, y):
    def make_pair(element):
        if element == 'car':
            return x
        elif element == 'cdr':
            return y
        else:
            return None

    return make_pair


def car(pair):
    return pair('car')


def cdr(pair):
    return pair('cdr')
