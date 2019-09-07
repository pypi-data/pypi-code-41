'''
    Conversions between date and time representations
    Brett Hosking 2018

'''
import datetime
from calendar import monthrange
import numpy as np
import pandas as pd
import sys

def ticks(startdate,enddate,starttime=[0,0,0],endtime=[0,0,0],timeticks=False,dayticks=False,monticks=True,yearticks=True):
    '''
        Given a start date and end date, produce monthly and yearly ticks 
        for that period. 

        Parameters
        ----------
        start : list 
            [year,month,day] 
        end : list 
            [year,month,day] 
        Returns 
        -------


    '''
    # convert start and end date - datetime format
    sdatetime   = datetime.datetime(startdate[0],startdate[1],startdate[2],
                    hour=starttime[0],minute=starttime[1],second=starttime[2])
    edatetime     = datetime.datetime(enddate[0],enddate[1],enddate[2],
                    hour=endtime[0],minute=endtime[1],second=endtime[2])

    totsecond   = (edatetime - sdatetime).total_seconds()
    # print("total seconds:", totsecond)

    def diff_month(d1, d2):
        return (d1.year - d2.year) * 12 + d1.month - d2.month

    # Values to return 
    returnvals = []

    # list of months in range 
    months      = np.mod(np.arange(startdate[1], startdate[1] + diff_month(edatetime,sdatetime)+1),12)
    months[months == 0] = 12

    # list of years in range
    years       = np.arange(startdate[0]+1,enddate[0]+1) 

    if timeticks:
        # currently does not allow for timeperiod>3600
        # Determine period of labels 
        if totsecond <=7750:
            timeperiod = 900
        if (totsecond>7750) and (totsecond < 15500):
            timeperiod      = 1800
        elif totsecond >= 15500:
            timeperiod      = 3600
        # timeperiod      = 900#5400#1800

        # delay in seconds from the first valid tick point
        secdelay        = ((starttime[1] * 60) + starttime[2])%timeperiod
        # print('delay: ', secdelay)

        # total number of labels - currently creates an extra tick for the next valid tick point 
        npoints = int(np.floor(totsecond / timeperiod)) + 1 # without this 1 tick will not be created for endtime
        # print('npoints:', npoints)

        # add index for each time 
        if secdelay ==0:
            timindex = [x*timeperiod for x in range(npoints)]
        else:
            timindex = [(timeperiod-secdelay)+(x*timeperiod) for x in range(npoints)]
        # print('timeindex: ', timindex)

        # determine quadrant (time interval) that the starttime corresponds to within the hour
        quadrant    = ((starttime[1] * 60) + starttime[2])//timeperiod
        nquandrants = int(3600/timeperiod)
        # print('quadrant: ', quadrant)
        # print('quadrants: ', nquandrants)

        # create list of minute strings 
        mininterval = 60/(3600/timeperiod)
        # print('min interval: ', mininterval)
        minstrings  = [':' + str(int(mininterval*x)) for x in range(1,nquandrants)]
        minstrings.insert(0,':00')
        # print('minute strings: ', minstrings)

        timlabel = []
        if (nquandrants - quadrant == 1) and (secdelay >0): # in the last quandrant
            hourtick = starttime[0] +1
        else:
            hourtick = starttime[0]

        if secdelay >0:
            quadrant = (quadrant+1) % nquandrants 

        for x in range(npoints):
            timlabel.append( str(hourtick%24) + minstrings[quadrant] )
            # update quadrant 
            quadrant+=1
            if quadrant == nquandrants:
                hourtick+=1
                quadrant=0

        returnvals.append(timlabel)
        returnvals.append(timindex)

    if dayticks: 
        # day/date index - the index (in seconds) where each day/date label is given
        dindex      = []
        dlabel      = []
        # total number of days
        days        = (edatetime - sdatetime).days 
        print("total days: ", days)

        cur_year    = startdate[0]
        cur_mon     = startdate[1]

        # Handle first month separately - may not be a full month 
        if (startdate[1] != enddate[1]) and (startdate[0] == enddate[0]):
            # expands over more than one month in the same year
            daysmonth   =  (datetime.datetime(startdate[0], months[1], 1) - datetime.datetime(startdate[0], months[0], startdate[2])).days
            dlabel.extend(np.arange(startdate[2], startdate[2]+daysmonth))
        elif (startdate[1] == enddate[1]) and (startdate[0] == enddate[0]):
            # within the same month in the same year
            daysmonth   =  (datetime.datetime(startdate[0], months[0], enddate[2]) - datetime.datetime(startdate[0], months[0], startdate[2])).days
            dlabel.extend(np.arange(startdate[2], startdate[2]+daysmonth+1))
        elif (startdate[1] == 12):
            # first month is december (and end date year is not the same) 
            daysmonth   =  (datetime.datetime(years[0], months[1], 1) - datetime.datetime(startdate[0], months[0], startdate[2])).days
            dlabel.extend(np.arange(startdate[2], startdate[2]+daysmonth))
        else:
            sys.exit("tick error")


        # if the starttime does not equal [0,0,0] then we remove the first day
        if starttime != [0,0,0]:    
            del dlabel[0]
            # calculate delay for first complete day index 
            daydelay = 86400 - ((starttime[0]*(60*60)) + (starttime[1]*60) + starttime[2])
        else:
            daydelay = 0
        print('days in first month: :', dlabel)
        print('delay for first day index: ', daydelay)
        print('time past in day: ', (starttime[0]*(60*60)) + (starttime[1]*60) + starttime[2])

        cur_year    = startdate[0]
        cur_mon     = months[0]

        if len(months) >1:
            for m in months[1:]:
                if m < cur_mon:
                    cur_year+=1
                cur_mon=m
                # print cur_year, enddate[0]
                # print m, enddate[1]
                # calculate number of days in month and append list of days 
                if (cur_year == enddate[0]) and (m == enddate[1]):
                    # count days in partial month
                    daysmonth   =  (datetime.datetime(enddate[0], enddate[1], enddate[2]+1) - datetime.datetime(enddate[0], enddate[1], 1)).days
                    # print ('days of the month: ', daysmonth)
                    dlabel.extend(np.arange(1, daysmonth+1))
                else:
                    # count days in full month
                    daysmonth   = monthrange(cur_year, m)[1] 
                    # print ('days of the month: ', daysmonth)
                    dlabel.extend(np.arange(1,daysmonth+1)) # there may be a situation where we don't add 1 here

        

        # add index for each day 
        dindex.extend(np.add(np.multiply(np.arange(len(dlabel)),86400),daydelay))
        
        returnvals.append(dlabel)
        returnvals.append(dindex)

    if monticks:
        mon_labels = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

        # month index - the index (in seconds) where each month label is given
        mindex      = []
        mlabel      = []

        # location of 'month' ticks - if first day and midnight
        if (startdate[2] == 1) and (starttime == [0,0,0]):
            mindex.append(0)
            mlabel.append(mon_labels[(startdate[1]-1)%12])

        cur_year    = startdate[0]
        prev_mon    = months[0]
        for m in months[1:]:
            if m < prev_mon:
                cur_year+=1
            mindex.append( (datetime.datetime(cur_year,m,1) - sdatetime).total_seconds() )
            mlabel.append(mon_labels[m-1])
            prev_mon = m
    
        returnvals.append(mlabel)
        returnvals.append(mindex)

    if yearticks:

        # year index - the index (in seconds) where each year label is given 
        yindex      = []
        ylabel      = []

        # location of 'year' ticks
        if (startdate == [startdate[0],1,1]) and (starttime == [0,0,0]):
            yindex.append(0)
            ylabel.append(str(startdate[0]))

        for y in years:
            yindex.append( (datetime.datetime(y,1,1) - sdatetime).total_seconds() )
            ylabel.append(str(y))
        
        returnvals.append(ylabel)
        returnvals.append(yindex)

    # print(returnvals)
    return returnvals


def ticksfromdata(df):
    '''
        Given the number of samples in each year and month, produce xticks
        and positions

        ### Note 
        This only really works if you use one set of data points
        Ticks should only take into account the start date and end date and then produce
        labels and xpoints for this period
    '''
    mon_labels = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

    # months in each year
    ysamples    = df['year'].value_counts().sort_index()
    years       = list(ysamples.index)
    mlabels = []
    midx = []

    for i in range(len(ysamples)):
        if i == 0:
            unqmon  = df['month'].iloc[0:ysamples.iloc[i]].unique().T
            ylist   = [years[i]]*len(unqmon)
            midx    = np.asarray((ylist, unqmon)).T.astype(int)

        else:
            unqmon  = df['month'].iloc[ysamples.iloc[i-1]:ysamples.iloc[i-1]+ysamples.iloc[i]].unique().T
            ylist   = [years[i]]*len(unqmon)
            arr     = np.asarray((ylist, unqmon)).T.astype(int)
            midx    = np.concatenate((midx,arr), axis=0)

    # for each month index, asign a label
    for m in midx[:,1]:
        mlabels.append(mon_labels[m-1])

    mlocs = []
    mlocs.append(0)
    cloc = 0
    for m in range(1,len(mlabels)):
        # for each month, calculate the number of seconds
        cloc+=(datetime.datetime(midx[m][0],midx[m][1],1)-datetime.datetime(midx[m-1][0],midx[m-1][1],1)).total_seconds()
        mlocs.append(cloc)

    cloc = 0
    ylocs = []
    ylabels = []
    for y in range(1,len(years)):
        # For each year calculate the number of seconds
        if y == 1:
            # start from 1st recorded month
            cloc+=(datetime.datetime(years[y],1,1)-datetime.datetime(midx[0][0],midx[0][1],1)).total_seconds()
        ylocs.append(cloc)
        ylabels.append(years[y])

    return  mlabels,mlocs,ylabels,ylocs


def datasync(Y,X,startdate,enddate, starttime=[0,0,0], endtime=[0,0,0],overlap=0):
    '''
    Takes in Y points and corrsponding X points which are given 
    as the number of seconds since 1970/1/1. Time indices are 
    adjusted based on the startdate and starttime parameters, 
    and the arrays returned only contain values within the 
    specified window between startdate and starttime to enddate
    and endtime. Overlap can be used to return a wider range 
    of samples than in the specified time window, useful for 
    signals that may undergo filtering.
    
    Parameters
    ----------
    Y : array_list 
        datapoints 
    X : corresponding time indices given in seconds passed 
        1970/1/1.
    startdate : list of ints
        [year,month,day]
    enddate : list of ints 
        [year, month, day]
    starttime  : list of ints 
        [hour,minute, second]
    endtime : list of ints 
        [hour, minute, second]
    overlap : in seconds
        extends the window for the samples returned, this may result in 
        negative time indices.

    Returns 
    -------
    Two arrays, Y and X, which are the synchronised Y and X input 
    arrays
    '''
    # Epoch time 1970/1/1
    epoch = datetime.datetime(1970,1,1)
    # specified start time 
    sdatetime   = datetime.datetime(startdate[0],startdate[1],startdate[2],
                    hour=starttime[0],minute=starttime[1],second=starttime[2])
    # specified end time 
    edatetime   = datetime.datetime(enddate[0],enddate[1],enddate[2],
                    hour=endtime[0],minute=endtime[1],second=endtime[2])
    # Seconds past since Epoch time and start time 
    epochelapsed = (sdatetime - epoch).total_seconds()
    # Duration of specified window 
    duration    = (edatetime - sdatetime).total_seconds()
    # Sync X points
    X = np.subtract(X, epochelapsed)
    # get values in the specified time window
    indices     = np.where(np.logical_and(X>=0-overlap, X<=duration+overlap))[0]
    return Y[indices],X[indices],duration


def datetime2arr(date,time):
    '''
        Reformat date of DD/MM/YY to [YY, MM, DD]
        Reformat time of hh:mm:ss to [hh, mm, ss]
    '''
    N               = np.shape(date)[0]
    datetime_arr    = np.array(np.zeros((N,6)))
    for d in range(N):
        datetime_arr[d,:3] = date[d].split('/')[::-1]
        datetime_arr[d,3:] = time[d].split(':')
    return datetime_arr.astype(int)


def dt2pd(date,time,delimiter='/',MODE=0):
    '''
        Reformat date of DD/MM/YY to [YY, MM, DD]
        Reformat time of hh:mm:ss to [hh, mm, ss]

        convert to pandas dataframe
    '''
    df  = pd.DataFrame(columns=[    'year','month','day','hour','minute','second',
                                    'elapsed_1970/1/1','elapsed_sample','elapsed_month'])
    N   = np.shape(date)[0]

    epoch = datetime.datetime(1970,1,1)
    yrlist, mthlist, dylist, hlist, mlist, slist, epochlist = [],[],[],[],[],[],[]
    for i in range(N):
        if MODE==0:
            year,month,day      = date[i].split(delimiter)[::-1]
        if MODE==1:
            year,month,day      = reversed(date[i].split(delimiter)[::-1])
        hour,minute,second  = time[i].split(':')
        yrlist.append(int(year));mthlist.append(int(month));dylist.append(int(day))
        hlist.append(int(hour));mlist.append(int(minute));slist.append(int(second))
        epochlist.append((datetime.datetime(int(year),int(month),int(day),
                                            hour=int(hour),
                                            minute=int(minute),
                                            second=int(second) ) - epoch).total_seconds())

    df['year']      = yrlist
    df['month']     = mthlist
    df['day']       = dylist
    df['hour']      = hlist
    df['minute']    = mlist
    df['second']    = slist

    ## elapsed
    offset = (datetime.datetime(    int(df['year'].iloc[0]),
                                    int(df['month'].iloc[0]),
                                    int(df['day'].iloc[0]),
                                    hour=int(df['hour'].iloc[0]),
                                    minute=int(df['minute'].iloc[0]),
                                    second=int(df['second'].iloc[0])) - datetime.datetime( int(df['year'].iloc[0]),
                                                                                    int(df['month'].iloc[0]),1,
                                                                                    hour=0,
                                                                                    minute=0,
                                                                                    second=0)).total_seconds()

    df['elapsed_1970/1/1']             = epochlist
    df['elapsed_sample']               = np.subtract(epochlist,epochlist[0])
    df['elapsed_month']                = np.add(df['elapsed_sample'],offset)
    return df


def addepoch(df,yearstr='year',monthstr='month',daystr='day'):
    '''
    Takes in a dataframe with:
    year, month, day, hour, minute, second 

    adds epoch elapsed time to dataframe
    '''
    N   = np.shape(df)[0]
    epoch = datetime.datetime(1970,1,1)
    epochlist = []
    for i in range(N):
        try: hour       = df['hour'].iloc[i]
        except: hour    = 0
        try: minute     = df['minute'].iloc[i]
        except: minute  = 0
        try: second     = df['second'].iloc[i]
        except: second  = 0
        epochlist.append((datetime.datetime(int(df[yearstr].iloc[i]),int(df[monthstr].iloc[i]),int(df[daystr].iloc[i]),
                                                hour=int(hour),
                                                minute=int(minute),
                                                second=int(second) ) - epoch).total_seconds())

    ## elapsed
    try: hour       = df['hour'].iloc[0]
    except: hour    = 0
    try: minute     = df['minute'].iloc[0]
    except: minute  = 0
    try: second     = df['second'].iloc[0]
    except: second  = 0
    offset = (datetime.datetime(    int(df[yearstr].iloc[0]),
                                    int(df[monthstr].iloc[0]),
                                    int(df[daystr].iloc[0]),
                                    hour=int(hour),
                                    minute=int(minute),
                                    second=int(second)) - datetime.datetime( int(df[yearstr].iloc[0]),
                                                                        int(df[monthstr].iloc[0]),1,
                                                                        hour=0,
                                                                        minute=0,
                                                                        second=0)).total_seconds()

    df['elapsed_1970']             = epochlist
    df['elapsed_sample']               = np.subtract(epochlist,epochlist[0])
    df['elapsed_month']                = np.add(df['elapsed_sample'],offset)

    return df

def elapsed(date,time,startdate,enddate,starttime=[0,0,0],endtime=[0,0,0],delimiter='/',MODE=0):
    '''
        Number of seconds past date and time given

        Parameters
        ----------
        date : arraylike

        time: arraylike

        Returns
        -------
        time elapsed in seconds

    '''
    N               = np.shape(date)[0]

    sdatetime   = datetime.datetime(startdate[0],startdate[1],startdate[2],
                    hour=starttime[0],minute=starttime[1],second=starttime[2])
    second_arr      = []
    for i in range(N):
        if MODE==0:
            year,month,day      = date[i].split(delimiter)[::-1]
        if MODE==1:
            year,month,day      = reversed(date[i].split(delimiter)[::-1])
        hour,minute,second  = time[i].split(':')
        second_arr.append((datetime.datetime(int(year),int(month),int(day),
                                            hour=int(hour),
                                            minute=int(minute),
                                            second=int(second) ) - sdatetime).total_seconds())

    return second_arr

    
def datetime2epoch(datetime_arr):
    '''
        Convert date and time into seconds past since 1970

        First data point - elapsed time from 1st of the month

        Parameters
        ----------
        datetime_arr : array
            array of shape (N, 6), where N is the number of timestamps with values
            Year, Month, Day, Hour, Minute, Second

        Returns
        -------
        epoch time since 1970

    '''
    N               = np.shape(datetime_arr)[0]
    epochtime       = np.array(np.zeros(N))
    second_arr      = np.array(np.zeros(N))
    epoch = datetime.datetime(1970,1,1)
    offset = (datetime.datetime(    datetime_arr[0][0],
                                    datetime_arr[0][1],
                                    datetime_arr[0][2],
                                    hour=datetime_arr[0][3],
                                    minute=datetime_arr[0][4],
                                    second=datetime_arr[0][5]) - datetime.datetime( datetime_arr[0][0],
                                                                                    datetime_arr[0][1],1,
                                                                                    hour=0,
                                                                                    minute=0,
                                                                                    second=0)).total_seconds()
    for d in range(N):
        epochtime[d] = (datetime.datetime(  datetime_arr[d][0],
                                            datetime_arr[d][1],
                                            datetime_arr[d][2],
                                            hour=datetime_arr[d][3],
                                            minute=datetime_arr[d][4],
                                            second=datetime_arr[d][5]) - epoch).total_seconds()

        second_arr[d] = epochtime[d] - epochtime[0] + offset

    return epochtime,second_arr

##### Do not use ###
def ticks_v0_0_1(startdate,enddate,starttime=[0,0,0],endtime=[0,0,0],timeticks=False,dayticks=False,monticks=True,yearticks=True):
    '''
        Given a start date and end date, produce monthly and yearly ticks 
        for that period. 

        Currently only works for 00:00 hours

        Parameters
        ----------
        start : list 
            [year,month,day] 
        end : list 
            [year,month,day] 
        Returns 
        -------


    '''
    # convert start and end date - datetime format
    sdatetime   = datetime.datetime(startdate[0],startdate[1],startdate[2],
                    hour=starttime[0],minute=starttime[1],second=starttime[2])
    edatetime     = datetime.datetime(enddate[0],enddate[1],enddate[2],
                    hour=endtime[0],minute=endtime[1],second=endtime[2])

    totsecond   = (edatetime - sdatetime).total_seconds()
    print("total seconds:", totsecond)

    def diff_month(d1, d2):
        return (d1.year - d2.year) * 12 + d1.month - d2.month

    # Values to return 
    returnvals = []

    # list of months in range 
    months      = np.mod(np.arange(startdate[1], startdate[1] + diff_month(edatetime,sdatetime)+1),12)
    months[months == 0] = 12

    # list of years in range
    years       = np.arange(startdate[0]+1,enddate[0]+1) 

    if timeticks:
        timindex        = []
        timlabel        = []

        # Determine period of labels 
        # if totsecond < 15500:
        #     timeperiod      = 1800
        # elif totsecond >= 15500:
            # timeperiod      = 3600
        timeperiod      = 1800#1800

        # total number of labels
        npoints = int(totsecond // timeperiod) 
        print('npoints:', npoints)
        # start labels from first time period 


        if ((starttime[2]%(timeperiod/60)) != 0):# and (starttime[1] != 0):
            if (starttime[2] > (timeperiod/60)) or (timeperiod==3600):
                # tick start is before first timeperiod to be labeled 
                intitial_hour   = starttime[0] + 1
            else:
                intitial_hour   = starttime[0]


        # delay in seconds
        secdelay        = (timeperiod - (starttime[1] * 60)) + (60-starttime[2])
        # add index for each time 
        timindex.extend(np.add(np.multiply(np.arange(npoints),timeperiod),secdelay))
        # else:
        # intitial_hour = starttime[0]
        # # add index for each time 
        # timindex.extend(np.multiply(np.arange(npoints),3600))
        
        # Hour interval - 1 every hour, 0.5 every half hour
        # hour_interval = timeperiod/3600

        # time labels
        if timeperiod==3600:
            timlabel          = [ str(int(x%24))+':00' for x in range(intitial_hour,intitial_hour + npoints) ]
        else:
            timlabel            = [str(intitial_hour) + ':' +  str(int(timeperiod/60))]
            prev_minstr = timeperiod/60      
            # number of labels in hour
            nlabelsnhour    = 3600/timeperiod     
            hourlabels = []
            val = intitial_hour
            for x in range(npoints):
                if x%nlabelsnhour==0:
                    val+=1
                minstr  = ((timeperiod/60)+prev_minstr)%60
                prev_minstr = minstr
                if minstr == 0:
                    timlabel.append(str(int(np.floor(val%24)))+':00')
                else:
                    timlabel.append(str(int(np.floor(val%24)))+':' + str(int(minstr)))
                
        # print(timlabel)
        # sys.exit()

        returnvals.append(timlabel)
        returnvals.append(timindex)

    if dayticks: 
        # day/date index - the index (in seconds) where each day/date label is given
        dindex      = []
        dlabel      = []
        # total number of days
        days        = (edatetime - sdatetime).days 

        cur_year    = startdate[0]
        cur_mon     = startdate[1]

        # Handle first month separately - may not be a full month 
        if (startdate[1] != enddate[1]) and (startdate[0] == enddate[0]):
            # expands over more than one month in the same year
            daysmonth   =  (datetime.datetime(startdate[0], months[1], 1) - datetime.datetime(startdate[0], months[0], startdate[2])).days
            dlabel.extend(np.arange(startdate[2], startdate[2]+daysmonth))
        elif (startdate[1] == enddate[1]) and (startdate[0] == enddate[0]):
            # within the same month in the same year
            daysmonth   =  (datetime.datetime(startdate[0], months[0], enddate[2]) - datetime.datetime(startdate[0], months[0], startdate[2])).days
            dlabel.extend(np.arange(startdate[2], startdate[2]+daysmonth+1))
        elif (startdate[1] == 12):
            # first month is december (and end date year is not the same) 
            daysmonth   =  (datetime.datetime(years[0], months[1], 1) - datetime.datetime(startdate[0], months[0], startdate[2])).days
            dlabel.extend(np.arange(startdate[2], startdate[2]+daysmonth))
        else:
            sys.exit("tick error")

        cur_year    = startdate[0]
        cur_mon     = months[0]

        if len(months) >1:
            for m in months[1:]:
                if m < cur_mon:
                    cur_year+=1
                cur_mon=m
                # print cur_year, enddate[0]
                # print m, enddate[1]
                # calculate number of days in month and append list of days 
                if (cur_year == enddate[0]) and (m == enddate[1]):
                    # print "last count"
                    daysmonth   =  (datetime.datetime(enddate[0], enddate[1], enddate[2]+1) - datetime.datetime(enddate[0], enddate[1], 1)).days
                    # print daysmonth
                    dlabel.extend(np.arange(1, daysmonth+1))
                else:
                    # print 'normal count'
                    daysmonth   = monthrange(cur_year, m)[1] 
                    dlabel.extend(np.arange(1,daysmonth))
        

        # add index for each day 
        dindex.extend(np.multiply(np.arange(len(dlabel)),86400))
        
        returnvals.append(dlabel)
        returnvals.append(dindex)

    if monticks:
        mon_labels = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

        

        # month index - the index (in seconds) where each month label is given
        mindex      = []
        mlabel      = []

        # location of 'month' ticks
        if (startdate[2] == 1) and (starttime == [0,0,0]):
            mindex.append(0)
            mlabel.append(mon_labels[(startdate[1]-1)%12])

        cur_year    = startdate[0]
        prev_mon    = months[0]
        for m in months[1:]:
            if m < prev_mon:
                cur_year+=1
            mindex.append( (datetime.datetime(cur_year,m,1) - sdatetime).total_seconds() )
            mlabel.append(mon_labels[m-1])
            prev_mon = m
    
        returnvals.append(mlabel)
        returnvals.append(mindex)

    if yearticks:

        # year index - the index (in seconds) where each year label is given 
        yindex      = []
        ylabel      = []

        # location of 'year' ticks
        if (startdate == [startdate[0],1,1]) and (starttime == [0,0,0]):
            yindex.append(0)
            ylabel.append(str(startdate[0]))

        for y in years:
            yindex.append( (datetime.datetime(y,1,1) - sdatetime).total_seconds() )
            ylabel.append(str(y))
        
        returnvals.append(ylabel)
        returnvals.append(yindex)

    # print(returnvals)
    return returnvals


def datecount0(year,month):
    '''
        Determine the number of samples in each month and year

        Has a bug...

        Returns
        -------
        Two array of shape (nYears,2) and (nMonths,3) which indicate the number
        of samples in each year and month, respectively. The second array also
        indicates the corresponding year in index 0 axis=0
    '''
    # samples in each year
    unique, counts  = np.unique(year, return_counts=True)
    ycount          = np.asarray((unique, counts)).T
    mcount          = []
    for i in range(np.shape(ycount)[0]):
        unique, counts  = np.unique(month[i:ycount[i,1]], return_counts=True)
        yeararr         = [ycount[i,0]]*len(unique)
        if i ==0:
            mcount    = np.asarray((yeararr,unique, counts)).T
        else:
            arr       = np.asarray((yeararr,unique, counts)).T
            mcount    = np.concatenate((mcount,arr), axis=0)

    # print ycount,mcount
    raise NotYetImplented


def ticks0(mcount):
    '''
        Given the number of samples in each year and month, produce xticks
        and positions
    '''
    mon_labels = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

    mlabels =[]
    for x in range(len(mcount)):
        mlabels.append(mon_labels[(mcount[x,1]-1)])

    mlocs = []
    mlocs.append(0)
    cloc = 0
    for m in xrange(1,len(mlabels)-1):
        # for each month, calculate the number of seconds
        cloc+=(datetime.datetime(mcount[m][0],mcount[m][1],1)-datetime.datetime(mcount[m-1][0],mcount[m-1][1],1)).total_seconds()
        mlocs.append(cloc)

    return  mlabels,mlocs


def elapsed0(dfstamp):
    '''
        Given the time stamp, add the elapsed time to dataframe
        Perhaps combine with dt2pd() to reduce for loops

        Very slow...
    '''
    N               = np.shape(dfstamp)[0]
    epochtime       = np.array(np.zeros(N)) # elapsed from 1970/1/1
    epoch = datetime.datetime(1970,1,1)

    offset = (datetime.datetime(    int(dfstamp['year'].iloc[0]),
                                    int(dfstamp['month'].iloc[0]),
                                    int(dfstamp['day'].iloc[0]),
                                    hour=int(dfstamp['hour'].iloc[0]),
                                    minute=int(dfstamp['minute'].iloc[0]),
                                    second=int(dfstamp['second'].iloc[0])) - datetime.datetime( int(dfstamp['year'].iloc[0]),
                                                                                    int(dfstamp['month'].iloc[0]),1,
                                                                                    hour=0,
                                                                                    minute=0,
                                                                                    second=0)).total_seconds()

    for i in range(N):
        epochtime[i] = (datetime.datetime(  int(dfstamp.iloc[i]['year']),
                                            int(dfstamp.iloc[i]['month']),
                                            int(dfstamp.iloc[i]['day']),
                                            hour=int(dfstamp.iloc[i]['hour']),
                                            minute=int(dfstamp.iloc[i]['minute']),
                                            second=int(dfstamp.iloc[i]['second'])) - epoch).total_seconds()

    dfstamp['elapsed_1970/1/1']             = epochtime
    dfstamp['elapsed_sample']               = np.subtract(epochtime,epochtime[0])
    dfstamp['elapsed_month']                = np.add(dfstamp['elapsed_sample'],offset)

    return dfstamp
