import unittest
from __init__ import create_patch, apply_patch


class TestDiff(unittest.TestCase):

    def test_all(self):
        a = """Here is a test
With all possible cases
There is deletion
Of multiple lines
There is empty lines

There is also insertion of multiple lines
There is also deletion of a single line
And insertion of a single line
Fuck"""
        b = """
Here is a test
With all possible cases
There is empty lines

There is also insertion of multiple lines
Here
And also here
And insertion of a single line
Right here"""
        patch = create_patch(a, b)
        mayb = apply_patch(a, patch)
        self.assertEqual(b, mayb)


if __name__ == '__main__':
    unittest.main()
