from py_analytics_api.py_analytics_api import PyAnalyticsApi


class TestPyAnalyticsApi():
    ip = '172.24.76.225'
    endpoint = 'tdfana'
    datasource = 'etx'
    measure_period = 5

    def test_connection(self):
        api_wrapper = PyAnalyticsApi(self.ip, self.endpoint, self.datasource, self.measure_period)
        result = api_wrapper.get_all_roadways('link')
        assert len(result) > 0

    def test_get_day_ts_for_item(self):
        item_id = 1
        item_type = 'measurement_site'
        measure = 'volume'
        data_types = ['real', 'normal', 'forecasth']
        horizon = 15
        day = '20180505'
        api_wrapper = PyAnalyticsApi(self.ip, self.endpoint, self.datasource, self.measure_period)
        result = []
        for data_type in data_types:
            result.append(api_wrapper.get_day_ts_for_item(item_id, item_type, measure, data_type, horizon, day))
        assert (len(result[0]) == len(result[1])) and (len(result[0]) == len(result[1])) and (
                    len(result[0]) == len(result[1]))

    def test_get_all_get_all_items_roadways_and_name(self):
        item_type = 'measurement_site'
        measure = 'volume'
        api_wrapper = PyAnalyticsApi(self.ip, self.endpoint, self.datasource, self.measure_period)
        result = api_wrapper.get_all_items_roadways_and_name(item_type, measure)
        # get a first element to check if it has two values for the roadway and itemName
        element = result[list(result.keys())[0]]
        assert isinstance(result, dict) and isinstance(element['roadway'], str) and isinstance(element['itemName'], str)
