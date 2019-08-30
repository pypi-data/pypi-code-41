
class Switcher(object):
    def names(self, argument):
        """Dispatch method"""
        # Get the method from 'self'. Default to a lambda.
        method = getattr(self, argument, self.default)
        # Call the method as we return it
        return method(5)

    def opt1(self, x):
        return x

    def opt2(self, x):
        return 2 * x

    def default(self, _):
        return 'Default'


def numbers(arg=None):

    def opt1(x):
        return x

    def opt2(x):
        return 2 * x

    def default(_):
        return 'Default'

    switcher = {
        1: opt1,
        2: opt2
    }

    x = switcher.get(arg, default)(5)
    print(x)


if __name__ == '__main__':
    numbers(2)
    numbers(1)
    numbers(0)

    s = Switcher()
    print(s.names('opt2'))
    print(s.names('opt1'))
    print(s.names('opt0'))
