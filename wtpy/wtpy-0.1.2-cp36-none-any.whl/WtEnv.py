from wtpy.porter import WtWrapper
from wtpy.Context import Context

from .ProductMgr import ProductMgr
from .SessionMgr import SessionMgr

def singleton(cls):
    instances = {}
    def getinstance(*args,**kwargs):
        if cls not in instances:
            instances[cls] = cls(*args,**kwargs)
        return instances[cls]
    return getinstance

@singleton
class WtEnv:

    def __init__(self):
        self.__wrapper__ = WtWrapper()
        self.__ctx_dict__ = dict()

    def init(self, folder, cfgfile = "config.json"):
        self.__wrapper__.initialize(self, cfgfile)

        self.productMgr = ProductMgr()
        self.productMgr.load(folder + "commodities.json")

        self.sessionMgr = SessionMgr()
        self.sessionMgr.load(folder + "sessions.json")

    def getSessionByCode(self, code):
        pInfo = self.productMgr.getProductInfo(code)
        if pInfo is None:
            return None

        return self.sessionMgr.getSession(pInfo.session)

    def getSessionByName(self, sname):
        return self.sessionMgr.getSession(sname)

    def getProductInfo(self, code):
        return self.productMgr.getProductInfo(code)

    def add_strategy(self, strategy):

        id = self.__wrapper__.create_context(strategy.name())
        self.__ctx_dict__[id] = Context(id, strategy, self.__wrapper__, self)

    def get_context(self, id):
        if id not in self.__ctx_dict__:
            return None

        return self.__ctx_dict__[id]

    def run(self):
        self.__wrapper__.run()