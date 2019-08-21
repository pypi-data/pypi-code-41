#!/usr/bin/python3
# @Time    : 2019-08-21
# @Author  : Kevin Kong (kfx2007@163.com)

import unittest
from sf.api import SF


class TestOrder(unittest.TestCase):

    def test_order(self):
        """测试下单"""
        sf = SF("QXH", "yxGvL9y1bJj9mRy9rIjZVBK4nokAwxrf")

        print(sf.order.create_order("SFKD-20160219000020", "测试公司",
                                    "张三", "18512345678", "丰县", "北京市昌平区", "15112345678"))

    


if __name__ == "__main__":
    unittest.main()
