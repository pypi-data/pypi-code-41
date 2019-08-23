import io
import os
import unittest

from timeout_decorator import timeout_decorator

from symmetry.common.shell import Shell, parsed


class ShellTest(unittest.TestCase):

    @timeout_decorator.timeout(1)
    def test_echo_round_trip(self):
        fake_in = io.StringIO(os.linesep.join(['echo "foo"', 'exit']))
        fake_out = io.StringIO()

        shell = Shell(stdin=fake_in, stdout=fake_out)
        shell.prompt = ''
        shell.intro = None
        shell.use_rawinput = False
        shell.run()

        self.assertEqual('foo', fake_out.getvalue().strip())

    @timeout_decorator.timeout(1)
    def test_custom_shell_command(self):
        invocations = list()

        class MyShell(Shell):
            use_rawinput = False
            prompt = ''
            intro = None

            @parsed
            def do_custom_command(self, arg1: str, arg2: int):
                invocations.append(('custom_command', arg1, arg2))

        fake_in = io.StringIO(os.linesep.join(['custom_command "the answer" 42', 'exit']))
        fake_out = io.StringIO()

        MyShell(stdin=fake_in, stdout=fake_out).run()

        self.assertEqual(1, len(invocations))
        self.assertEqual(('custom_command', 'the answer', 42), invocations[0])
