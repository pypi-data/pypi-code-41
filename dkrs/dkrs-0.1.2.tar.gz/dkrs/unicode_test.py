import unittest

from dkrs.unicode import Unicode


class MyTestCase(unittest.TestCase):

    def test_is_zh_traditional(self):
        self.assertEqual(Unicode.is_zh_traditional('F'), False)
        self.assertEqual(Unicode.is_zh_traditional('1'), False)
        self.assertEqual(Unicode.is_zh_traditional(','), False)
        self.assertEqual(Unicode.is_zh_traditional('#'), False)
        self.assertEqual(Unicode.is_zh_traditional('中'), False)
        self.assertEqual(Unicode.is_zh_traditional('體'), True)
        self.assertEqual(Unicode.is_zh_traditional('の'), False)
        self.assertEqual(Unicode.is_zh_traditional('中国'), False)
        self.assertEqual(Unicode.is_zh_traditional('节點'), False)
        self.assertEqual(Unicode.is_zh_traditional('節點'), True)

    def test_is_zh_simplified(self):
        self.assertEqual(Unicode.is_zh_simplified('中'), True)
        self.assertEqual(Unicode.is_zh_simplified('中国'), True)
        self.assertEqual(Unicode.is_zh_simplified('F'), False)
        self.assertEqual(Unicode.is_zh_simplified('1'), False)
        self.assertEqual(Unicode.is_zh_simplified(','), False)
        self.assertEqual(Unicode.is_zh_simplified('#'), False)
        self.assertEqual(Unicode.is_zh_simplified('の'), False)
        self.assertEqual(Unicode.is_zh_simplified('體'), False)
        self.assertEqual(Unicode.is_zh_simplified('节點'), False)
        self.assertEqual(Unicode.is_zh_simplified('節點'), False)

    def test_traditional_to_simplified(self):
        """
        测试繁体 转 简体
        """
        self.assertEqual(Unicode.traditional_to_simplified('1'), '1')
        self.assertEqual(Unicode.traditional_to_simplified('11'), '11')
        self.assertEqual(Unicode.traditional_to_simplified('体'), '体')
        self.assertEqual(Unicode.traditional_to_simplified('體'), '体')
        self.assertEqual(Unicode.traditional_to_simplified('身體'), '身体')
        self.assertEqual(Unicode.traditional_to_simplified('節點'), '节点')

        self.assertNotEqual(Unicode.traditional_to_simplified('身體'), '身體')

    def test_simplified_to_traditional(self):
        """
        测试简体 转 繁体
        """

        self.assertEqual(Unicode.simplified_to_traditional('1'), '1')
        self.assertEqual(Unicode.simplified_to_traditional('11'), '11')
        self.assertEqual(Unicode.simplified_to_traditional('体'), '體')
        self.assertEqual(Unicode.simplified_to_traditional('身体'), '身體')
        self.assertEqual(Unicode.simplified_to_traditional('节点'), '節點')
        self.assertEqual(Unicode.simplified_to_traditional('身體'), '身體')

        self.assertNotEqual(Unicode.simplified_to_traditional('体'), '体')
        self.assertNotEqual(Unicode.simplified_to_traditional('身体'), '身')
        self.assertNotEqual(Unicode.simplified_to_traditional('身体'), '身体')


if __name__ == '__main__':
    unittest.main()
