

#from .opensprinkler import OpenSprinkler

#__all__ = ['OpenSprinkler']


import logging
import requests
import json
import os
from collections import OrderedDict
from datetime import datetime, timedelta
import pytz

weekDays = ['M','T','W','T','F','S','S']

utc_tz = pytz.timezone('UTC')

logger = logging.getLogger(__name__)

class OpenSprinkler(object):
    """ Class to manage the OpenSprinker device """
    def __init__(self, password=None, hostname=None, defaultstationruntime=600, fulldatarefresh=300, maxretries=5, timeout=10):
        """
        Class initializaton
        """
        self.password = password
        self.hostname = hostname
        self.defaultruntime = defaultstationruntime
        self.fulldatarefresh = fulldatarefresh
        self.retries = maxretries
        self.timeout = timeout

        return

    def getData(self):
        response = self.geturl('ja')
        if not response:
            raise OpSprException('Could not contact OpenSprinkler host')
        #self.lastfullresponse = response.json()
        #print(self.lastfullresponse)

        try:
          api_dict = self.parse_api_data(json.loads(response.text, object_pairs_hook=OrderedDict))
          return api_dict
        except:
          print("error")
          return OrderedDict()

        


    def geturl(self, url='ja', commands=[]):
        """ Get a URL from the password protected opensprinkler page
            Return None on failure
        """
        params = [('pw', self.password)] + commands
        full_url = "http://%s/%s" % (self.hostname, url)
        response = None
        for i in range(0, self.retries):
            try:
                response = requests.get(full_url, params=params,
                                        timeout=self.timeout)
            except requests.exceptions.RequestException as e:
                logger.warning("Request timed out - %d retries left.",
                               self.retries - i - 1)
                logger.debug("Caught exception %s", str(e))
                continue
            if response.status_code == 200:
                break
        logger.debug('Response code: %s', response.status_code)
        #print(response.text)
        return response

    def exec_station(self, action, station_index, seconds):

        if (action == "on"):
            params = [('en', 1),('sid', station_index),('t', seconds)]
        else:
            params = [('en', 0),('sid', station_index)]

        response = self.geturl('cm', params)
        if not response:
            raise OpSprException('Could not contact OpenSprinkler host')

    def exec_program(self, program_index):
        params = [('en', 1),('pid', program_index),('uwt', 1)]
        response = self.geturl('mp', params)
        if not response:
            raise OpSprException('Could not contact OpenSprinkler host')

    def processDurations(self,durations, stations):
      strDurations = ''
      for i in range(0, len(stations)):
        seconds = int(durations[i])
        if (seconds != 0):
          minutes = 0
          hours = 0
          if (seconds >= 60): #minutes
            minutes = int(seconds/60)
            seconds = seconds%60

            if (minutes >= 60): #hour
              hours = int(minutes/60)
              minutes = minutes%60

          if (hours == 0):
              hours = ''
          else:
              hours = str(hours)+"h "
          if (minutes == 0):
              minutes = ''
          else:
              minutes = str(minutes)+"\' "
          if (seconds == 0):
              seconds = ''
          else:
              seconds = str(seconds)+"\'\' "

          strDurations += (stations[i] +" "+hours+minutes+seconds+"| ")
      return (strDurations[:-2])

    def processStarts(self,starts, type):
      strStarts = ''
      if (type == 'Fixed time'):
        for t in starts:
          if (t != -1):
            s_time = datetime.strptime('00:00', '%H:%M')
            s_time_adj = (s_time + timedelta(minutes=t)).strftime("%H:%M")
            strStarts += str(s_time_adj) +" | "
        return (strStarts[:-3])
      else:
        s_time = datetime.strptime('00:00', '%H:%M')
        s_time_adj = (s_time + timedelta(minutes=starts[0])).strftime("%H:%M")
        strStarts += str(s_time_adj) +" | "
        h = round(starts[2]/60)
        if (h == 1):
          strStarts += "every "+str(h) +" hour | "
        else:
          strStarts += "every "+str(h) +" hours | "
        if (starts[1] == 1):
          strStarts += str(starts[1]) +" time"
        else:
          strStarts += str(starts[1]) +" times"
        return (strStarts)

    def processDays(self,d0,d1,type):
      strDays = ''
      if (type == 'WEEKDAYS'):
        i_bin = 7
        for i in range(0, len(d0)-1):
          if (d0[i_bin]=='1'):
            strDays += weekDays[i]
          else:
            strDays += ' - '
          if (i < 6):
            strDays += ' | '
          i_bin-=1
      else:
        if (d1 == 1):
          strDays = '1 day interval'
        else:
          strDays = str(d1)+' days interval'
      return (strDays)

    def processLastRun(self,lrun, stations):
        dictLastRun = OrderedDict()
        dictLastRun['stationIndex'] = lrun[0]
        dictLastRun['station'] = stations[lrun[0]]
        dictLastRun['progIndex'] = lrun[1]
        if(lrun[1]==99):
          dictLastRun['program'] = "Manual run"
        elif(lrun[1]==254):
          dictLastRun['program'] = "Run once prog."
        else:
          dictLastRun['program'] = "Schedule run"

        dictLastRun['duration'] = lrun[2]
        dictLastRun['endtime'] = lrun[3]
        return (dictLastRun)

    def parse_api_data(self,response):

        programs = response['programs']['pd']
        settings = response['settings']
        options = response['options']
        stations = response['stations']
        status = response['status']

        #MAX_SECTORS = int(stations['maxlen'])
        MAX_SECTORS = len(stations['snames'])
        number_of_bytes_segments = int(MAX_SECTORS/8)

        #print("MAX_SECTORS: {}".format(MAX_SECTORS))
        #print("number_of_bytes_segments: {}".format(number_of_bytes_segments))
        i=0
        ignore_rain = [0 for i in range(number_of_bytes_segments)]
        ignore_rain = [0 for i in range(number_of_bytes_segments)]
        disabled = [0 for i in range(number_of_bytes_segments)]
        sequencial = [0 for i in range(number_of_bytes_segments)]
        pump1 = [0 for i in range(number_of_bytes_segments)]
        pump2 = [0 for i in range(number_of_bytes_segments)]
        i=0
        while (i<number_of_bytes_segments):
            #_LOGGER.warning("number_of_bytes_segments: %d - i: %d", number_of_bytes_segments,i)
            ignore_rain[i] = str(bin(stations['ignore_rain'][i]))[2:]
            if (len(ignore_rain[i]) < 8):
                missing = 8-len(ignore_rain[i])
                for j in range(missing):
                    ignore_rain[i] = "0"+ignore_rain[i]


            disabled[i] = str(bin(stations['stn_dis'][i]))[2:]
            if (len(disabled[i]) < 8):
                missing = 8-len(disabled[i])
                for j in range(missing):
                    disabled[i]= "0"+disabled[i]

            sequencial[i] = str(bin(stations['stn_seq'][i]))[2:]
            if (len(sequencial[i]) < 8):
                missing = 8-len(sequencial[i])
                for j in range(missing):
                    sequencial[i] = "0"+sequencial[i]

            pump1[i] = str(bin(stations['masop'][i]))[2:]
            if (len(pump1[i]) < 8):
                missing = 8-len(pump1[i])
                for j in range(missing):
                    pump1[i] = "0"+pump1[i]

            pump2[i] = str(bin(stations['masop2'][i]))[2:]
            if (len(pump2[i]) < 8):
                missing = 8-len(pump2[i])
                for j in range(missing):
                    pump2[i] = "0"+pump2[i]
            #print "i:{} - disabled: {} - ignore_rain: {} - sequencial {}".format(i,disabled,ignore_rain, sequencial)
            i += 1


        #sbits = str(bin(settings['sbits'][0]))[2:]
        #if (len(sbits) < 8):
        #    missing = 8-len(sbits)
        #    for i in range(missing):
        #        sbits = "0"+sbits

        p_status = settings['ps']
        rain_sensor = settings['rs']
        rain_delay = settings['rd']
        rain_delay_time = settings['rdst']

        pump1_index = options['mas']
        pump1_delay_on = options['mton']
        pump1_delay_off = options['mtof']
        pump2_index = options['mas2']
        pump2_delay_on = options['mton2']
        pump2_delay_off = options['mtof2']

        my_dict = OrderedDict()
        my_dict['stations'] = OrderedDict()
        my_dict['pump1_index'] = pump1_index
        my_dict['pump2_index'] = pump2_index

        my_dict['rain_sensor'] = rain_sensor
        my_dict['rain_delay'] = rain_delay
        my_dict['rain_delay_time'] = rain_delay_time
        my_dict['lastrun'] = self.processLastRun(settings['lrun'], stations['snames'])
        my_dict['snames'] = stations['snames']
        i = 0
        i_bin = (7)


        #_LOGGER.warning("disabled: %s - ignore_rain: %s - sequencial %s", disabled,ignore_rain, sequencial)
        #print "disabled: {} - ignore_rain: {} - sequencial {}".format(disabled,ignore_rain, sequencial)

        while (i<MAX_SECTORS):
        #for sta in stations['snames']:
            segment = int(i/8)

            sta = stations['snames'][i]
            settings_dict = OrderedDict()
            #settings_dict.fromkeys(['last_run'])
            #settings_dict = {k:[] for k in ['last_run']}
            settings_dict['name'] = sta
            
            #if (sta == my_dict['lastrun']['station']):
            #  utcTime = datetime.fromtimestamp(my_dict['lastrun']['endtime'], utc_tz)
            #  settings_dict['last_run'] = utcTime.strftime("%d/%m %H:%M")
            #else:
            #  settings_dict['last_run'] = ''

              
            settings_dict['disabled'] = int(disabled[segment][i_bin])
            #_LOGGER.warning("segment:%d - i: %d - settings_dict: %s - int(disabled[segment][i_bin]): %d - disabled[segment]: %s",segment, i, settings_dict['disabled'],int(disabled[segment][i_bin]), disabled[segment])
            settings_dict['ignore_rain'] = int(ignore_rain[segment][i_bin])
            settings_dict['sequencial'] = int(sequencial[segment][i_bin])
            settings_dict['pump1'] = int(pump1[segment][i_bin])
            settings_dict['pump2'] = int(pump2[segment][i_bin])
            #settings_dict['status'] = int(sbits[i_bin])
            settings_dict['status'] = status['sn'][i]
            settings_dict['index'] = i
            settings_dict['p_status'] = p_status[i]
            if ((i+1)==int(pump1_index)):
              settings_dict['pump1_delay_on'] = pump1_delay_on
              settings_dict['pump1_delay_off'] = pump1_delay_off
            elif ((i+1)==int(pump2_index)):
              settings_dict['pump2_delay_on'] = pump2_delay_on
              settings_dict['pump2_delay_off'] = pump2_delay_off

            my_dict['stations'][sta] = settings_dict
            i_bin -= 1
            i += 1
            if (i_bin == -1):
                i_bin = (7)

        i=0
        my_dict['programs'] = OrderedDict()
        #_LOGGER.warning("programs: %s", str(programs))

        for prog in programs:
            settings_dict = OrderedDict()

            days0 = prog[1]
            days1 = prog[2]
            starts = prog[3]
            durations = prog[4]
            name = prog[5]

            flags = str(bin(prog[0]))[2:]
            if (len(flags) < 8):
                missing = 8-len(flags)
                for i in range(missing):
                    flags = "0"+flags

            settings_dict['Enabled'] = flags[7]
            settings_dict['Weather'] = flags[6]
            settings_dict['restrictions'] = flags[5]+str(flags[4])

            if (flags[3]=='0' and flags[2]=='0'):
                settings_dict['weekdays'] = self.processDays(format(days0, '08b'),format(days1, '08b'),'WEEKDAYS')
                settings_dict['schedule_type'] = 'WEEKDAYS'
            else:
                settings_dict['interval'] = self.processDays(days0, days1,'INTERVAL')
                settings_dict['schedule_type'] = 'INTERVAL'

            if (flags[1]=='1'):
                settings_dict['start_type'] = 'Fixed time'
                settings_dict['start_times'] = self.processStarts(starts, 'Fixed time')
            else:
                settings_dict['start_type'] = 'Repeating time'
                settings_dict['interval_times'] = self.processStarts(starts, 'Repeating time')

            settings_dict['water_durations'] = self.processDurations(durations,stations['snames'])

            settings_dict['index'] = i
            settings_dict['name'] = name
            settings_dict['flags'] = flags
            settings_dict['days0'] = days0
            settings_dict['days1'] = days1
            settings_dict['starts'] = starts
            settings_dict['durations'] = durations

            my_dict['programs'][name] = settings_dict
            i += 1

        return my_dict
