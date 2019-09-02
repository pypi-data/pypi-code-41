# def wc_str(wc, precision=3):
#     if wc >= 1e9:
#         wc_str = str(round(wc / 1e9, precision)) + " GHz"
#     elif wc >= 1e6:
#         wc_str = str(round(wc / 1e6, precision)) + " MHz"
#     elif wc >= 1e3:
#         wc_str = str(round(wc / 1e3, precision)) + " KHz"
#     else:
#         wc_str = str(round(wc, precision)) + " Hz"

#     return wc_str


# def wc_str_v(wc, precision=3):
#     if wc >= 1e9:
#         wc_str = str(round(wc / 1e9, precision))
#     elif wc >= 1e6:
#         wc_str = str(round(wc / 1e6, precision))
#     elif wc >= 1e3:
#         wc_str = str(round(wc / 1e3, precision))
#     else:
#         wc_str = str(round(wc, precision))

#     return wc_str


# def wa_str(wa):
#     if wa >= 1e9:
#         wa_str = str(round(wa / 1e9, 3)) + " GHz"
#     elif wa >= 1e6:
#         wa_str = str(round(wa / 1e6, 3)) + " MHz"
#     elif wa >= 1e3:
#         wa_str = str(round(wa / 1e3, 3)) + " KHz"
#     else:
#         wa_str = str(round(wa, 3)) + " Hz"

#     return wa_str


# def g_str(g):
#     if g >= 1e9:
#         g_str = str(round(g / 1e9, 3)) + " GHz"
#     elif g >= 1e6:
#         g_str = str(round(g / 1e6, 3)) + " MHz"
#     elif g >= 1e3:
#         g_str = str(round(g / 1e3, 3)) + " KHz"
#     else:
#         g_str = str(round(g, 3)) + " Hz"
#     return g_str


# def T_str(T):
#     if T >= 1e-3:
#         T_str = str(round(T * 1e3, 3)) + " ms"
#     elif T >= 1e-6:
#         T_str = str(round(T * 1e6, 3)) + " mks"
#     elif T >= 1e-9:
#         T_str = str(round(T * 1e9, 3)) + " ns"
#     else:
#         T_str = str(round(T, 3)) + " s"
#     return T_str


def T_str_v(T):
    if T >= 1e-3:
        T_str = round(T * 1e3, 3)
    elif T >= 1e-6:
        T_str = round(T * 1e6, 3)
    elif T >= 1e-9:
        T_str = round(T * 1e9, 3)
    else:
        T_str = round(T, 3)
    return T_str


def T_str_mark(T):
    if T >= 1e-3:
        T_str = " ms"
    elif T >= 1e-6:
        T_str = " mks"
    elif T >= 1e-9:
        T_str = " ns"
    else:
        T_str = " s"

    return T_str
