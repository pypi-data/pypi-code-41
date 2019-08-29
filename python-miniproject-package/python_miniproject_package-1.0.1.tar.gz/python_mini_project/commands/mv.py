import os


def run(src, dest):
    try:
        if os.path.exists(dest):
            os.unlink(dest)
        os.rename(src, dest)
    except Exception as e:
        print(e)
        