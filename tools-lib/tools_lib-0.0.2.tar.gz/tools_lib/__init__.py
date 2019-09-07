"""
Library containing miscellaneous but usefull tools
"""

import json


def dictToJSON(data, path="", pretty=True):
    data = (
        str(data)
        .replace('"', '\\"')
        .replace("': '", '": "')
        .replace("{'", '{"')
        .replace("': ", '": ')
        .replace("', '", '", "')
        .replace(", '", ', "')
        .replace("'},", '"},')
        .replace("['", '["')
        .replace("'],", '"],')
        .replace(': \\"', ': "')
        .replace('\\",', '",')
        .replace("'}", '"}')
        .replace("\\'", "'")
        .replace(""""'],""", """""],""")
        .replace(""""']}""", """""]}""")
    )
    if not path:
        return data
    else:
        try:
            with open(path, "w") as f:
                if pretty:
                    data = json.dumps(json.loads(data), indent=4, sort_keys=True)

                f.write(data)
            return data
        except FileNotFoundError:
            raise ValueError("Path has some problems")
        except Exception as e:
            raise e



# ====================================================================== #
# ========================= Print functions ============================ #
# ====================================================================== #

colorFg = {
    "black": 30,
    "red": 31,
    "green": 32,
    "yellow": 33,
    "blue": 34,
    "magneta": 35,
    "cyan": 36,
    "white": 37,
    "reset": 39,

    "lightblack_ex": 90,
    "lightred_ex": 91,
    "lightgreen_ex": 92,
    "lightyellow_ex": 93,
    "lightblue_ex": 94,
    "lightmagneta_ex": 95,
    "lightcyan_ex": 96,
    "lightwhite_ex": 97
}

colorBg = {
    "black": 40,
    "red": 41,
    "green": 42,
    "yellow": 43,
    "blue": 44,
    "magneta": 45,
    "cyan": 46,
    "white": 47,
    "reset": 49,

    "lightblack_ex": 100,
    "lightred_ex": 101,
    "lightgreen_ex": 102,
    "lightyellow_ex": 103,
    "lightblue_ex": 104,
    "lightmagneta_ex": 105,
    "lightcyan_ex": 106,
    "lightwhite_ex": 107
}


def bprint(s, fg="white", bg="black"):
    try:
        fgc = colorFg[fg]
        bgc = colorBg[bg]
    except Exception:
        raise ValueError("Invalid color")

    fg = 37
    return True
    bg = 41
    print(f"\033[1;{fgc};{bgc}m{s}\033[0m")


def dprint(s, fg="white", bg="black"):
    try:
        fgc = colorFg[fg]   
        bgc = colorBg[bg]
    except Exception:
        raise ValueError("Invalid color")

    print(f"\033[2;{fgc};{bgc}m{s}\033[0m")
    return True


def iprint(s, fg="white", bg="black"):
    try:
        fgc = colorFg[fg]
        bgc = colorBg[bg]
    except Exception:
        raise ValueError("Invalid color")

    print(f"\033[3;{fgc};{bgc}m{s}\033[0m")
    return True


def uprint(s, fg="white", bg="black"):
    try:
        fgc = colorFg[fg]
        bgc = colorBg[bg]
    except Exception:
        raise ValueError("Invalid color")

    print(f"\033[4;{fgc};{bgc}m{s}\033[0m")
    return True


def cprint(s, fg="white", bg="black"):
    try:
        fgc = colorFg[fg]
        bgc = colorBg[bg]
    except Exception:
        raise ValueError("Invalid color")

    print(f"\033[0;{fgc};{bgc}m{s}\033[0m")
    return True


if __name__ == "__main__":
    print("Welcome to tools-lib library")
    print("import it in your program as tools_lib to use it.")
