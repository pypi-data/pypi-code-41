def head(stream: "file", n: int = 10) -> bytes:
    """Output the first part of the file.

    This function behaves like the Unix `head` command, but not all options have been
    implemented.

    Args:
        stream: File stream.

        n: Number of lines to output

    Return:
        The first part of the file.
    """
    lines = []
    while n > 0:
        buf = stream.readline()
        if buf == b"":
            break
        lines.append(buf)
        n -= 1

    return b"".join(lines)
