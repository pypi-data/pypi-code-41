import sensorsanalytics

# 神策分析数据接收的 URL
SA_SERVER_URL = 'https://test-hechun.datasink.sensorsdata.cn/sa?project=yuejianzhong&token=d28b875ed9ac268f'

SA_SERVER_URL1 = 'https://sdk-test.datasink.sensorsdata.cn/sa?project=support&token=95c73ae661f85aa0'


# 发送数据的超时时间，单位毫秒
SA_REQUEST_TIMEOUT = 100000
# 当缓存的数据量达到参数值时，批量发送数据
SA_BULK_SIZE = 100

# 初始化 Batch Consumer
consumer = sensorsanalytics.DebugConsumer(SA_SERVER_URL1, SA_BULK_SIZE, SA_REQUEST_TIMEOUT)

# 使用 Consumer 来构造 SensorsAnalytics 对象
sa = sensorsanalytics.SensorsAnalytics(consumer,enable_time_free = True)

distinct_id = 'ABCDEF123456789'
properties = {
    # 用户 IP 地址
    # 商品 ID 列表，list<str> 类型的属性
    'ProductIdList' : ['123456AAA', '234567', '345678'],
    # 订单价格
    'OrderPaid' : 12.10,
    'time_local':'2019-07-10 17:51:21.234'
}
sa.track(distinct_id, 'BuyGold', properties, is_login_id=True)

sa.track(1234, 'Test', {'From1': 'Baidu', '$token': "dhuw393jdcioj39", '$project': "yuejianzhong"})


# sa.item_set(item_type='aaa',item_id='iddd',properties={'item_name':'name'})
sa.item_delete(item_type='aaa',item_id='iddd')

sa.flush()
# 程序结束前调用 close() ，通知 Consumer 发送所有缓存数据
# sa.close()