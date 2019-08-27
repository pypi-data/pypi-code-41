from ddcmaker import LSC_Client

lsc = LSC_Client.LSC_Client()
class showlib(object):
    def hiphop(self):
        lsc.RunActionGroup(16, 1)
        lsc.WaitForFinish(60000)
    def jiangnanstyle(self):
        lsc.RunActionGroup(17, 1)
        lsc.WaitForFinish(60000)
    def smallapple(self):
        lsc.RunActionGroup(18, 1)
        lsc.WaitForFinish(60000)
    def lasong(self):
        lsc.RunActionGroup(19, 1)
        lsc.WaitForFinish(60000)
    def feelgood(self):
        lsc.RunActionGroup(20, 1)
        lsc.WaitForFinish(60000)