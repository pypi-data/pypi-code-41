def toYYYYMMDDHHMMSS(str_time:str):
    # 1970-01-01 00:00:00
    datetime_ = str_time.split(' ')
    date = datetime_[0].split('-')
    time = datetime_[1].split(':')
    if int(date[1]) > 12 or int(date[1]) < 1:
        date[1] = "01"
    if int(date[2]) > 31 or int(date[2]) < 1:
        date[2] = "01"
    if int(time[0]) > 24 or int(time[0]) < 0:
        time[0] = "00"
    if int(time[1]) > 60 or int(time[1]) < 0:
        time[1] = "00"
    if int(time[2]) > 60 or int(time[2]) < 0:
        time[2] = "00"
    return date[0]+"-"+date[1]+"-"+date[2]+" "+time[0]+":"+time[1]+":"+time[2]