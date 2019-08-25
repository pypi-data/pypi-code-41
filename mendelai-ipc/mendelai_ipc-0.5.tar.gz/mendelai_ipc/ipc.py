import sys


MSG_SYMBOL = "#_#_MSG_#_#"
START_MSG_SYMBOL = "#_#_SMSG_#_#"
END_MSG_SYMBOL = "#_#_EMSG_#_#"
NEW_LINE_SYMBOL = "#_#_NL_#_#"
MAX_MSG_CHAR=1000

class IPC(object):
    """
    A class used for inter process communication over stdin/stdout with
    defined count of input/output messages. The class assumes that the other process
    relies on some agreed symbols to define msg start and end as messages are assumed to
    be comming in chunks if it is larger than certain threshold.
    """
    def __init__(self, input_count=1, output_count=1):
        """
        :param input_count: define the desired input messages count
        :param output_count: define the desired output messages count
        """
        self.input_count = input_count
        self.output_count = output_count

    def get_input(self):
        """
        Waits to read desired input from stdin and handles concating message chunks.
        :return: a string or array of strings
        """
        messages = []
        current_msg = ""
        inside_msg = False
        while len(messages) < self.input_count:
            line = sys.stdin.readline().rstrip("\r\n")
            if line is None or len(line) == 0:
                return None
            if line.startswith(START_MSG_SYMBOL):
                inside_msg = True
                line = line[len(START_MSG_SYMBOL):]
            elif line.startswith(MSG_SYMBOL):
                line = line[len(MSG_SYMBOL):]
            elif line.startswith(END_MSG_SYMBOL):
                line = line[len(END_MSG_SYMBOL):]
                inside_msg = False
            else:
                continue

            current_msg += line
            if not inside_msg:
                messages.append(current_msg.replace(NEW_LINE_SYMBOL, "\n"))
                current_msg = ""
        if len(messages) == 1:
            return messages[0]
        return messages

    def write_output(self, output):
        """
        Writes specified output to stdout and handles splitting each message if greater than certain threshold.
        :param output: a string or array of strings
        """
        outputs = []
        if isinstance(output, str):
            outputs.append(output)
        else:
            outputs = output

        assert len(outputs) == self.output_count

        for o in outputs:
            o = o.replace("\n", NEW_LINE_SYMBOL)
            parts = [o[i:i+MAX_MSG_CHAR] for i in range(0, len(o), MAX_MSG_CHAR)]
            if len(parts) == 1:
                print(MSG_SYMBOL + parts[0], flush=True)
            elif len(parts) == 0:
                print(MSG_SYMBOL, flush=True)
            else:
                for i in range(len(parts)):
                    symbol = MSG_SYMBOL
                    if i == 0:
                        symbol = START_MSG_SYMBOL
                    elif i == len(parts) - 1:
                        symbol = END_MSG_SYMBOL
                    print(symbol + parts[i], flush=True)
