"""
Library containing miscellaneous but usefull tools
"""


def welcome():
    print("Welcome to the library")


def dictToJSON(data, path=""):
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
    )
    if not path:
        return data
    else:
        try:
            with open(path, "w") as f:
                f.write(data)
            return data
        except Exception:
            raise ValueError("Path has some problems")


if __name__ == "__main__":
    print("Welcome to tools-lib library")
    print("import it in your program as tools_lib to use it.")
