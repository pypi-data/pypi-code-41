from os import SEEK_END


def tail(stream: "file", n: int = 10, block_size: int = 1024):
    """Output the last part of the file.

    This function behaves like the Unix `tail` command, but not all options have been
    implemented.

    Args:
        stream: File stream.

        n: Number of lines to output.

        block_size: Number of bytes to read at once. The optimum number depends on the
            file size and the average line length.

    Return:
        str: The last part of the file.
    """
    if not block_size > 0:
        raise ValueError("block_size must be a positive integer")
    if n == 0:
        return b""
    elif not n > 0:
        raise ValueError("n must be a positive integer")

    lines = []
    eol = b"\n"
    suffix = b""
    stream.seek(0, SEEK_END)
    stream_length = stream.tell()
    seek_offset = 0

    # From the end, move the offset by block size until the entire stream is covered
    while -seek_offset < stream_length:
        seek_offset -= block_size

        if -seek_offset > stream_length:
            # Adjust block size to avoid going past the first byte of the file
            block_size -= -seek_offset - stream_length
            if block_size == 0:
                # This happens when the offset is at the first byte already
                break
            # Set the offset to the first byte
            seek_offset = -stream_length

        stream.seek(seek_offset, SEEK_END)
        buf = stream.read(block_size)

        while 1:
            pos = buf.rfind(eol)
            if pos != -1:
                # EOL found
                suffix = buf[pos + 1 :] + suffix
                buf = buf[:pos]

                if seek_offset + pos + 1 == 0 and suffix == b"":
                    # If this is an EOL at the end of the file, `tail` keeps it so we do
                    # so as well
                    suffix = eol
                else:
                    lines.append(suffix)
                    suffix = b""
                    n -= 1
                    if n == 0:
                        return eol.join(lines[::-1])
            else:
                suffix = buf + suffix
                break

    # One-line file
    lines.append(suffix)
    return eol.join(lines[::-1])
