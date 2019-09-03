import shlex, subprocess
import time

def execute_shell_command(command, preserve_output=False):
    lines = []
    cmd = "sh -c '{}'".format(command)
    p = subprocess.Popen(shlex.split(cmd),
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    while True:
        retval = p.poll()
        if retval is not None:
            break
        output = p.stdout.readline()
        if output:
            line = output.decode('utf-8').strip()
            print(line)
            if preserve_output:
                lines.append(line)
    return retval, lines
