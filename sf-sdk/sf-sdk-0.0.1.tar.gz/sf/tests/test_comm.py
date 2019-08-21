#!/usr/bin/python3
# @Time    : 2019-08-21
# @Author  : Kevin Kong (kfx2007@163.com)

import unittest
from sf.api import SF


class TestComm(unittest.TestCase):

    def test_verifycode(self):
        """测试校验码"""
        sf = SF("QXH", "yxGvL9y1bJj9mRy9rIjZVBK4nokAwxrf")
        print(sf.comm.gen_verifycode(None))

    def test_xmldata(self):
        """测试报文生成格式"""
        sf = SF("QXH", "yxGvL9y1bJj9mRy9rIjZVBK4nokAwxrf")
        data = {
            "service": "服务名",
            "clientcode": "顾客编码",
            "data": {
                "Order":{
                    "orderid":"TEST20180410001",
                    "Cargo":{
                        "name":"手机"
                    }
                }
            }
        }

        print(sf.comm.gen_xmldata(data))

    def test_parse(self):
        """测试xml解析"""
        sf = SF("QXH", "yxGvL9y1bJj9mRy9rIjZVBK4nokAwxrf")
        data = """
        <Response service="OrderService">  
    <Head>OK</Head>
    <Body>
          <OrderResponse 
            filter_result="2" 
            destcode="755" 
            mailno="619428034014" 
            origincode="755" 
            orderid="TEST20180410001">
          <rls_info 
            rls_errormsg="619428034014:" 
            invoke_result="OK" 
            rls_code="1000">
              <rls_detail waybillNo="619428034014" 
                sourceTransferCode="755WF" 
                sourceCityCode="755" 
                sourceDeptCode="755AQ" 
                sourceTeamCode="036" 
                destCityCode="755" 
                destDeptCode="755AQ" 
                destDeptCodeMapping="755WF-S3" 
                destTeamCode="036" 
                destTransferCode="755WF" 
                destRouteLabel="755WF-S3" 
                proName="顺丰标快" 
                cargoTypeCode="C201" 
                limitTypeCode="T4" 
                expressTypeCode="B1" 
                codingMapping="S3" 
                xbFlag="0" 
                printFlag="000000000" 
                twoDimensionCode="MMM={'k1':'755WF','k2':'755AQ','k3':'036','k4':'T4','k5':'619428034014','k6':'','k7':'dce4e1c6','k7':'3fc52389'}"
                proCode="T4" 
                printIcon="00000000"/>
            </rls_info>
        </OrderResponse>
    </Body>
</Response>
        """
        print(sf.comm.parse_response(data))


if __name__ == "__main__":
    unittest.main()
