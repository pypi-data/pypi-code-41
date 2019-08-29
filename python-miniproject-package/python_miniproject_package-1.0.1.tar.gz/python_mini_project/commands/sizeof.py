import os


def run(path):
    try:
        ans = os.path.getsize(path)
    except FileNotFoundError:
        print("File doesnot exist")
    else:
        print(ans)

    