def write_line(line, filename, mode):
    with open(filename, mode) as f:
        f.write(line)
