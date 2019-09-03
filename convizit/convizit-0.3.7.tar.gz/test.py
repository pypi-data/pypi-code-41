from convizit import Convizit
from datetime import datetime, timezone
import pandas as pd

# prod
# apiSecret = 'aCwNkDkLJwDw'
# siteToken = 'e5cfe0690cc2877c9f74043f1de19ace'
# apiKey = '4723c81e336abd12ddbe35793b6ca2e1'

# dev
apiSecret = 'MxRZXuljvMKq'
siteToken = '53e7d98df7d8f6927386bfbf543b67ed'
apiKey = '956e1099ca534a583cd8064e1c145893'


# Please insert valid production values to authorize:
data_connection = Convizit(siteToken,
                           apiKey,
                           apiSecret)
timestamp_format = '%Y-%m-%d %H:%M:%S'
from_date_time = datetime.strptime('2019-08-02 00:00:00', timestamp_format)
from_date_time_utc = from_date_time.replace(tzinfo=timezone.utc).timestamp()
to_date_time = datetime.strptime('2019-08-21 00:03:00', timestamp_format)
to_date_time_utc = to_date_time.replace(tzinfo=timezone.utc).timestamp()
data_events = data_connection.get_events()
data_events_df = pd.DataFrame.from_records(data_events)
data_elements = data_connection.get_elements()
data_elements_df = pd.DataFrame.from_records(data_elements)
data_sessions = data_connection.get_sessions()
data_sessions_df = pd.DataFrame.from_records(data_sessions)
data_visits = data_connection.get_visits()
data_visits_df = pd.DataFrame.from_records(data_visits)
data_pages = data_connection.get_pages()
data_pages_df = pd.DataFrame.from_records(data_pages)
print()
