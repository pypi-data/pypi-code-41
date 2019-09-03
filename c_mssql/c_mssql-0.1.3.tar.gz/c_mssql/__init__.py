class DB_Config(object):
    def __init__(self, server,user,password,database,port=1433):
        self.server=server
        self.user=user
        self.password=password
        self.database=database
        self.port=port