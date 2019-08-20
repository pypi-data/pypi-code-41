#######################################################################
#
#       COPYRIGHT 2008 RHIZA LABS, LLC., ALL RIGHTS RESERVED.
#
# ALL INTELLECTUAL PROPERTY RIGHTS IN THIS PROGRAM ARE OWNED BY RHIZA OR
# MAYA DESIGN
#
# THIS PROGRAM CONTAINS CONFIDENTIAL AND PROPRIETARY INFORMATION OWNED BY
# RHIZA OR MAYA AND MAY NOT BE DISCLOSED TO ANY THIRD PARTY WITHOUT THE PRIOR
# CONSENT OF THE OWNER.  THIS PROGRAM MAY ONLY BE USED IN ACCORDANCE WITH
# THE TERMS  OF THE APPLICABLE LICENSE AGREEMENT FROM RHIZA. THIS LEGEND MAY
# NOT BE REMOVED FROM THIS PROGRAM BY ANY PARTY.
#
# THIS LEGEND AND ANY RHIZA LICENSE DOES NOT APPLY TO ANY OPEN SOURCE
# SOFTWARE THAT MAY BE PROVIDED HEREIN.  THE LICENSE AGREEMENT FOR ANY OPEN
# SOURCE SOFTWARE, INCLUDING WHERE APPLICABLE, THE GNU GENERAL PUBLIC LICENSE
# ("GPL") AND OTHER OPEN SOURCE LICENSE AGREEMENTS, IS LOCATED IN THE SOURCE
# CODE FOR SUCH SOFTWARE.  NOTHING HEREIN SHALL LIMIT YOUR RIGHTS UNDER THE
# TERMS OF ANY APPLICABLE LICENSE FOR OPEN SOURCE SOFTWARE.
#######################################################################
#
# An intial stab at a date package
#
# Date objects store datetime as tuple (rata_die_day, seconds_day)
# Rata Die day 1 in the first day of the year 1.
# leap seconds and papal calendar adjustment are NOT taken into account.
# regular (gregorian) leap days ARE taken into account.
#
# Historical Note: Gregorian calendar begins on Oct15,1582 which immediately
# follows (Julian) Oct4,1582.  Though this was not accepted by all countries
# very soon (notably: Britan/US until 1752).
# see: http://www.tondering.dk/claus/cal/node3.html
#
# If ISO8601 dates begin with the '-' character then the year is taken
# to be negative.  This format is also used in output of dates. This is
# a marginally accepted extension to the ISO8601 spec.  Additionally 
# more than 4 characters are allowed for the year to represent times before
# year -999 and after year 9999.
#
# Intended interface:
#
#  d = date.fromUnix(unix_epoch_seconds)
#  d = date.fromUnix(unix_epoch_seconds, tz=timezone_hour_offset)
#
#  d = date.fromString(iso8601_string)
#  d = date._(iso8601_string)
#
#  iso_string = d.toString()
#  iso_string = d.toString(round_fraction_seconds_to_this)
#
#  unix_date = d.toUnix()
#
#  d.timezone()      # current timezone in hours (None if not set)
#  d.setTimezone(tz) # sets timezone w/o affecting time!
#

## here's some stuff stolen from xml.utils:
## note: parsing of initial '-' is done in code below
from __future__ import absolute_import

import re
import time # for fromUnix()

from MAYA.VIA.uuid import JSON_PREFIX

__date_re = ("(?P<year>\d\d\d+)"
             "(?:(?P<dsep>-|)"
                "(?:(?P<julian>\d\d\d)"
                  "|(?P<month>\d\d)(?:(?P=dsep)(?P<day>\d\d))?))?")
__tzd_re = "(?P<tzd>[-+](?P<tzdhours>\d\d)(?::?(?P<tzdminutes>\d\d))|Z)"
__tzd_rx = re.compile(__tzd_re)
__time_re = ("(?P<hours>\d\d)(?P<tsep>:|)(?P<minutes>\d\d)"
             "(?:(?P=tsep)(?P<seconds>\d\d(?:[.,]\d+)?))?"
             + __tzd_re)
__datetime_re = "%s(?:T%s)?" % (__date_re, __time_re)
datetime_rx = re.compile(__datetime_re)
del re

## end of xml.utils stuff

## ymd/ratadie
##
## Rata Die algorithm adapted from : Peter Baum's Webpage
## <pbaum@capecod.net>
## http://home.capecod.net/~pbaum/
##
def _ymd(RD):
  Z = RD + 306
  H = 100*Z - 25
  A = H // 3652425
  B = A - (A // 4)
  year = (100*B+H) // 36525
  C = B + Z - 365 * year - (year//4)
  month = (5 * C + 456) // 153
  day = C - (0, 31, 61, 92, 122, 153, 184, 214, 245, 275, 306, 337)[month-3]
  if month > 12:
       year +=  1
       month -= 12
  return year,month,day

def _ratadie(x):
  y,m,d = x
  if m < 3: z = y-1
  else: z = y
  f = (306, 337, 0, 31, 61, 92, 122, 153, 184, 214, 245, 275)[m-1]
  return d+f+365*z+z//4-z//100+z//400 - 306

##
## End Rata Die
##
def _hms(s):
  h = int(s//3600)
  s -=  h*3600
  m = int(s//60)
  s -=  m*60  
  return h,m,s

def _daysec(hms):
  return hms[0]*3600+hms[1]*60+hms[2]

# adjust for more time in time part than fits in a day
def _canon(d):
  d0,d1 = d
  if d1 < 0 or d1 >= 86400:
    dy = d1 // 86400
    d0 += int(dy)
    d1 -= dy*86400
  return d0,d1

def _tz_str(timezone=None):
    if timezone == None:
      return "Z"
    else:
        sign = (timezone < 0) and "+" or "-"
        timezone = abs(timezone)
        hours = int(timezone)
        minutes = int(timezone*60) % 60
        return "%c%02d:%02d" % (sign, hours, minutes)

## give me the shortest repr of the fractional part of a positive float < 1
## that is equal to the original
## jas: does anyone know a better way??
def _shortest_f(f,mx=None):
  if mx != None: f = round(f,mx)
  rf = ("%%.%df"%32)%f  #32 should be enough to capture all precision in a longlong
  i = len(rf) - 3
  while 1:
    nf = ("%%.%df"%i)%f
    if float(nf) != f: break
    rf = nf
    i -= 1
  return rf[2:]
    
##
## Public Interface
##
unix_epoch_day = _ratadie((1970,1,1))      
unix_epoch = (unix_epoch_day,0)

class Date(object):
  __slots__ = ('d','tz',)
  def __getstate__(self):
      return self.d,self.tz
  def __setstate__(self,dtz):
      self.d, self.tz = dtz
  def __init__(self,d,tz=None):
    if tz is None and (type(d) == type('') or type(d) == type(u'')):
      dd,tz = Date.stringParse(d)
      self.d = _canon(dd)    # always zulu time
      self.tz = tz   # prefered timezone in hours offset
    elif type(d) != type(()) or len(d) != 2:
      raise Exception("date not 2-ple")
    else:
      self.d = _canon(d)     # always zulu time
      self.tz = tz   # prefered timezone in hours offset
    
  def setTimezone(self,tz=None): self.tz = tz
  
  def timezone(self): return self.tz

  def year(self): return _ymd(self.d[0])[0]
  
  def month(self): return _ymd(self.d[0])[1]
  
  def day(self): return _ymd(self.d[0])[2]

  def ratadie(self): return self.d[0]
  
  def daytime(self): return self.d[1]

  def _implements_date(self):
      return 1

  def toString(self,frac_sec=None):
    dd = list(_ymd(self.d[0]))
    f = '%04d-%02d-%02d'
    if self.d[1] != 0 or self.tz != None:
      dd.extend(_hms(self.d[1]))
      if dd[5] == 0: # avoid secs if we can
        f = '%04d-%02d-%02dT%02d:%02d'
        dd = dd[:-1]
      else:
        f = '%04d-%02d-%02dT%02d:%02d:%02d'
        # avoid fractional secs if we can
        hsecs = dd[5] - int(dd[5])
        dd[5] = int(dd[5])
        if hsecs != 0 and frac_sec != 0:
          f = '%04d-%02d-%02dT%02d:%02d:%02d.%s'
          if frac_sec != None: hsecs=round(hsecs,frac_sec)
          dd.append(_shortest_f(hsecs))
    ret =  (f % tuple(dd))
    if len(dd) < 5: return ret
    return  ret + _tz_str(self.tz)

  def toUnix(self):
    return (self.d[0] - unix_epoch_day)*86400.0 + self.d[1]

  def toDatetime(self):
    """To Python datetime.datetime object, paired with the timezone offset as number of minutes east of UTC"""
    import datetime
    dt = datetime.datetime(*_ymd(self.d[0]))
    seconds = datetime.timedelta(seconds = self.d[1])
    if self.tz is None:
        tz = None
    else:
        tz = round(-60 * self.tz)
    return dt + seconds, tz

  def __repr__(self):
    return "Date_( '"+ self.toString() + "' )"

  def __add__(self,a):
    if hasattr(a,"_implements_date"):
      return Date(_canon((self.d[0]+a.d[0],self.d[1]+a.d[1])))
    raise Exception("cannot add %s to Date" % str(type(a)))

  def __eq__(a,b):
    if not isinstance(b,Date): return False
    return a.d == b.d

  def __gt__(a,b):
    # implies the date is greater than anything that's not a date
    if not isinstance(b,Date): return True  

    return a.d[0] > b.d[0] or (a.d[0] == b.d[0] and a.d[1] > b.d[1])

  def __ge__(a,b):
    return a == b or a > b

  def __ne__(a,b):
    return not (a == b)

  def __lt__(a,b):
    return not (a >= b)

  def __le__(a,b):
    return not (a > b)

  def toJSON(self):
    return {JSON_PREFIX:['Date',self.toString()]}

  @staticmethod
  def stringParse(s):
      
    def __extract_date(m,neg=0):
        year = int(m.group("year"))
        if neg: year = -year
        julian = m.group("julian")
        if julian:
            raise "no support for julian years yet"
        month = m.group("month")
        day = 1
        if month is None:
            month = 1
        else:
            month = int(month)
            if not 1 <= month <= 12:
                raise ValueError, "illegal month number: " + m.group("month")
            else:
                day = m.group("day")
                if day:
                    day = int(day)
                    if not 1 <= day <= 31:
                        raise ValueError, "illegal day number: " + m.group("day")
                else:
                    day = 1
        return year, month, day

    def __extract_time(m):
        if not m:
            return 0, 0, 0
        hours = m.group("hours")
        if not hours:
            return 0, 0, 0
        hours = int(hours)
        if not 0 <= hours <= 23:
            raise ValueError, "illegal hour number: " + m.group("hours")
        minutes = int(m.group("minutes"))
        if not 0 <= minutes <= 59:
            raise ValueError, "illegal minutes number: " + m.group("minutes")
        seconds = m.group("seconds")
        if seconds:
            seconds = float(seconds)
            if not 0 <= seconds <= 60:
                raise ValueError, "illegal seconds number: " + m.group("seconds")
        else:
            seconds = 0
        return hours, minutes, seconds

    def __extract_tzd(m):
        """Return the Time Zone Designator as an offset in hours from UTC."""
        if not m:
            return None
        tzd = m.group("tzd")
        if not tzd:
            return None
        if tzd == "Z":
            return None
        hours = int(m.group("tzdhours"))
        minutes = m.group("tzdminutes")
        if minutes:
            minutes = int(minutes)
        else:
            minutes = 0
        offset = ((hours*60 + minutes) * 60.0) / 3600.0
        if tzd[0] == "+":
            return -offset
        return offset
        
    s1 = s
    neg = s.startswith('-')
    if neg: s1 = s[1:]
    m = datetime_rx.match(s1)
    if m is None or m.group() != s1:
      raise ValueError, "unknown or illegal ISO-8601 date format: " + s
    dd = _canon((_ratadie(__extract_date(m,neg)),_daysec(__extract_time(m))))
    return dd, __extract_tzd(m)

  @staticmethod
  def fromString(s):
    dd, tz = Date.stringParse(s)
    return Date(dd,tz)

  @staticmethod
  def fromUnix(ut=None,tz=None):
    if ut == None: 
      ut = round(time.time(),3) #round unix time to mS
    d = int(ut // 86400)
    ut -= d*86400
    return Date((d + unix_epoch_day, ut),tz)

  @staticmethod
  def fromDatetime(dt = None):
    import datetime
    if dt is None:
      dt = datetime.datetime.utcnow()
    d = _ratadie((dt.year, dt.month, dt.day))
    if isinstance(dt, datetime.datetime):
      t = _daysec([dt.hour, dt.minute, dt.second + (dt.microsecond/1000000.0)])
      if dt.tzinfo:
        delta = dt.tzinfo.utcoffset(dt)
        offset = delta.days * 24 + delta.seconds / 3600.0 + delta.microseconds / 3600000000.0
        tz =  tz = -offset
      else:
        tz = None
    else:
      t = 0
      tz = None
    dd = _canon((d, t))
    return Date(dd, tz)

  @staticmethod
  def isa(u):
    return hasattr(u,"_implements_date")      

      
def fromString(s):
    return Date.fromString(s)

def isa(u):
    return hasattr(u,"_implements_date")

def _(s): return fromString(s)
def Date_(s): return fromString(s)

def fromUnix(ut=None,tz=None):
  return Date.fromUnix(ut,tz)

def fromDatetime(dt = None):
  return Date.fromDatetime(dt)

def test(x):
  d = _(x)
  if d.toString() != x:
    print "Yikes",x,_(d.toString())
