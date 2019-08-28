import sensorsanalytics

# lisa = person.person('Lisa', 99)
#
# print(lisa.name, lisa.get_grade())

# person()

# lisa = person.person('Lisa', 99)
# print(lisa.name, lisa.get_grade())

# 神策分析数据接收的 URL
SA_SERVER_URL = 'https://test-hechun.datasink.sensorsdata.cn/sa?project=yuejianzhong&token=d28b875ed9ac268f'


sa_url = 'https://vipcloud2.datasink.sensorsdata.cn/sa?project=zhupj&token=207f6fc5228dadcd'

#https://test-hechun.datasink.sensorsdata.cn/sa?project=yuejianzhong&token=d28b875ed9ac268f
# 发送数据的超时时间，单位毫秒
SA_REQUEST_TIMEOUT = 100000
# Debug 模式下，是否将数据导入神策分析
#   True - 校验数据，并将数据导入到神策分析中
#   False - 校验数据，但不进行数据导入
SA_DEBUG_WRITE_DATA = True

# 初始化 Debug Consumer
consumer = sensorsanalytics.DebugConsumer(sa_url, SA_DEBUG_WRITE_DATA, SA_REQUEST_TIMEOUT)

# 使用 Consumer 来构造 SensorsAnalytics 对象
sa = sensorsanalytics.SensorsAnalytics(consumer,enable_time_free=True)

# item_type = 'apple'
# item_id = '12345'
# sa.item_set(item_type, item_id, {"price": "3"})
properties = {
    # 用户 IP 地址
    # 商品 ID 列表，list<str> 类型的属性
    # 订单价格
    'OrderPaid' : 12.10,
    'OrderTime':'2019-07-01 12:02:36',
    '$time' : 1546275661000
}

# 记录用户订单付款事件
sa.track("aaa", 'PaidOrder', properties, is_login_id=True)
sa.item_set("item_type","item_id",properties)
sa.item_delete("item_type","item_id",properties)