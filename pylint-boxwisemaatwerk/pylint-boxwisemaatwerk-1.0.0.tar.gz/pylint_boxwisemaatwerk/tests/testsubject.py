import clr
from Wms.RemotingObjects.Zones import ZoneUsers
from Wms.RemotingObjects import FindableList
from Wms.RemotingObjects.Sales import HistorySalesOrder
from Wms.RemotingObjects.Printing import PrintPickingListArgs
from Wms.RemotingImplementation.Caching import CachableString
from Wms.RemotingImplementation.BlobStorage import BlobExtensions
from Wms.RemotingImplementation import General,AppHost
from Wms.RemotingImplementation import Outbound,Inbound,Inventory


general123 = General()
Printing.config.FOXIT_PATH = "C:\Program Files (x86)\TranCon\BOXwisePro\Server\pdfprint.bat"
ZoneUsers.AddRange
FindableList.AddRange
general123.GetDocumentPrinterOfCurrentUser()
general123.GetLabelPrinterOfCurrentUser()
general123.GetPrintersOfUser()


class persoon:
    name = ''
    def foo(self,name):
        self.name = name
6[0] # pylint: disable=unsubscriptable-object


General.GetSettings()

General.AddOrUpdateErpLockDirect()
General.GetLabelPrinterOfCurrentUser()
sir = Outbound()
sir.PickInBatch()
sir.MovePackageItems()
Inbound.GetVendorsExpectedByFilter()
Inbound.GetItemVendors()
Inventory.ProcessWarehouseTransfer()