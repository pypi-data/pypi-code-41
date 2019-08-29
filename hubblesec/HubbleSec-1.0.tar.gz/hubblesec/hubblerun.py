from demo2 import config

my_config = config.Config()


class RunHubble():
    '''
    python library for Guanxing
    '''

    def __init__(self):
        pass

    def virtual(self, name, key):
        self.name = name
        self.key = key
        self.config = my_config

    def do_work(self):
        '''
        we can do work on my compulte search start rule
        :return:
        '''
        dic = {}
        dic['name'] = self.name
        dic['key'] = self.key
        dic['mysql_host'] = self.config.mysql_host
        dic['mysql_pwd'] = self.config.mysql_pwd
        dic['message'] = 'we do every things for you ,HAH!!!'
        return dic


if __name__ == '__main__':
    rh = RunHubble()
    rh.virtual(name='aJay13', key='MGfgh2kJ5B6iTk')
    result = rh.do_work()
    print(result)
