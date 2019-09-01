from subprocess import Popen, PIPE
import json
from shutil import which

class GCloudError(Exception):
    pass

def gcloud_proxy(command, *args, **kwargs):
    if "replace_underscore" in kwargs.keys():
        replace_underscore = kwargs["replace_underscore"]
        del kwargs["replace_underscore"]
    else:
        replace_underscore = True
    flags = [
        "--{key}=\"{value}\"".format(
            key=(key.replace("_", "-") if replace_underscore else key),
            value=val) for key, val in kwargs.items()
        ]
    f = Popen(" ".join([
        "gcloud",
        command,
        *["\"{}\"".format(arg) for arg in args],
        *flags,
        "--format=json"
    ]),
    stdout=PIPE,
    stderr=PIPE,
    shell=True
    )
    out, err = f.communicate()
    if f.returncode == 0:
        return json.loads(out.decode("utf-8"))
    else:
        raise GCloudError(err.decode("utf-8"))

class GCloud:
    def __init__(self):
        pass
    def __getattribute__(self, attr):
        attributes = attr.split("_")
        if attributes[-1] == "":
            attributes.pop(-1)
        def run_gcloud(*args, **kwargs):
            return gcloud_proxy(*attributes, *args, **kwargs)
        return run_gcloud

if which("gcloud") == None:
    raise FileNotFoundError("\'gcloud\' command was not found in your environment. Ensure it is installed and set up properly.")

if __name__ == '__main__':
    gc = GCloud()
    print(gc.projects_list())

__all__ = [GCloud, GCloudError]
