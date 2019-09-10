import unittest
from fastutils.listutils import chunk
from fastutils.listutils import pad
from fastutils.listutils import clean_none


class TestListUtils(unittest.TestCase):
    def test01(self):
        data = [1,2,3,4]
        data2 = chunk(data, 3)
        assert data2[0] == [1, 2, 3]

    def test02(self):
        data = [1,2,3,4]
        data2 = chunk(data, 2)
        assert data2[0] == [1, 2]
        assert data2[1] == [3, 4]
        assert len(data2) == 2

    def test03(self):
        data = [1,2,3,4]
        data2 = chunk(data, 2, with_padding=True)
        assert data2[0] == [1, 2]
        assert data2[1] == [3, 4]
        assert len(data2) == 2

    def test04(self):
        data = [1,2,3,4]
        data2 = chunk(data, 3, with_padding=True)
        assert data2[0] == [1, 2, 3]
        assert data2[1] == [4, None, None]
        assert len(data2) == 2

    def test05(self):
        data = []
        pad(data, 3, 1)
        assert data == [1, 1, 1]

    def test06(self):
        data = [1]
        pad(data, 3, 1)
        assert data == [1, 1, 1]

    def test07(self):
        data = [1, 1]
        pad(data, 3, 1)
        assert data == [1, 1, 1]

    def test08(self):
        data = [1, 1, 1]
        pad(data, 3, 1)
        assert data == [1, 1, 1]

    def test09(self):
        data = [1, 1, 1, 1]
        pad(data, 3, 1)
        assert data == [1, 1, 1, 1]

    def test10(self):
        assert clean_none([]) == []
        assert clean_none([1]) == [1]
        assert clean_none([1, 2]) == [1, 2]
        assert clean_none([1, None, 2]) == [1, 2]
        assert clean_none([1, None, 2, None]) == [1, 2]

if __name__ == "__main__":
    unittest.main()
