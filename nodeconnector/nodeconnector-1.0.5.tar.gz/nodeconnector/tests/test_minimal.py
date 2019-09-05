import unittest

import nodeconnector


class TestMinimal(unittest.TestCase):
    """
    Arguments test
    """

    def test_arguments(self):
        api = nodeconnector.Interface()
        # default port
        self.assertTrue((api.socket_address == 'tcp://127.0.0.1:24001'))
        # custom port
        api.listen(8080)
        self.assertTrue((api.socket_address == 'tcp://127.0.0.1:8080'))
        # end socket
        # api.end()


if __name__ == '__main__':
    unittest.main()
