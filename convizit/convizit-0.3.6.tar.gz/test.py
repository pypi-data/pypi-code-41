from convizit import Convizit
from datetime import datetime, timezone


# apiSecret - aCwNkDkLJwDw
# siteToken - e5cfe0690cc2877c9f74043f1de19ace
# apiKey - 4723c81e336abd12ddbe35793b6ca2e1


# Please insert valid production values to authorize:
data_connection = Convizit('e5cfe0690cc2877c9f74043f1de19ace',
                           '4723c81e336abd12ddbe35793b6ca2e1',
                           'aCwNkDkLJwDw')
timestamp_format = '%Y-%m-%d %H:%M:%S'
from_date_time = datetime.strptime('2019-08-02 00:00:00', timestamp_format)
from_date_time_utc = from_date_time.replace(tzinfo=timezone.utc).timestamp()
to_date_time = datetime.strptime('2019-08-21 00:03:00', timestamp_format)
to_date_time_utc = to_date_time.replace(tzinfo=timezone.utc).timestamp()
data_events = data_connection.get_events(fromDateTime=from_date_time_utc, nameContains='upright')
data_elements = data_connection.get_elements()
data_sessions = data_connection.get_sessions()
data_visits = data_connection.get_visits()
data_pages = data_connection.get_pages()
print()
