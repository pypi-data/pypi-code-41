import requests


class PyAnalyticsApi:
    def __init__(self, host, endpoint, datasource, measure_period):
        """
        Initialise the API object
        :param datasource: the datasource to be used for this API wrapper
        :param host: the IP of the Analytics Service
        :param endpoint: the name of the endpoint for the service e.g. tdfana, predictive...
        """
        self.host = host
        self.endpoint = 'http://{0}:8080/{1}/rest/'.format(host, endpoint)
        self.datasource = datasource
        self.measure_period = measure_period
        self.ts_endpoint = '/getTimeSeries'
        self.cluster_endpoint = '/getCluster'
        self.roadways_endpoint = '/getRoadwaysWithItems'
        self.items_for_roadways_endpoint = '/getItemsOfRoadway'

    def get_ts_for_item(self, item_id, item_type, measure, data_type='real', horizon=None,
                        from_time='20180724050000', to_time='20180724090000'):
        """
        Get a Time Series of values for a given item from one timestamp to another
        :param item_id: integer with the item id
        :param item_type: e.g. link, measurement_site
        :param measure: e.g. volume, speed, los
        :param data_type: e.g. real, forecasth, normal
        :param horizon: the horizon to be used in case of forecasth e.g. 5, 15, 30
        :param from_time: get values from a given timestamp. The format is YYYYMMDDhhmmss
        :param to_time: get values to a given timestamp. The format is YYYYMMDDhhmmss
        :return: list of integers
        """
        params = {
            'datasourceName': self.datasource,
            'itemType': item_type,
            'itemId': item_id,
            'measureName': measure,
            'dataType': data_type,
            'dateTimeFrom': from_time,
            'dateTimeToInclusive': to_time,
            'measurePeriod': self.measure_period,
            'forecastAheadMinutes': [horizon]
        }
        response = requests.get(self.endpoint + self.ts_endpoint,
                                params=params).json()
        # response has one key for each of the measures queried e.g. 'etx:measurement_site:16:volume:5:real'
        try:
            for k, v in response.items():
                res = v['values']
        except TypeError:
            res = []
        return res

    def get_day_ts_for_item(self, item_id, item_type, measure, data_type='real', horizon=5, day='20180724'):
        """
        It returns the time series for a given item id and day
        :param item_id: integer with the item id
        :param item_type: e.g. link, measurement_site
        :param measure: e.g. volume, speed, los
        :param data_type: e.g. real, forecasth, normal
        :param horizon: the horizon to be used in case of forecasth e.g. 5, 15, 30
        :param day: the day of interest. The format is YYYYMMDD
        :return: list of integers
        """
        from_time = day + '000000'
        to_time = day + '235959'
        return self.get_ts_for_item(item_id, item_type, measure, data_type,
                                    horizon, from_time=from_time, to_time=to_time)

    def get_all_roadways(self, item_type):
        """
        Roadways is the first combo you select in analytics. It gives the ids and the names of these roadways
        :param item_type: e.g. link, measurement_site
        :return: a list with pairs of {id,name} e.g. {'id': '8651', 'name': 'Paseo de Zorrilla (E)'}
        """
        params = {'datasourceName': self.datasource, 'itemType': item_type}
        # el roadways endpoint solo te da los ids de los roadways
        response = requests.get(self.endpoint + self.roadways_endpoint,
                                params=params).json()
        return response

    def get_items_for_roadway(self, roadway_id, measure, item_type):
        """
        Each roadway has a series of items attached. This returns a list of their ids, the names and the available data
        :param roadway_id: int with the id of the roadway
        :param measure: e.g. volume, speed
        :param item_type: e.g. link, measurement_site
        :return: a list with tuples of {itemId, itemName, availableDataTypes}
        e.g. {'itemId': 12, 'itemName': 'PM032306 (CTRA. ESPERANZA -> ARIZA) (LT/ST)',
        'availableDataTypes': ['real', 'normal', 'forecast']}
        """
        # Aqui se le puede pasar el itemType = measurement_site para que te devuelva el item ID del MSS
        params = {'roadwayId': roadway_id, 'datasourceName': self.datasource, 'measureName': measure,
                  'measurePeriod': 5, 'itemType': item_type}
        response = requests.get(self.endpoint + self.items_for_roadways_endpoint,
                                params=params).json()
        return response

    def get_all_items(self, itemtype='link', measure='volume'):
        """
        It returns the ids of all the items of a given type for a given measure
        :param itemtype: e.g. link, measurement_site
        :param measure: e.g. volume, speed
        :return: a list of ints for that item type that have that measure
        """
        items = set()
        req_all_roadways = self.get_all_roadways(itemtype)
        for roadway in req_all_roadways:
            req_items = self.get_items_for_roadway(roadway['id'], measure, itemtype)
            for item in req_items:
                items.add(item['itemId'])
        return list(items)

    def get_all_items_roadways_and_name(self, itemtype='link', measure='volume'):
        """
        It returns a dictionary with keys representing the itemid and a value which is a pair {roadway, itemName}
        :param itemtype: the type of item
        :param measure: the measure of interest
        :return: dict{itemid : dict{roadway,itemName}}
        """
        result_dict = {}
        req_all_roadways = self.get_all_roadways(itemtype)
        for roadway in req_all_roadways:
            req_items = self.get_items_for_roadway(roadway['id'], measure, itemtype)
            for item in req_items:
                result_dict[item['itemId']] = {'roadway': roadway['name'], 'itemName': item['itemName']}
        return result_dict

    def get_cluster_data(self, item_id, item_type, measure):
        """
        It gets all the information related to the clusterisation of an item_id :param item_id: integer with the item
        id :param item_type: e.g. link, measurement_site :param measure: e.g. volume, speed :return: a tuple with {
        min_value, max_value, list[horizons],
        dict{'MAE' : [int], 'MASE' : [int] ...} global_quality_metrics,
        dict{'MAE' : [int], 'MASE' : [int] ...} quality_metrics,
        dict{id: {'id', 'name' , 'itemId', 'valueList' ...}} patterns_dict,
        dict{'YYYYMMDD000000' : 'strDate', 'tagList', 'patternId' ...}
        """
        params = {
            'datasourceName': self.datasource,
            'itemType': item_type,
            'itemId': item_id,
            'measureName': measure,
            'measurePeriod': self.measure_period,
            'lang': 'en'
        }
        response = requests.get(self.endpoint + self.cluster_endpoint,
                                params=params).json()
        min_value = response['minValue']
        max_value = response['maxValue']
        horizons = response['predictionHorizons']
        global_quality_metrics = response['globalPredictionQualityMetrics']
        quality_metrics = response['predictionQualityMetrics']
        # Since the REST API returns a patternList we would have to traverse the whole list to find the values for a
        # pattern ID. We build a dictionary instead with patterns_dict
        patterns_dict = {d['id']: d for d in response['patternList']}
        # Same with the list of days. We build a dictionary
        calendar_dict = {d['strDate']: d for d in response['patternDateList']}
        return min_value, max_value, horizons, global_quality_metrics, quality_metrics, patterns_dict, calendar_dict
