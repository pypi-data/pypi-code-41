from termcolor import colored


def line(
    info: str = None,
    width: int = 80,
    char: str = "-",
    color: str = "magenta",
    align: int = 1,
    margin: tuple = (1, 1),
    *args,
):
    if info is None:
        return colored(char * width, color, *args)

    if align < 0:
        align = (
            width + align - len(info) - sum(margin)
        ) % width
    else:
        align = align % width

    return colored(
        "".join(
            [
                char * align,
                " " * margin[0],
                info,
                " " * margin[1],
                char
                * (
                    width - sum(margin) - len(info) - align
                ),
            ]
        ),
        color,
        *args,
    )
