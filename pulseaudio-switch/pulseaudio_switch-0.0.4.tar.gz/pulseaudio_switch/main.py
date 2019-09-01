import argparse
import re
from subprocess import Popen, PIPE


def run(arg):
    p1 = Popen(["pacmd", "set-default-sink", arg.output_sink], stdout=PIPE)
    p1.communicate()
    p1 = Popen(["pacmd", "list-sink-inputs"], stdout=PIPE)
    out, err = p1.communicate()
    out = out.decode("utf-8")
    for line in out.split("\n"):
        if "index:" in line:
            m = re.match(r".*index:[ \t]+([0-9]+)$", line)
            print("Found index %s. Change to output sink: %s" % (m.group(1), arg.output_sink))
            p1 = Popen(["pacmd", "move-sink-input", m.group(1), arg.output_sink])
            p1.communicate()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--output_sink",
        help="Specify the sink index number. The default sink and "
        "active streams will be set to the given sink index number."
    )
    arg = ap.parse_args()
    run(arg)
