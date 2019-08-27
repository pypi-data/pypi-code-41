def narcissistic(i):
    s = str(i)
    n = len(s)
    sum = 0
    for j in range(0, n):
        sum = sum + int(s[j]) ** n
    if i == sum:
        print(i, 'is a narcissistic number')
    else:
        print(i, 'is not a narcissistic number')
