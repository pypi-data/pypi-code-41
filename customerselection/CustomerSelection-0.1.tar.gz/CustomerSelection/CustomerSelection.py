from math import radians, cos, sin, asin, sqrt
import json

class CustomerSelection:
	# approximate radius of earth in km
	R = 6373.0
	def __init__(self, center_area_lon,center_area_lat,customerdataArr):
		self.center_area_lon = center_area_lon
		self.center_area_lat = center_area_lat
		self.customerdataArr = customerdataArr
		self.passedlist = []
	def sortByUserId(e):
		return e['user_id'] 
	def dataSorting(self):
		self.passedlist.sort(key=CustomerSelection.sortByUserId)
		#return self.passedlist
		
	def displayCustomer(self):
		for item in self.passedlist:
			print("------------>")
			print("name:",item['name'])
			print("User Id:",item['user_id'])
			
	def distanceCalculation(self):
		for item in self.customerdataArr:
			lon = float(item["longitude"])
			lat = float(item["latitude"])
			
			lon,lat = map(radians, [lon,lat])
			dlon = lon - self.center_area_lon
			dlat = lat - self.center_area_lat
			#print(dlon)
			
			a = sin(dlat / 2)**2 + cos(self.center_area_lat) * cos(lat) * sin(dlon / 2)**2
			c = 2 * asin(sqrt(a))
			distance = CustomerSelection.R * c
			
			if distance < 100:
				self.passedlist.append(item)
		
		#return self.passedlist