

def get_fibonacci_numbers(n):
    a = 0
    b = 1

    result = []
    i = 0
    while i<n:
        
        result.append(a)
        temp = b

        b = a + b
        a = temp
        i += 1

    return result




