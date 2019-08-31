"""
MIT License
Copyright (c) 2019 Dextroz
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""
try:
    from requests import get
except ImportError as err:
    print(f"Failed to import required modules: {err}")


class TransportAPI(object):
    """
    Base class for interacting with the TransportAPI (https://www.transportapi.com/)
    """

    def __init__(self, APP_ID=None, API_KEY=None, PROXIES=None):
        self.APP_ID = APP_ID
        self.API_KEY = API_KEY
        self.PROXIES = PROXIES
        self.BASE_URL = "https://transportapi.com/v3"
        self.VERSION = "0.0.1"
        self.HEADERS = {"User-Agent": f"transportapi-python {self.VERSION}"}

        if (APP_ID is None) or (API_KEY is None):
            raise ValueError(
                "An APP_ID and API_KEY is required to interact with the TransportAPI."
            )
    
    @staticmethod
    def _validate_response(response):
        """
        Helper function to validate the response request produced from _make_request().
           :param response: The requests response object.
           :rtype: A dictionary containing the resp_code and JSON response.
        """
        if response.status_code == 200:
            json_resp = response.json()
            return dict(status_code=response.status_code, json_resp=json_resp)
        else:
            return dict(
                status_code=response.status_code,
                error=response.text,
                resp=response.content,
            )

    def _make_request(self, endpoint: str, params: dict):
        """
        Helper function to make the request to the specified endpoint.
        :param endpoint: The API endpoint.
        :param params: The parameters to go along with the request.
        """
        response = get(
            endpoint, params=params, headers=self.HEADERS, proxies=self.PROXIES
        )
        return self._validate_response(response)
    
    def places(self, **kwargs):
        """
        (1 hit) (https://developer.transportapi.com/docs?raml=https://transportapi.com/v3/raml/transportapi.raml##uk_places_json)
        NOTE: The Places endpoint is in alpha testing, and may be subject to change.
        Places are a generic name for various types of geo-located search results which can be retrieved via this single flexible API endpoint. 
        This includes transport stop points for bus, train, tube etc. as well as non-transport related results such as postcodes and names of towns/villages/streets and points of interest.
        :**kwargs: Other optional query parameters. See link above for all options.
        """
        endpoint = f"{self.BASE_URL}/uk/places.json"
        params = {"app_id": f"{self.APP_ID}", "app_key": f"{self.API_KEY}"}
        # Add optional query parameters if any.
        params.update(**kwargs)
        return self._make_request(endpoint, params)


class Train(TransportAPI):
    """
    TransportAPI Train class.
    """

    def train_timetable(self, station_code: str = "LBG", *args, **kwargs):
        """
        (1 hit) (https://developer.transportapi.com/docs?raml=https://transportapi.com/v3/raml/transportapi.raml##uk_train_station_station_code_date_time_timetable_json)
        Timetabled service updates at a given station: departures, arrivals or passes.
        :param station_code: REQUIRED, at least 3 characters. The station code of the station of interest. Example: "LBG".
        :*args:
            1. date: The date of interest in yyyy-mm-dd format. Defaults to today's date if not specified. Example: "2014-11-20".
            2. time: The time of interest in hh:mm format. Defaults to the current time of the request if not specified. Example: "19:45".
        :**kwargs: Other optional query parameters. See link above for all options.
        """
        endpoint = f"{self.BASE_URL}/uk/train/station/{station_code}/{'/'.join(args)}/timetable.json"
        params = {"app_id": f"{self.APP_ID}", "app_key": f"{self.API_KEY}"}
        # Add optional query parameters if any.
        params.update(**kwargs)
        return self._make_request(endpoint, params)

    def train_live(self, station_code: str = "LBG", **kwargs):
        """
        (1 hit) (https://developer.transportapi.com/docs?raml=https://transportapi.com/v3/raml/transportapi.raml##uk_train_station_station_code_live_json)
        Live service updates at a given station: departures, arrivals or passes.
        :param station_code: REQUIRED, at least 3 characters. The station code of the station of interest. Example: "LBG".
        :**kwargs: Other optional query parameters. See link above for all options.
        """
        endpoint = f"{self.BASE_URL}/uk/train/station/{station_code}/live.json"
        params = {"app_id": f"{self.APP_ID}", "app_key": f"{self.API_KEY}"}
        # Add optional query parameters if any.
        params.update(**kwargs)
        return self._make_request(endpoint, params)

    def train_service_timetable(self, service: str = "24614006", *args, **kwargs):
        """
        (1 hit) (https://developer.transportapi.com/docs?raml=https://transportapi.com/v3/raml/transportapi.raml##uk_train_service_service_date_time_timetable_json)
        Timetabled service updates for a given service.
        :param service: REQUIRED. The service reference to the service of interest. Example: "24614006". See link above for more info.
        :*args:
            1. date: The date of interest in yyyy-mm-dd format. Defaults to today's date if not specified. Example: "2014-11-20".
            2. time: The time of interest in hh:mm format. Defaults to current time of the request if not specified. Example: "19:45".
                NOTE: If referencing by train UID, the **time** parameter is not allowed since a train UID and a date uniquely identify a train service.
        :**kwargs: Other optional query parameters. See link above for all options.
        """
        endpoint = f"{self.BASE_URL}/uk/train/service/{service}/{'/'.join(args)}/timetable.json"
        params = {"app_id": f"{self.APP_ID}", "app_key": f"{self.API_KEY}"}
        # Add optional query parameters if any.
        params.update(**kwargs)
        return self._make_request(endpoint, params)


class Bus(TransportAPI):
    """
    TransportAPI Bus class.
    """

    def bus_service_info(self, line: str = "57", operator: str = "SD"):
        """
        (1 hit) (https://developer.transportapi.com/docs?raml=https://transportapi.com/v3/raml/transportapi.raml##uk_bus_services_operator_line_json)
        One particular bus service, identifed by line and operator.
        This method returns information about the service, including the operator, line name and identifiers, and the directions it operates in.
        :param line: REQUIRED. The operator code of the bus you are interested in. Example: "57".
        :param operator: REQUIRED. The bus line you are interested in. Often these are numeric, and we might expect this to be displayed on the front of a bus. Example: "SD".
        """
        endpoint = f"{self.BASE_URL}/uk/bus/services/{operator}:{line}.json"
        params = {"app_id": f"{self.APP_ID}", "app_key": f"{self.API_KEY}"}
        return self._make_request(endpoint, params)

    def bus_live(self, atcocode: str = "490000077E", **kwargs):
        """
        (1 hit / 10 hits) (https://developer.transportapi.com/docs?raml=https://transportapi.com/v3/raml/transportapi.raml##uk_bus_stop_atcocode_live_json)
        Bus departures at a given bus stop.
        Live bus data is not available for all stops. 
        This operation will make use of different live data sources including NextBuses and TfL Countdown, to bring you a consistently formatted response with the best live data available, or fallback to timetable.
        NOTE: NextBuses is a more expensive source and the charge is adjusted to 10 hits per request to reflect this. If you wish to avoid this hit charge and use only the other data sources, add a nextbuses=no kwarg.
        :param atcocode: REQUIRED. The ATCO code of the bus stop of interest. 5-12 characters. Example: "490000077E".
        :**kwargs: Other optional query parameters. See link above for all options.
        """
        endpoint = f"{self.BASE_URL}/uk/bus/stop/{atcocode}/live.json"
        params = {"app_id": f"{self.APP_ID}", "app_key": f"{self.API_KEY}"}
        # Add optional query parameters if any.
        params.update(**kwargs)
        return self._make_request(endpoint, params)

    def bus_stop_timetable(self, atcocode: str = "490000077E", *args, **kwargs):
        """
        (1 hit) (https://developer.transportapi.com/docs?raml=https://transportapi.com/v3/raml/transportapi.raml##uk_bus_stop_atcocode_date_time_timetable_json)
        Bus departures at a given bus stop.
        This method shows what buses are scheduled to be departing from the specified bus stop in the coming hour.
        :param atcocode: REQUIRED. The ATCO code of the bus stop of interest. 5-12 characters. Example: "490000077E".
        :*args:
            1. date: The date of interest in yyyy-mm-dd format. Defaults to today's date if not specified. Example: "2014-11-20".
            2. time: The time of interest in hh:mm format. Defaults to current time of the request if not specified. Example: "19:45".
        :**kwargs: Other optional query parameters. See link above for all options.
        """
        endpoint = (
            f"{self.BASE_URL}/uk/bus/stop/{atcocode}/{'/'.join(args)}/timetable.json"
        )
        # Add optional query parameters if any.
        params = {"app_id": f"{self.APP_ID}", "app_key": f"{self.API_KEY}"}
        # Add optional query parameters if any.
        params.update(**kwargs)
        return self._make_request(endpoint, params)

    def bus_route_timetable(
        self,
        atcocode: str = "450016345",
        direction: str = "inbound",
        line: str = "427",
        operator: str = "WRAY",
        *args,
        **kwargs,
    ):
        """
        (1 hit) (https://developer.transportapi.com/docs?raml=https://transportapi.com/v3/raml/transportapi.raml##uk_bus_route_operator_line_direction_atcocode_date_time_timetable_json)
        The route of one specific bus.
        :param atcocode: REQUIRED. The ATCO code of the bus stop of interest. 5-12 characters. Example: "450016345".
        :param direction: REQUIRED. Whether the direction is 'inbound', 'outbound' or 'clockwise'.
        :param line: REQUIRED. The bus line you are interested in. Example: "427".
        :param operator: REQUIRED. The operator code of the bus you are interested in. Example: "WRAY" (for Arriva Yorkshire).
        :*args:
            1. date: The date of interest in yyyy-mm-dd format. Defaults to today's date if not specified. Example: "2014-11-20".
            2. time: The time of interest in hh:mm format. Defaults to current time of the request if not specified. Example: "19:45".
        :**kwargs: Other optional query parameters. See link above for all options.
        """
        endpoint = f"{self.BASE_URL}/uk/bus/route/{operator}/{line}/{direction}/{atcocode}/{'/'.join(args)}/timetable.json"
        params = {"app_id": f"{self.APP_ID}", "app_key": f"{self.API_KEY}"}
        # Add optional query parameters if any.
        params.update(**kwargs)
        return self._make_request(endpoint, params)


class Public(TransportAPI):
    """
    Transport API Public journey class.
    """

    def plan_journey(self, _from: str = "lonlat:-0.134649,51.529258", to: str = "lonlat:-0.088780,51.506383", **kwargs):
        """
        (10 hits) (https://developer.transportapi.com/docs?raml=https://transportapi.com/v3/raml/transportapi.raml##uk_public_journey_from_from_to_to_json)
        Plans a route between two locations via public transport. Returns a multi-modal journey plan.
        :param from: REQUIRED. The location from which the route starts. Example: "lonlat:-0.134649,51.529258".
        :param to: REQUIRED. The location to which the route leads. Example: "lonlat:-0.088780,51.506383".
        :**kwargs: Other optional query parameters. See link above for all options.
        """
        endpoint = f"{self.BASE_URL}/uk/public/journey/from/{_from}/to/{to}.json"
        params = {"app_id": f"{self.APP_ID}", "app_key": f"{self.API_KEY}"}
        # Add optional query parameters if any.
        params.update(**kwargs)
        return self._make_request(endpoint, params)

    def plan_journey_extra(self, _from: str = "lonlat:-0.134649,51.529258", to: str = "lonlat:-0.088780,51.506383", *args, **kwargs):
        """
        (10 hits) (https://developer.transportapi.com/docs?raml=https://transportapi.com/v3/raml/transportapi.raml##uk_public_journey_from_from_to_to_type_date_time_json)
        Plans a route between two locations via public transport. Returns a multi-modal journey plan.
        This method has extra uri parameters for more specific configuration.
        :param from: REQUIRED. The location from which the route starts. Example: "lonlat:-0.134649,51.529258".
        :param to: REQUIRED. The location to which the route leads. Example: "lonlat:-0.088780,51.506383".
        :*args:
            1. date: The date of interest in yyyy-mm-dd format. Defaults to today's date if not specified. Example: "2014-11-20".
            2. time: The time of interest in hh:mm format. Defaults to current time of the request if not specified. Example: "19:45".
        :**kwargs: Other optional query parameters. See link above for all options.
        """
        endpoint = f"{self.BASE_URL}/uk/public/journey/from/{_from}/to/{to}/at/{'/'.join(args)}.json"
        params = {"app_id": f"{self.APP_ID}", "app_key": f"{self.API_KEY}"}
        # Add optional query parameters if any.
        params.update(**kwargs)
        return self._make_request(endpoint, params)


class Car(TransportAPI):
    """
    Transport API Car class.
    """

    def car_plan_journey(self, _from: str = "lonlat:-0.134649,51.529258", to: str = "lonlat:-0.088780,51.506383"):
        """
        (5 hits) (https://developer.transportapi.com/docs?raml=https://transportapi.com/v3/raml/transportapi.raml##uk_car_journey_from_from_to_to_json)
        Plan a journey by car between two locations.
        :param from: REQUIRED. The location from which the route starts. Example: "lonlat:-0.134649,51.529258".
        :param to: REQUIRED. The location to which the route leads. Example: "lonlat:-0.088780,51.506383".
        """
        endpoint = f"{self.BASE_URL}/uk/car/journey/from/{_from}/to/{to}.json"
        params = {"app_id": f"{self.APP_ID}", "app_key": f"{self.API_KEY}"}
        return self._make_request(endpoint, params)


class Bicycle(TransportAPI):
    """
    Transport API Bicycle class.
    """

    def bicycle_plan_journey(self, _from: str = "lonlat:-0.134649,51.529258", to: str = "lonlat:-0.088780,51.506383"):
        """
        (5 hits) (https://developer.transportapi.com/docs?raml=https://transportapi.com/v3/raml/transportapi.raml##uk_cycle_journey_from_from_to_to_json)
        Plan a journey by bicycle between two locations.
        :param from: REQUIRED. The location from which the route starts. Example: "lonlat:-0.134649,51.529258".
        :param to: REQUIRED. The location to which the route leads. Example: "lonlat:-0.088780,51.506383".
        """
        endpoint = f"{self.BASE_URL}/uk/cycle/journey/from/{_from}/to/{to}.json"
        params = {"app_id": f"{self.APP_ID}", "app_key": f"{self.API_KEY}"}
        return self._make_request(endpoint, params)
