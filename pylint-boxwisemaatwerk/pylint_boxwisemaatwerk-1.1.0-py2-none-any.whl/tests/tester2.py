from Wms.RemotingImplementation import Printing, General
from Wms.RemotingObjects.Printing import PrintPickingListArgs
from System import Guid
from System.Collections.Generic import List




class student(persoon):
    group = ""
    def bar(self, group):
        self.group = group
    instance = student

student1 = student().instance().instance().instance()

student1.instance().instance()