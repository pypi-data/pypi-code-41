import colorama


def marker_on(s, marked, marker):
    if not marked:
        s += marker
        marked = True
    return s, marked


def marker_off(s, marked):
    if marked:
        s += colorama.Style.RESET_ALL
        marked = False
    return s, marked


def chardiff(a, b, marker=colorama.Style.BRIGHT):
    s = ""
    marked = False

    for i in range(len(a)):
        if i > len(b) - 1:
            s, marked = marker_on(s, marked, marker)
        else:
            if a[i] == b[i]:
                s, marked = marker_off(s, marked)
            else:
                s, marked = marker_on(s, marked, marker)
        s += a[i]
    s, marked = marker_off(s, marked)
    return s


def get_color(color):
    color = color.upper()
    if not hasattr(colorama.Fore, color):
        raise RuntimeError("Chosen color does not exist in pallet.")
    return getattr(colorama.Fore, color)
