import sys
from subprocess import Popen, PIPE
import json
from shutil import which

class AzureError(Exception):
    pass

def azure_proxy(command, *args, **kwargs):
    if "replace_underscore" in kwargs.keys():
        replace_underscore = kwargs["replace_underscore"]
        del kwargs["replace_underscore"]
    else:
        replace_underscore = True
    
    if "keep_stdout" in kwargs.keys():
        keep_stdout = kwargs["keep_stdout"]
        del kwargs["keep_stdout"]
    else:
        keep_stdout = False

    flags = [
        "--{key}=\"{value}\"".format(
            key=(key.replace("_", "-") if replace_underscore else key),
            value=val) for key, val in kwargs.items()
        ]
    f = Popen(" ".join([
        "az",
        command,
        *["\"{}\"".format(arg) for arg in args],
        *flags,
        "--output json"
    ]),
    stdout=PIPE if not keep_stdout else sys.stdout,
    stderr=PIPE if not keep_stdout else sys.stderr,
    stdin=None if not keep_stdout else sys.stdin,
    shell=True
    )
    if keep_stdout:
        if f.wait()==0:
            return True
        else:
            return False
    out, err = f.communicate()
    if f.returncode == 0:
        return json.loads(out.decode("utf-8"))
    else:
        raise AzureError(err.decode("utf-8"))

class Azure:
    def __init__(self):
        pass
    def __getattribute__(self, attr):
        attributes = attr.split("_")
        if attributes[-1] == "":
            attributes.pop(-1)
        def run_azure(*args, **kwargs):
            return azure_proxy(*attributes, *args, **kwargs)
        return run_azure

if which("az") == None:
    raise FileNotFoundError("\'az\' command was not found in your environment. Ensure it is installed and set up properly.")

if __name__ == '__main__':
    az = Azure()
    print(az.account_show())

__all__ = [Azure, AzureError]
