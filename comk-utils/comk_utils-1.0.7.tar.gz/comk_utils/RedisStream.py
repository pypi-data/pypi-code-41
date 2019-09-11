from . import RedisUtils


class RedisStream():
    def __init__(self, host='localhost', port=6379, db=1, decode_responses=True, stream_name='default_stream',
                 group_name='default_group', consumer_name='default_consumer'):
        super().__init__()
        self.ru = RedisUtils(host, port, db, decode_responses)
        self.r = self.ru.get_redis_connection_pool_link()
        if stream_name and group_name and consumer_name:
            self.stream_name = stream_name
            self.group_name = group_name
            self.consumer_name = consumer_name
        else:
            raise Exception('stream_name、group_name、consumer_name must be not null')

    def rs_xadd(self, data):
        '''
        追加消息
        首次使用xadd指令追加消息时，自动创建stream

        :param data:
        :return:
        '''
        return self.r.xadd(self.stream_name, data)

    def rs_xinfo_stream(self):
        '''
        获取stream的信息

        :return:
        '''
        return self.r.xinfo_stream(self.stream_name)

    def rs_xrange(self, min='-', max='+', count=None):
        '''
        获取消息列表

        :return:
        '''
        return self.r.xrange(self.stream_name, min=min, max=max, count=count)

    def rs_get_data_by_ids(self, ids):
        '''
        获取消息列表

        :return:
        '''
        result = self.rs_xrange(min=ids, count=1)
        return result[0][1]

    def rs_xgroup_create(self, id='0-0'):
        '''
        创建group

        :param id:
        :return:
        '''
        group_name = self.group_name
        groups_names = self.get_groups_names()
        if group_name not in groups_names:
            result = self.r.xgroup_create(self.stream_name, group_name, id)
            return result
        return False

    def rs_xinfo_groups(self):
        '''
        获取stream的groups信息

        :return:
        '''
        return self.r.xinfo_groups(self.stream_name)

    def get_groups_names(self):
        '''
        获取groups的名称列表

        :return:
        '''
        result = self.rs_xinfo_groups()
        groups_names = [x['name'] for x in result]  # 获取groups_names
        return groups_names

    def rs_xread_create(self, ids='0-0'):
        '''
        创建一个消费者

        :param ids:
        :return:
        '''
        stream_dict = {self.stream_name: ids}
        return self.r.xreadgroup(self.group_name, self.consumer_name, stream_dict)

    def rs_xinfo_consumers(self):
        '''
        读取一个group内的消费者信息

        :return:
        '''
        return self.r.xinfo_consumers(self.stream_name, self.group_name)

    def rs_xreading(self, count=None, block=None):
        '''
        请求处理消息

        :return:
        '''
        stream_dict = {self.stream_name: '>'}
        return self.r.xreadgroup(self.group_name, self.consumer_name, stream_dict, count, block)

    def rs_xpending(self):
        '''
        获取正在处理中的消息

        :return:
        '''
        return self.r.xpending(self.stream_name, self.group_name)

    def rs_xack(self, ids):
        '''
        返回一个成功标记，表明该消息已经处理

        :param ids:
        :return:
        '''
        return self.r.xack(self.stream_name, self.group_name, ids)

    def handling(self, method=None):
        '''
        处理消息程序

        :param method: 自定义方法
        :return: 如果有自定义方法，则返回自定义方法产生的结果
        '''
        self.rs_xreading()  # 先加载消息
        xpending_result = self.rs_xpending()  # 再获取加载到队列的消息
        pending = xpending_result['pending']
        print(pending)
        while pending != 0:
            ids = xpending_result['min']
            data = self.rs_get_data_by_ids(ids)
            if method:
                result = method(data)  # 执行自定义任务，获取结果
                if result:
                    self.rs_xack(ids)  # 执行任务成功后，标记该消息
                    return result
            else:
                self.rs_xack(ids)  # 执行任务成功后，标记该消息
            xpending_result = self.rs_xpending()  # 重新获取加载到队列的消息
            pending = xpending_result['pending']


if __name__ == '__main__':
    rs = RedisStream()
    result = rs.rs_xinfo_stream()  # 获取stream的信息
    print(result)
    # result = rs.rs_xrange()  # 获取stream的消息列表
    # print(result)

    # result = rs.rs_xgroup_create()
    # print(result)

    result = rs.rs_xinfo_groups()
    print(result)

    result = rs.rs_xinfo_consumers()
    print(result)
