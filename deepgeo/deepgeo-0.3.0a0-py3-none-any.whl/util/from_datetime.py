import datetime

def from_datetime(date_time):
    tt = datetime.datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
    return int(tt.timestamp())