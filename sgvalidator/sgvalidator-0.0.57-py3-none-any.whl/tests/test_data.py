import os
import csv
import pandas as pd


def getFakeData(fname='sample_data_good_header.csv'):
    data = []
    path = os.path.join(os.path.dirname(__file__), fname)
    with open(path) as csv_file:
        reader = csv.DictReader(csv_file, skipinitialspace=True)
        for row in reader:
            data.append(row)
    return data


class TestDataFactory:
    columns = ["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
               "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"]

    @staticmethod
    def getDefaultRow():
        return DefaultRow()

    @staticmethod
    def defaultRowsToPandasDf(listOfDefaultRows, cols=None):
        if cols is None:
            cols = TestDataFactory.columns
        inp = list(map(lambda x: x.toList(), listOfDefaultRows))
        return pd.DataFrame(inp, columns=cols)


class DefaultRow:
    def __init__(self):
        self.locator_domain = "example.com"
        self.location_name = "example"
        self.street_address = "1543 Mission St"
        self.city = "San Francisco"
        self.state = "CA"
        self.zip = "94103"
        self.country_code = "US"
        self.store_number = "10"
        self.phone = "2149260428"
        self.location_type = "ATM"
        self.latitude = "37.868692"
        self.longitude = "-122.814205"
        self.hours_of_operation = "24/7'"

    def toList(self):
        return [
            self.locator_domain,
            self.location_name,
            self.street_address,
            self.city,
            self.state,
            self.zip,
            self.country_code,
            self.store_number,
            self.phone,
            self.location_type,
            self.latitude,
            self.longitude,
            self.hours_of_operation
        ]

    def copy(self, locator_domain=None, location_name=None, street_address=None, city=None, state=None, zip=None,
             country_code=None, store_number=None, phone=None, location_type=None, latitude=None, longitude=None,
             hours_of_operation=None):
        if locator_domain is not None:
            self.locator_domain = locator_domain

        if location_name is not None:
            self.location_name = location_name

        if street_address is not None:
            self.street_address = street_address

        if city is not None:
            self.city = city

        if state is not None:
            self.state = state

        if zip is not None:
            self.zip = zip

        if country_code is not None:
            self.country_code = country_code

        if store_number is not None:
            self.store_number = store_number

        if phone is not None:
            self.phone = phone

        if location_type is not None:
            self.location_type = location_type

        if latitude is not None:
            self.latitude = latitude

        if longitude is not None:
            self.longitude = longitude

        if hours_of_operation is not None:
            self.hours_of_operation = hours_of_operation
        return self
