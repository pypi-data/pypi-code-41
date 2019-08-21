"""OGTRest exposes the OGT rest api."""
import requests
from .ogtstop import OGTStop
from .ogtdeparture import OGTDeparture


class OGTRest(object):
    """Static class that exposes the OGT rest api."""

    URL_REST = 'https://rest.ostgotatrafiken.se/'
    METHOD_STOPS_FIND = 'stops/Find'
    METHOD_STOPS_INFOS = 'stops/Infos'
    METHOD_STOP_DEPARTURES = 'stopdepartures/departures'

    @staticmethod
    def get(method, params):
        """Perform a http get requests to the OGT rest api."""
        url = OGTRest.URL_REST + method
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        return None

    @staticmethod
    def stops_find(query):
        """Find stops that matches the query."""
        # Define method and params
        method = OGTRest.METHOD_STOPS_FIND
        params = {
            'q': query,
            'pointType': 'stop',
        }

        # Send request
        stops = OGTRest.get(method, params)

        # Convert to list of OGTStop
        ogt_stops = []
        if stops is not None:
            for stop in stops:
                name = stop['OgtStopUrlSegment']
                id_ = stop['Id']
                pretty_name = stop['PlaceName']
                ogt_stops.append(OGTStop(name, id_, pretty_name))

        # Return stops
        return ogt_stops

    @staticmethod
    def stops_infos(ids):
        """Find stops that matches the ids."""
        # Define method and params
        method = OGTRest.METHOD_STOPS_INFOS
        if isinstance(ids, (list,)):
            ids = ','.join(map(str, ids))
        params = {
            'ids': ids,
        }

        # Send request
        stops = OGTRest.get(method, params)

        # Convert to list of OGTStop
        ogt_stops = []
        if stops is not None:
            for stop in stops:
                name = stop['OgtStopUrlSegment']
                id_ = stop['Id']
                pretty_name = stop['PlaceName']
                ogt_stops.append(OGTStop(name, id_, pretty_name))

        # Return stops
        return ogt_stops

    @staticmethod
    def stop_departures(stop_id, num_departures=5):
        """Find stop departures that matches the stop_id."""
        # Define method and params
        method = OGTRest.METHOD_STOP_DEPARTURES
        sort_order = 'DepartureTime'  # LineNumber
        params = {
            'stopAreaId': stop_id,
            'date': '',
            'delay': 0,
            'maxNumberOfResultPerColumn': num_departures,
            'columnsPerPageCount': 1,
            'pagesCount': 1,
            'lines': ','.join([]),
            'trafficTypes': ','.join([]),
            'stopPoints': ','.join([]),
            'sortOrder': sort_order,
            'useDaySeparator': False,
        }

        # Send request
        data_departures = OGTRest.get(method, params)['groups'][0]

        # Convert to list of OGTDeparture
        ogt_departures = []
        if data_departures is not None:
            for data_departure in data_departures:
                data_line = data_departure['Line']
                name = data_line['Ogt']['OgtLineUrlSegment']
                date_time = data_line['JourneyDateTime']
                towards = OGTRest.stops_infos(
                    data_line['Ogt']['PassingStops'][-1])[0]
                stop_point = data_line['StopPointAliasFormatted']
                ogt_departures.append(
                    OGTDeparture(name, date_time, towards, stop_point))

        # Return departures
        return ogt_departures
