from CustomerSelection import CustomerSelection
from math import radians
import json

dub_lon = -6.257664
dub_lat = 53.339428
dub_lon,dub_lat = map(radians, [dub_lon,dub_lat])
customerdataArr = []
filedata = open("datafile.txt", "r")
for item in filedata:
  customerdata = json.loads(item)
  customerdataArr.append(customerdata)
selectionarea = CustomerSelection(dub_lon,dub_lat,customerdataArr)
selectionarea.distanceCalculation()
selectionarea.dataSorting()
selectionarea.displayCustomer()



