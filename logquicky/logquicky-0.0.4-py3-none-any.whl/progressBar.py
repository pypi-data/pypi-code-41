import logging
import sys


class ProgressBar:

    """ Component to easily print a progress bar in a shell. """

    def __init__(self, steps, prefix=None, suffix=None, fill="#", length=30, wait="⏳", complete="🎉"):
        self.prefix: str = prefix if prefix else ""
        self.suffix: str = suffix if suffix else ""
        self.fill: str = fill
        self.length: int = length
        self.steps = steps

        # emoji to be displayed when finished.
        self.complete = complete
        self.wait = wait

        self.log = logging.getLogger("pb")
        self.log.setLevel("INFO")

        # Setup formatter
        formatter = logging.Formatter("%(message)s")

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.terminator = ""
        stream_handler.setFormatter(formatter)

        self.log.addHandler(stream_handler)

    def update(self, block: int) -> int:
        """	Call in a loop to create terminal progress bar """
        percentage = round((((block + 1) / self.steps) * 100), 1)

        filled_length = int(self.length * block // self.steps)
        bar = self.fill * filled_length + " " * (self.length - filled_length)
        message = f"{self.prefix} {block} of {self.steps} {bar}  {percentage}% {self.suffix} {self.wait}  \r"

        if block == self.steps - 1:
            bar = self.fill * self.length
            message = f"{self.prefix} {block+1} of {self.steps} {bar}  100% {self.suffix} {self.complete}  \n"

        self.log.info(message)
        return percentage

