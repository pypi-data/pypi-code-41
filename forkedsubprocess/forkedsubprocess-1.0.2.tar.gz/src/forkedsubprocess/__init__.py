"""Forked subprocesses support for Python."""

import subprocess
import threading
from typing import IO, Any, Callable, Dict, List, Optional

__version__ = '1.0.2'

# Define our callback types
InputCallback = Callable[[], str]
OutputCallback = Callable[[str], None]

# Only export these 3 items
__all__ = ['ForkedSubprocess', 'ForkedSubprocessNotRunningException', 'InputCallback', 'OutputCallback']


class ForkedSubprocessNotRunningException(RuntimeError):
    """Exception raised when a method is called on a subprocess which is supposed to be running."""


class ForkedSubprocessIOBase:
    """The ForkedSubprocessIOBase class handles the basics of readers and writers."""

    # Pipe to read from
    _pipe: IO[Any]
    # Thread
    _thread: threading.Thread

    def __init__(self, pipe: IO[Any]):
        """Initialize our class.

        The lines_lists argument is a list of lists to add lines to.
        This is so we can add to stdouterr and stdout/stderr at the same time.
        """

        # Setup pipe we're going to be using
        self._pipe = pipe

        # Setup thread
        self._thread = threading.Thread(target=self._thread_target)

    def start(self):
        """Start the thread."""
        self._thread.start()

    def wait(self):
        """Wait until the thread exits."""
        self._thread.join()

    def _thread_target(self):
        """Responsible for reading data."""
        raise RuntimeError('The method "_thread_target" should of been overridden')


class ForkedSubprocessReader(ForkedSubprocessIOBase):
    """The ForkedSubprocessReader class handles reading data from a stream."""

    # Lines we've collected
    _lines_lists: List[List[str]]

    # Output to terminal?
    _output: bool

    # Output callback to use
    _output_callback: Optional[OutputCallback]

    def __init__(self, pipe: IO[Any], lines_lists: List[List[str]], **kwargs):
        """Initialize our class.

        The lines_lists argument is a list of lists to add lines to.
        This is so we can add to stdouterr and stdout/stderr at the same time.
        """

        # Initialize base class
        super().__init__(pipe)

        # Setup lists we're going to output to
        self._lines_lists = lines_lists

        # Are we going to output to the terminal?
        self._output = kwargs.get('output', False)

        # Setup the output callback if we have one
        self._output_callback = kwargs.get('output_callback', None)

    def _thread_target(self):
        """Responsible for reading data."""

        # Loop with raw lines received
        for raw_line in iter(self._pipe.readline, ''):
            # Strip off newline
            line = raw_line.rstrip('\n')
            # Add to all the lines lists
            for lines in self._lines_lists:
                lines.append(line)
                # Are we outputting to terminal aswell?
                if self._output:
                    print(f'{line}\n')
            # Are we going to send the line to the output callback
            if self._output_callback:
                self._output_callback(line)


class ForkedSubprocessWriter(ForkedSubprocessIOBase):
    """The ForkedSubprocessWriter class handles writing an list to a stream."""

    # Writer condition
    _writer_cond: threading.Condition
    # Lines we're going to be sending
    _lines: List[str]
    # Trigger to stop thread and exit
    _stop: bool
    # Are we closed?
    _closed: bool

    def __init__(self, pipe: IO[Any]):
        """Initialize our class."""

        # Initialize base class
        super().__init__(pipe)

        # Create the thread and its condition
        self._writer_cond = threading.Condition()

        # Setup the lines list we're going to be sending
        self._lines = []

        # Setup stop condition
        self._stop = False

        # Closed status
        self._closed = False

    def send(self, text: str):
        """Send text to the pipe."""

        self._lines.append(text)
        # Use lock
        with self._writer_cond:
            self._writer_cond.notify_all()

    def stop(self):
        """Send stop signal."""

        # Notify threads to process, and in this case exit
        self._stop = True
        # Use lock
        with self._writer_cond:
            self._writer_cond.notify_all()

    def _thread_target(self):
        """Worker of this class."""

        # Carry on looping
        while True:

            # If we're stopping break
            if self._stop:
                break

            # Use lock
            with self._writer_cond:

                # If there is no lines, wait
                if not self._lines:
                    self._writer_cond.wait()

                # Loop with lines...
                while self._lines:
                    line = self._lines.pop(0)
                    self._pipe.write(f'{line}\n')

        # Close pipe as we're done
        self._pipe.close()


# pylama: ignore=R0902
class ForkedSubprocess:
    """The ForkedSubprocess class handles curating a subprocess to send and receive data."""

    # Command and args to create the subprocess
    _args: List[str]

    # Environment to pass to subprocess
    _env: Optional[Dict[str, str]]

    # This is the process we created
    _process: subprocess.Popen
    # STDIO readers and writers
    _stdout_reader: Optional[ForkedSubprocessReader]
    _stderr_reader: Optional[ForkedSubprocessReader]
    _stdin_writer: Optional[ForkedSubprocessWriter]
    # Output
    _stdout: List[str]
    _stderr: List[str]
    _output: List[str]

    # Are we going to output lines we received
    _enable_output: bool

    # Callback for output lines we received
    _output_callback: Optional[OutputCallback]

    def __init__(self, args: List[str], **kwargs):
        """Initialize our class."""

        self._args = args

        # Check if we have an ENV to pass to the subprocess
        self._env = kwargs.get('env', None)

        # Enable output to terminal
        self._enable_output = kwargs.get('enable_output', False)

        # Check if we have an output callback
        self._output_callback = kwargs.get('output_callback', None)

        # Clear internal data
        self._clear_data()

    def run(self):
        """Run the subprocess."""

        # Clear internal data
        self._clear_data()

        # Run process
        self._process = subprocess.Popen(self._args, env=self._env,
                                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                         text=True)

        # Check what we're going to output to the terminal
        enable_stdout = False
        enable_stderr = False
        if self._enable_output:
            enable_stdout = True
            enable_stderr = True

        # Create the readers and writers
        self._stdout_reader = ForkedSubprocessReader(self._process.stdout,
                                                     [self._stdout, self._output],
                                                     output=enable_stdout,
                                                     output_callback=self._output_callback)
        self._stderr_reader = ForkedSubprocessReader(self._process.stderr,
                                                     [self._stderr, self._output],
                                                     output=enable_stderr,
                                                     output_callback=self._output_callback)
        self._stdin_writer = ForkedSubprocessWriter(self._process.stdin)

        # Start the readers and writers
        self._stdout_reader.start()
        self._stderr_reader.start()
        self._stdin_writer.start()

    def send(self, text: str):
        """Send the subprocess text over stdin."""

        # Raise an error
        if not self._process:
            raise ForkedSubprocessNotRunningException('send() was called on a subprocess which is not running')

        # We use the IF so we don't trigger a typing error on the None possibility
        if self._stdin_writer:
            self._stdin_writer.send(text)

    def wait(self) -> int:
        """Wait for subprocess to exit."""

        # Raise an error
        if not self._process:
            raise ForkedSubprocessNotRunningException('wait() was called on a subprocess which is not running')

        # Stop writer
        self._stdin_writer.stop()

        # Wait for process exit
        self._process.wait()

        # Wait for threads to read data and exit
        self._stdin_writer.wait()
        self._stdout_reader.wait()
        self._stderr_reader.wait()

        return self._process.returncode

    @property
    def output(self):
        """Return the output we got from the process."""
        return self._output

    @property
    def stderr(self):
        """Return the stderr we got from the process."""
        return self._stderr

    @property
    def stdout(self):
        """Return the stdout we got from the process."""
        return self._stdout

    def _clear_data(self):
        """Clear internal data."""

        self._process = None

        self._stdout_reader = None
        self._stderr_reader = None
        self._stdin_writer = None

        self._stdout = []
        self._stderr = []
        self._output = []
