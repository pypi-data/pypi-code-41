def df(x, y):
    f_xn = y[-1]
    xn = x[-1]

    DF = []

    for i in range(len(y)-2, -1, -1):
        f_xn_1 = y[i]
        xn_1 = x[i]

        df = (f_xn-f_xn_1) / (xn - xn_1)
        # print('i: ', i, ' (', f_xn, '-', f_xn_1, ') / (', xn - xn_1, '), df = ', df, sep='')
        # print('i: ', i, ', df = ', df, sep='')
        # print("dx", xn-xn_1)

        DF.append(df)

        f_xn = f_xn_1
        xn = xn_1

    DF = DF[::-1]


def df2(x, y):
    f_xn = y[-1]
    xn = x[-1]

    DF = []
    t = []

    for i in range(1, len(y)-1):
        df_ = (y[i+1]-y[i-1]) / (x[i+1] - x[i-1])
        DF.append(df_)
        t.append(x[i])
        # f_xn_1 = y[i]
        # xn_1 = x[i]

        # print('i: ', i, ' (', f_xn, '-', f_xn_1, ') / (', xn - xn_1, '), df = ', df, sep='')
        # print('i: ', i, ', df = ', df, sep='')
        # print("dx", xn-xn_1)

        # f_xn = f_xn_1
        # xn = xn_1

    return DF, t
    # DF = DF[::-1]
    # print(DF[0], DF[-1])
    # exit(0)
    # s = 0

    # for i in range(1, len(DF)):
    #     s += DF[i] * (x[1]-x[0])
    # print(s)
    # print(sum(DF))

    # return DF
