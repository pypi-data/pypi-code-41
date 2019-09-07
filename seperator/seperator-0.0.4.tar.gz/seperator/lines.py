from colorama import Fore, Back, Style
import shutil


def line(
    info: str = None,
    width: int = 80,
    char: str = "-",
    color: str = "magenta",
    align: int = 1,
    margin: tuple = (1, 1),
    *args,
):

    columns, _ = shutil.get_terminal_size()
    sup_limit = columns
    if width == 0 or width > columns:
        width = sup_limit
    if align < 0:
        info = "" if info is None else info
        align = (
            width + align - len(info) - sum(margin)
        ) % width
    else:
        align = align % width

    if info is None:
        color_code = getattr(Fore, color.upper())
        return str(
            color_code + str(char) * width + Fore.RESET
        )
    sub_limit = len(info) + sum(margin) + align
    if width < sub_limit:
        width = sub_limit
    else:
        color_code = getattr(Fore, color.upper())
        return "".join(
            [
                color_code,
                char * align,
                " " * margin[0],
                info,
                " " * margin[1],
                char
                * (
                    width - sum(margin) - len(info) - align
                ),
                Fore.RESET,
            ]
        )
