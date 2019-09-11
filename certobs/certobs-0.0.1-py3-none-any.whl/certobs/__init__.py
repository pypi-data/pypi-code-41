#!/usr/bin/env python3 

def pointingscan():
    import numpy as np
    from datetime import datetime
    import astropy.units as u
    from astropy.time import Time, TimeDelta, TimezoneInfo
    from astropy.coordinates import SkyCoord, EarthLocation, AltAz, Angle, ITRS
    from astropy.coordinates import get_body, get_moon,  solar_system_ephemeris
    #import matplotlib as mpl
    import matplotlib.pyplot as plt
    #import matplotlib.dates as mdates
    plt.style.use('seaborn')
    #%matplotlib inline
    #import pytz
    
    #Antennaes location
    VIL1 = EarthLocation(lat=Angle('40d26m33.233s'), lon=Angle('-3d57m5.70s'), height=655.150*u.m)
    VIL2 = EarthLocation(lat=Angle('40d26m44.2s'), lon=Angle('-3d57m9.4s'), height=664.80*u.m)
    #VIL2 = EarthLocation(lat=Angle('40d26m33.233'), lon=Angle('-3d57m5.70s'), height=645.0*u.m)
    
    #Timezone definition (BEWARE OF THE SUMMER TIME)
    utc_plus_two_hours = TimezoneInfo(utc_offset=2*u.hour)
    
    #Loading the sources catalogue
    f = open('CERT-Cat.dat', mode='r', encoding='iso-8859-1')
    wid = (10,21,17,9)
    cat = np.genfromtxt(f,usecols = (0,1,2,3), skip_header=3, skip_footer=12,
                        dtype=("U7","U18", float, float),delimiter=wid)
    cata = []
    for i in cat:
        cata.append(i)
        
    ###############################################################################
    
    #Date and time (now)
    nowtime = Time(datetime.utcnow(), scale='utc')
        
    ###############################################################################
    #Select the operation mode
    mode = input("Select the operation mode for the observation: transit/tracking/scanning/tipping curve:\n")
    
    if mode == 'tracking' or mode == 'Tracking' or mode == 'TRACKING':
        #Date and time (Observation)
        otime = [input("Enter the starting time of the observation in the next format: 2010-12-31 00:00:00 (UTC time) \n")]
        obs_time = Time(otime, format='iso', scale='utc')
        #obs_time = obs_time + TimeDelta(3.2,format='sec')   #Corrección Fortran
       ###############################################################################
        
        #Date and time (datetime format)
        #obs_time.format = 'datetime'
        #obs_time.tzinfo = 'utc_plus_two_hour'
        #falta mejorar lo de la zona horaria o bien dejar el input para UTC y a tomar viento
        
        ###############################################################################
        #Solar System Objects (pensar como añadirlos al input de fuente)
        with solar_system_ephemeris.set('builtin'):
            sun =  get_body('sun', obs_time, VIL2)
            moon = get_body('moon', obs_time, VIL2)
            mercury = get_body('mercury', obs_time, VIL2)
            venus = get_body('venus', obs_time, VIL2)
            mars = get_body('mars', obs_time, VIL2)
            jupiter = get_body('jupiter', obs_time, VIL2)
            saturn = get_body('saturn', obs_time, VIL2)
            uranus = get_body('uranus', obs_time, VIL2)
            neptune = get_body('neptune', obs_time, VIL2)
            
    #    solar = [sun, moon, mercury, venus, mars, jupiter, saturn, uranus, neptune]
    #    ss = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune']
    
        solar = [moon, mercury, venus, mars, jupiter, saturn, uranus, neptune]
        ss = ['moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune']
        
        #Radio source name input
        source = input("Enter the name of the radio-source. Press ENTER if the source is neither in the catalogue nor a planet:\n")

        name = []
        ra = []
        dec = []
        #Identifying the source in the loaded catalogue    
        for i, item in enumerate(ss):
            #print("i="+str(i))
            #print("item="+str(item))#caso de que sea planeta
            if source == item:
                name = ss[i]
                ra = solar[i].ra.degree[0]
                dec = solar[i].dec.degree[0]
            else:
                for a, atem in enumerate(cata):
                    #print("a="+str(a))
                    #print("atem="+str(atem))
                    if source == atem[0]:      #caso de que esté en el catálogo
                        name = cata[a][1]
                        ra = cata[a][2]
                        dec = cata[a][3]
        if name == []:
            name = "unknown source"
            ra = float(input("Enter manually the desired right ascension: "))
            dec = float(input("Enter manually the desired declination: "))
        else:
            pass
 
        #Locating the Sun in order to avoid it:
        ra_sun = sun.ra.degree[0]
        dec_sun = sun.dec.degree[0]
        suncoords = SkyCoord(Angle(ra_sun, unit=u.deg), Angle(dec_sun, unit=u.deg), frame='icrs')        

        # Icarus condition
        ra_dif = abs(ra_sun - ra)
        dec_dif =abs(dec_sun - dec)
        if ra_dif < 1.5:
            if dec_dif < 1.5:
                print("WARNING: YOU FLEW TOO CLOSE TO THE SUN!!!!!!!!!!!!!!!!!!!!")
        
        #Equatorial coords of the object
        obj = SkyCoord(Angle(ra, unit=u.deg), Angle(dec, unit=u.deg), frame='icrs')
        #Taking precession into account: ITRS conversion
        obj_itrs = obj.transform_to(ITRS(obstime=obs_time))
        # Calculate local apparent Hour Angle (HA), wrap at 0/24h
        local_ha = VIL2.lon - obj_itrs.spherical.lon
        local_ha.wrap_at(24*u.hourangle, inplace=True)
        # Calculate local apparent Declination
        local_dec = obj_itrs.spherical.lat
        print("Local apparent HA, Dec={} {}".format(local_ha.to_string(unit=u.hourangle,
              sep=':'), local_dec.to_string(unit=u.deg, sep=':', alwayssign=True) ))
        
        
        
        #In case the source is not in the catalogue you can input it manually:
        #if source not in enumerate(cat):
        #    obj = SkyCoord(Angle(input("Enter its right ascension (in degrees): \n"), unit=u.deg),
        #               Angle(input("Enter its declination (in degrees, negative for W): \n"), unit=u.deg),
        #               frame='icrs')
        ###############################################################################
        #
        duration = float(input("Enter the duration of the observation, in minutes: "))
        
        #La esfera celeste gira unos 15' cada minuto. La anchura del beam es 37'
        #frequency = float(input("Enter the frequency of the pointings, in times per minute (between 1 and 60): "))
        dt = float(input("Enter the time interval between two consecutive pointings (in seconds): "))
        
        #Number of pointings
        #pointings = duration*frequency
        pointings = duration*60/dt
        
        #dt = (60./frequency)
        dt2 = TimeDelta(dt,format='sec')
        
        suc = np.linspace(0.,pointings,pointings+1)
        t = obs_time[0] + dt2 * suc
        
        #Pre-pointing time and post-pointing time:
        pre = TimeDelta(300,format='sec')
        t0 = obs_time[0] - pre
        tf = obs_time[0] + pre
        
        #Coordinates conversion
        completecoords = []
        time = []
        alti = []
        azi = []
        for i in suc.astype(int):
        #    print(t[i])
            new = obj.transform_to(AltAz(obstime=t[i],location=VIL2))
            alt_i = new.alt.degree
            az_i = new.az.degree
            alti.append(alt_i)
            azi.append(az_i)

            time.append(t[i].isot)
            cco = time[i], alti[i], azi[i]  #including time
            completecoords.append(cco) #with time
        
        #We must avoid non-visible objects at the observing times
        for i in suc.astype(int):
            if completecoords[i][1] < 10:
                completecoords[i] = np.ma.masked
                print("Object non visible at the " + str(i) +"position of the observation")
                
        #Atmospheric refreaction correction, supposing a simple model based on gb.nrao
        #where: delta(elev)=(n0-1)*Cot(elev+(4.7/(2.24+elev)))
        #T = float(input("Enter the temperature (ºC): "))     #Temperature
        r = []
        elev = []
        n0 = 1.00031 #Considering the worst refraction index possible at surface level
        for i in suc.astype(int):
            #P = 950 #Atmospheric pressure (mbar)
            p = np.deg2rad(alti[i]+4.7/(2.24+alti[i]))
            r.append((n0-1)*1/(np.tan(p)))
            elev.append(alti[i] + r[i])
            #elev.append(alti[i])
        
        #Required output format: isot
        t.format = "isot"
        t0 = t0.isot
        
        #We create a 'tt' column for the pointing times
        tt = []
        for i in time:
            tt.append([i])
        
        #We put together the time column  and the two coordinates columns
        #(coordlist not used anymore)
        elev = np.around(elev, decimals=4)
        azi = np.around(azi, decimals=4)
        final = np.column_stack((time,azi,elev))
        r0 = np.column_stack((t0, azi[0], elev[0]))    #incluimos el apuntado 0
        rf = np.column_stack((tf, azi[-1], elev[-1]))   #y el apuntado final
        final = np.vstack((r0,final,rf))
        
        final = np.hstack((final,np.zeros((final.shape[0],10))))
        
        #We generate the header for the output file
        header = (
        '<FILE>'
        '\n<HEADER>'
        '\nGENERATION DATE       : '+ str(nowtime) + 
        '\nANTENNA               : VIL-2' 
        '\nLATITUDE              : 40d26m44.2s' 
        '\nLONGITUDE             : -3d57m9.4s' 
        '\nHEIGHT            [KM]: 0.6648' 
        '\nTARGET                : '+ str(source) + 
        '\nTRAJECTORY DATA SOURCE: CESAR/JPL'
        '\nS -DL-FREQUENCY  [MHZ]: 2277.000'
        '\nX -DL-FREQUENCY  [MHZ]: 0.000'
        '\nKA-DL-FREQUENCY  [MHZ]: 0.000'
        '\nANALYSIS PERIOD-START : '+ str(obs_time[0]) + 
        '\nANALYSIS PERIOD-END   : '+ str(obs_time[-1]) +
        '\nNUMBER OF PASSES      : 2'
        '\n</HEADER>'
        '\n<PASS>\n'
        + str(obs_time[0]) + '  ' + str(obs_time[-1]) +
        '\n<ZPASS>'
        '\n</ZPASS>'
        '\n<WRAP>'
        '\n</WRAP>'
        '\n<INIT_TRAVEL_RANGE>'
        '\n<LOWER/>'
        '\n</INIT_TRAVEL_RANGE>'
        '\n   Date - Time        AZ (Deg) EL (Deg) TxRx dXEl (deg) TxRx dEl (deg)  Range (km) Range Rate (km/s)    S-Dop (Hz)      X-Dop (Hz)      Ka-Dop(Hz)      S-EIRP(dBw)     X-EIRP(dBW)     Ka-EIRP(dBW)'
        '\n-------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        
        obs_time.out_subfmt = 'date'
        np.savetxt('datos/track-'+str(name)+str(obs_time[0])+'.txt',final, fmt="%s",
                   delimiter=" ", header=header, footer='</PASS>\n</FILE>', comments='')
    
        obs_time.out_subfmt = 'date_hms'
    
    elif mode == 'transit' or mode == 'Transit' or mode == 'TRANSIT':      
        #Date and time (Observation)
        otime = [input("Enter the starting time of the observation in the next format: 2010-12-31 00:00:00 (UTC time) \n")]
        obs_time = Time(otime, format='iso', scale='utc')
        #obs_time = obs_time + TimeDelta(3.2,format='sec')   #Corrección Fortran
        ###############################################################################
        
        #Date and time (datetime format)
        #obs_time.format = 'datetime'
        #obs_time.tzinfo = 'utc_plus_two_hour'
        #falta mejorar lo de la zona horaria o bien dejar el input para UTC y a tomar viento
        
        ###############################################################################
        #Solar System Objects (pensar como añadirlos al input de fuente)
        with solar_system_ephemeris.set('builtin'):
    #       sun =  get_body('sun', obs_time, VIL2)
            moon = get_body('moon', obs_time, VIL2)
            mercury = get_body('mercury', obs_time, VIL2)
            venus = get_body('venus', obs_time, VIL2)
            mars = get_body('mars', obs_time, VIL2)
            jupiter = get_body('jupiter', obs_time, VIL2)
            saturn = get_body('saturn', obs_time, VIL2)
            uranus = get_body('uranus', obs_time, VIL2)
            neptune = get_body('neptune', obs_time, VIL2)
            
    #    solar = [sun, moon, mercury, venus, mars, jupiter, saturn, uranus, neptune]
    #    ss = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune']
    
        solar = [moon, mercury, venus, mars, jupiter, saturn, uranus, neptune]
        ss = ['moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune']
        
        #Radio source name input
        source = input("Enter the name of the radio-source. Press ENTER if the source is neither in the catalogue nor a planet:\n")

        name = []
        ra = []
        dec = []
        #Identifying the source in the loaded catalogue    
        for i, item in enumerate(ss):
            #print("i="+str(i))
            #print("item="+str(item))#caso de que sea planeta
            if source == item:
                name = ss[i]
                ra = solar[i].ra.degree[0]
                dec = solar[i].dec.degree[0]
            else:
                for a, atem in enumerate(cata):
                    #print("a="+str(a))
                    #print("atem="+str(atem))
                    if source == atem[0]:      #caso de que esté en el catálogo
                        name = cata[a][1]
                        ra = cata[a][2]
                        dec = cata[a][3]
        if name == []:
            name = "unknown source"
            ra = float(input("Enter manually the desired right ascension: "))
            dec = float(input("Enter manually the desired declination: "))
        else:
            pass
        
        #Equatorial coords of the object
        obj = SkyCoord(Angle(ra, unit=u.deg), Angle(dec, unit=u.deg), frame='icrs')
        
        #Taking precession into account: ITRS conversion
        obj_itrs = obj.transform_to(ITRS(obstime=obs_time))
        # Calculate local apparent Hour Angle (HA), wrap at 0/24h
        local_ha = VIL2.lon - obj_itrs.spherical.lon
        local_ha.wrap_at(24*u.hourangle, inplace=True)
        # Calculate local apparent Declination
        local_dec = obj_itrs.spherical.lat
        print("Local apparent HA, Dec={} {}".format(local_ha.to_string(unit=u.hourangle,
              sep=':'), local_dec.to_string(unit=u.deg, sep=':', alwayssign=True) ))
        
        #In case the source is not in the catalogue you can input it manually:
        #if source not in enumerate(cat):
        #    obj = SkyCoord(Angle(input("Enter its right ascension (in degrees): \n"), unit=u.deg),
        #               Angle(input("Enter its declination (in degrees, negative for W): \n"), unit=u.deg),
        #               frame='icrs')
        ###############################################################################
        #
        duration = float(input("Enter the duration of the transit, in minutes: "))

        t = obs_time[0]
        
        
        #Pre-pointing time:
        pre = TimeDelta(300,format='sec')
        dur = TimeDelta(duration*60,format='sec')
        t0 = t - pre
        obs_time_end = t + dur

        #Coordinates conversion
        completecoords = []
        time = []
        
        #for i in suc.astype(int):
        #    print(t[i])
        new = obj.transform_to(AltAz(obstime=t,location=VIL2))
        alti = new.alt.degree
        azi = new.az.degree
        completecoords = t.isot, azi, alti  #with time
        
        #We must avoid non-visible objects at the observing times
        if alti < 10:
                completecoords = np.ma.masked
                print("Too low pointing")
                
        #Atmospheric refreaction correction, supposing a simple model based on gb.nrao
        #where: delta(elev)=(n0-1)*Cot(elev+(4.7/(2.24+elev)))
        #T = float(input("Enter the temperature (ºC): "))     #Temperature
        r = []
        elev = []
        n0 = 1.00031 #Considering the worst refraction index possible at surface level
        p = np.deg2rad(alti+4.7/(2.24+alti))
        r = ((n0-1)*1/(np.tan(p)))
        elev = [alti + r]
        
        # No zenith tracking warning:
        max_elev = 85   #maximum elevation allowed
        if max(elev) > max_elev:
            print("DANGER: TOO HIGH ELEVATION. THERE MIGHT BE TRACKING ISSUES")

        #Required output format: isot
        t.format = "isot"
        t0 = t0.isot
        
        #We create a 'tt' column for the pointing times
        tt = []
        for i in time:
            tt.append([i])
        
        #We put together the time column  and the two coordinates columns
        #(coordlist not used anymore)
        elev = np.around(elev, decimals=4)
        azi = np.around(azi, decimals=4)
        #final = np.column_stack((t.isot,azi,elev))
        r0 = np.column_stack((t0, azi, elev))
        #incluimos el apuntado 0
        final = np.vstack((r0))
        
        final = np.hstack((final,np.zeros((final.shape[0],10))))
        
        #We generate the header for the output file
        header = (
        '<FILE>'
        '\n<HEADER>'
        '\nGENERATION DATE       : '+ str(nowtime) + 
        '\nANTENNA               : VIL-2' 
        '\nLATITUDE              : 40d26m44.2s' 
        '\nLONGITUDE             : -3d57m9.4s' 
        '\nHEIGHT            [KM]: 0.6648' 
        '\nTARGET                : '+ str(source) + 
        '\nTRAJECTORY DATA SOURCE: CESAR/JPL'
        '\nS -DL-FREQUENCY  [MHZ]: 2277.000'
        '\nX -DL-FREQUENCY  [MHZ]: 0.000'
        '\nKA-DL-FREQUENCY  [MHZ]: 0.000'
        '\nANALYSIS PERIOD-START : '+ str(obs_time[0]) + 
        '\nANALYSIS PERIOD-END   : '+ str(obs_time_end) +
        '\nNUMBER OF PASSES      : 2'
        '\n</HEADER>'
        '\n<PASS>\n'
        + str(obs_time[0]) + '  ' + str(obs_time_end) +
        '\n<ZPASS>'
        '\n</ZPASS>'
        '\n<WRAP>'
        '\n</WRAP>'
        '\n<INIT_TRAVEL_RANGE>'
        '\n<LOWER/>'
        '\n</INIT_TRAVEL_RANGE>'
        '\n   Date - Time        AZ (Deg) EL (Deg) TxRx dXEl (deg) TxRx dEl (deg)  Range (km) Range Rate (km/s)    S-Dop (Hz)      X-Dop (Hz)      Ka-Dop(Hz)      S-EIRP(dBw)     X-EIRP(dBW)     Ka-EIRP(dBW)'
        '\n-------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        
        obs_time.out_subfmt = 'date'
        np.savetxt('datos/transit-'+str(name)+str(obs_time[0])+'.txt',final, fmt="%s",
                   delimiter=" ", header=header, footer='</PASS>\n</FILE>', comments='')
    
        obs_time.out_subfmt = 'date_hms'    
    
        
    elif mode == 'tipping curve' or mode == 'tipping' or mode == 'tip' or mode == 'TIPPING' or mode == 'TIP' or mode == 'Tipping':
        #Date and time (Observation)
        otime = [input("Enter the starting time of the observation in the next format: 2010-12-31 00:00:00 (UTC time) \n")]
        obs_time = Time(otime, format='iso', scale='utc')
        #obs_time = obs_time + TimeDelta(3.2,format='sec')   #Corrección Fortran
       ###############################################################################
        # Coordinates input        

        dt = 2 #suponiendo que tarde 2 segundos en hacer una medida
        dt2 = TimeDelta(dt,format='sec')
        #Pre-pointing time:
        pre = TimeDelta(300,format='sec')
        
        t0 = obs_time[0] - pre

        suc = np.linspace(0,90,91)
        t = list()
        t.append(obs_time[0])
        for i, tex in enumerate(suc):
            if i > 0:
                t.append(t[i-1]+dt2)
        
        azimuth = float(input("Enter the azimuth for the tipping curve: "))
        #Atmospheric refreaction correction, supposing a simple model based on gb.nrao
        #where: delta(elev)=(n0-1)*Cot(elev+(4.7/(2.24+elev)))
        #T = float(input("Enter the temperature (ºC): "))     #Temperature
        elev = []
        azi = []
        for i,tex in enumerate(suc):
            elev.append(tex)
            azi.append(azimuth)
            #elev.append(alti[i])
            
        #Coordinates conversion, taking time pass into account
        completecoords = []
        
        for i,tex in enumerate(suc):    #equivalent to "for i in ccc.flatten():"
            cco = t[i].isot, elev[i], azi[i] #including time
            completecoords.append(cco) 
        
        #Required output format: isot
        for i, tex in enumerate(t):
            t[i].format = "isot"
            
        t0 = t0.isot
        duration = t[-1] - t[0]
        
        #We put together the time column  and the two coordinates columns
        #(coordlist not used anymore)
        final = []
        final = np.column_stack((t,azi,elev))
        r0 = (t0, azi[0], elev[0])
        
        final = np.vstack((r0,final))
        final = np.hstack((final,np.zeros((final.shape[0],10))))
        
        #We generate the header for the output file
        header = (
        '<FILE>'
        '\n<HEADER>'
        '\nGENERATION DATE       : '+ str(nowtime) + 
        '\nANTENNA               : VIL-2' 
        '\nLATITUDE              : 40d26m44.2s' 
        '\nLONGITUDE             : -3d57m9.4s' 
        '\nHEIGHT            [KM]: 0.6648' 
        '\nTARGET                : TIPPING CURVE' 
        '\nTRAJECTORY DATA SOURCE: CESAR/JPL'
        '\nS -DL-FREQUENCY  [MHZ]: 2277.000'
        '\nX -DL-FREQUENCY  [MHZ]: 0.000'
        '\nKA-DL-FREQUENCY  [MHZ]: 0.000'
        '\nANALYSIS PERIOD-START : '+ str(obs_time[0]) + 
        '\nANALYSIS PERIOD-END   : '+ str(obs_time[-1]) +
        '\nNUMBER OF PASSES      : 2'
        '\n</HEADER>'
        '\n<PASS>\n'
        + str(obs_time[0]) + '  ' + str(obs_time[-1]) +
        '\n<ZPASS>'
        '\n</ZPASS>'
        '\n<WRAP>'
        '\n</WRAP>'
        '\n<INIT_TRAVEL_RANGE>'
        '\n<LOWER/>'
        '\n</INIT_TRAVEL_RANGE>'
        '\n   Date - Time        AZ (Deg) EL (Deg) TxRx dXEl (deg) TxRx dEl (deg)  Range (km) Range Rate (km/s)    S-Dop (Hz)      X-Dop (Hz)      Ka-Dop(Hz)      S-EIRP(dBw)     X-EIRP(dBW)     Ka-EIRP(dBW)'
        '\n-------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        
        obs_time.out_subfmt = 'date'
        np.savetxt('datos/tip-'+str(nowtime)+'.txt',final, fmt="%s",
                   delimiter=" ", header=header, footer='</PASS>\n</FILE>', comments='')
    
        obs_time.out_subfmt = 'date_hms'
    
    elif mode == 'scanning' or mode == 'Scanning' or mode == 'SCANNING' or mode == 'SCAN' or mode == 'scan':
        #Date and time (Observation)
        otime = [input("Enter the starting time of the observation in the next format: 2010-12-31 00:00:00 (UTC time) \n")]
        obs_time = Time(otime, format='iso', scale='utc')
        #obs_time = obs_time + TimeDelta(3.2,format='sec')   #Corrección Fortran
       ###############################################################################
        
        #Date and time (datetime format)
        #obs_time.format = 'datetime'
        #obs_time.tzinfo = 'utc_plus_two_hour'
        #falta mejorar lo de la zona horaria o bien dejar el input para UTC y a tomar viento
        
        ###############################################################################
        #Solar System Objects (pensar como añadirlos al input de fuente)
        with solar_system_ephemeris.set('builtin'):
            sun =  get_body('sun', obs_time, VIL2)
            moon = get_body('moon', obs_time, VIL2)
            mercury = get_body('mercury', obs_time, VIL2)
            venus = get_body('venus', obs_time, VIL2)
            mars = get_body('mars', obs_time, VIL2)
            jupiter = get_body('jupiter', obs_time, VIL2)
            saturn = get_body('saturn', obs_time, VIL2)
            uranus = get_body('uranus', obs_time, VIL2)
            neptune = get_body('neptune', obs_time, VIL2)
            
    #    solar = [sun, moon, mercury, venus, mars, jupiter, saturn, uranus, neptune]
    #    ss = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune']
    
                # Coordinates input
        ra1 = float(input("Enter manually the right ascension for the first observing point: "))
        dec1 = float(input("Enter manually the declination for the first observing point: "))
        ra2 = float(input("Enter manually the right ascension for the last observing point: "))  
        dec2 = float(input("Enter manually the declination for the last observing point: "))
        
        dra = 0.308
        ddec = 0.308
        deltara = ra2 - ra1
        
        nra = int(np.around(abs(deltara/dra)+1,decimals=0))
        #incra = SkyCoord(Angle(dra, unit=u.deg), Angle(dec1, unit=u.deg), frame='icrs')
        deltadec = dec2 - dec1
        ndec = int(np.around(abs(deltadec/ddec)+1,decimals=0))
        #incdec = SkyCoord(Angle(ra1, unit=u.deg), Angle(ddec, unit=u.deg), frame='icrs')
        
        #Locating the Sun in order to avoid it:
        ra_sun = sun.ra.degree[0]
        dec_sun = sun.dec.degree[0]
        suncoords = SkyCoord(Angle(ra_sun, unit=u.deg), Angle(dec_sun, unit=u.deg), frame='icrs')        

        # Icarus condition
        ra_dif = abs(ra_sun - ra1)
        dec_dif = abs(dec_sun - dec1)
        if ra_dif < 1.5:
            if dec_dif < 1.5:
                print("WARNING: YOU FLEW TOO CLOSE TO THE SUN!!!!!!!!!!!!!!!!!!!!")
        
        nnra = np.linspace(0,nra-1,nra)
        nndec = np.linspace(0,ndec-1,ndec)
        
        ra = []
        dec = []
        for i in nnra:
            ra.append(ra1 + dra * i)
        for i in nndec:
            dec.append(dec1 + ddec * i)
        
        ccc = np.zeros((nra,ndec),dtype=object)
        for i in nnra.astype(int):
            for j in nndec.astype(int):
                ccc[i][j] = SkyCoord(Angle(ra[i],unit=u.deg), Angle(dec[j], unit=u.deg), frame='icrs')
                
        #INTRODUCIR CADA NRA SALTOS UN SALTO TEMPORAL MÁS GRANDE PARA DAR TIEMPO A LA ANTENA A QUE
        #APUNTE CORRECTAMENTE. HACERLO ANTES O DESPUÉS DE QUE GENERE t[i].
        
        
        #Hacer lo mismo para el paso en declinación, pero tiene que estar en un bucle para cada 
        # ascensión recta (o quizá más bien al revés)
        #nn2 = np.linspace(0,nra,nra+1)
        #ra2 = []
        #for i in nn2.astype(int):
        #    rac2 = SkyCoord(Angle(ra[a],unit=u.deg), Angle(dec1+ddec*i, unit=u.deg), frame='icrs')
        #    ra2.append(rac2)
        
        #Number of pointings
        #pointings = duration*frequency
        dt = 2 #suponiendo que tarde 2 segundos en hacer una medida
        dt2 = TimeDelta(dt,format='sec')
        pointings = nra*ndec
        #Pre-pointing time:
        pre = TimeDelta(300,format='sec')
        
        t0 = obs_time[0] - pre

        suc = np.linspace(0.,pointings,pointings+1)
        t = list()
        t.append(t0)
        t.append(obs_time[0])
        dt3 = np.sqrt((deltara/3)**2+(deltadec/3)**2)
        dt3 = TimeDelta(dt3,format='sec')
        
        for i, tex in enumerate(suc):
            if i > 1:
                if (i-1)%nra!=0:
                    t.append(t[i-1]+dt2)
                else:
                    t.append(t[i-1]+dt3)
        
        #Coordinates conversion, taking time pass into account
        completecoords = []
        time = []
        ccc_f = ccc.flatten()
        ccc_n = np.zeros((np.shape(ccc_f)),dtype=object)
        
        for i,tex in enumerate(ccc_f):    #equivalent to "for i in ccc.flatten():"
            ccc_n[i] = ccc_f[i].transform_to(AltAz(obstime=t[i],location=VIL2))
            #cccn = np.reshape(ccc_n,(np.shape(ccc)))
            cco = t[i].isot, ccc_n[i].alt.degree, ccc_n[i].az.degree #including time
            ccl = list(cco)
            completecoords.append(ccl) 
            
        completecoords[0][1] = completecoords[1][1]
        completecoords[0][2] = completecoords[1][2]
        #Graficamos el escaneo, tanto en coordenadas ecuatoriales como en las horizontales
        figure, (ax, ay) = plt.subplots(2,1,figsize=(18,18))
    
        #Mapeo del scanning en coordenadas ecuatoriales (ax) y horizontales (ay):
        if pointings > 500: 
            for i, tex in enumerate(ccc_f):
                if i%100==0:
                        ax.annotate(i, (ccc_f[i].ra.deg, ccc_f[i].dec.deg))
                        ax.set_xlabel('Right Ascension (deg)')          
                        ax.set_ylabel('Declination (deg)')
                        ax.scatter(ccc_f[i].ra.deg,ccc_f[i].dec.deg, s=12000, alpha=0.35)
                        ay.annotate(i, (ccc_n[i].az.deg, ccc_n[i].alt.deg))
                        ay.set_xlabel('Azimuth (deg)')
                        ay.set_ylabel('Elevation (deg)')
                        ay.scatter(ccc_n[i].az.deg, ccc_n[i].alt.deg, s=12000, alpha=0.35)
        else:
            for i, tex in enumerate(ccc_f):
                ax.annotate(i, (ccc_f[i].ra.deg, ccc_f[i].dec.deg))
                ax.set_xlabel('Right Ascension (deg)')          
                ax.set_ylabel('Declination (deg)')
                ax.scatter(ccc_f[i].ra.deg,ccc_f[i].dec.deg, s=12000, alpha=0.35)
                ay.annotate(i, (ccc_n[i].az.deg, ccc_n[i].alt.deg))
                ay.set_xlabel('Azimuth (deg)')
                ay.set_ylabel('Elevation (deg)')
                ay.scatter(ccc_n[i].az.deg, ccc_n[i].alt.deg, s=12000, alpha=0.35)
            
        # (lo suyo sería un movimiento en zig-zag)
                    
        #We must avoid non-visible objects at the observing times
        for i, tex in enumerate(ccc_f):
            if completecoords[i][1] < 10:
                completecoords[i] = np.ma.masked
                print("Too low scanning position")
                
        #Atmospheric refreaction correction, supposing a simple model based on gb.nrao
        #where: delta(elev)=(n0-1)*Cot(elev+(4.7/(2.24+elev)))
        #T = float(input("Enter the temperature (ºC): "))     #Temperature
        r = []
        elev = []
        azi = []
        n0 = 1.00031 #Considering the worst refraction index possible at surface level
        for i,tex in enumerate(ccc_f):
            #P = 950 #Atmospheric pressure (mbar)
            p = np.deg2rad(ccc_n[i].alt.deg+4.7/(2.24+ccc_n[i].alt.deg))
            r.append((n0-1)*1/(np.tan(p)))
            elev.append(ccc_n[i].alt.deg + r[i])
            azi.append(ccc_n[i].az.deg)
            #elev.append(alti[i])
        
        azi.insert(0,azi[0])
        elev.insert(0,elev[0])
        #Required output format: isot
        for i, tex in enumerate(t):
            t[i].format = "isot"
            
        #t0 = t0.isot
        duration = t[-1] - t[0]
                
        #We put together the time column  and the two coordinates columns
        #(coordlist not used anymore)
        elev = np.around(elev, decimals=4)
        azi = np.around(azi, decimals=4)
        final = np.column_stack((t,azi,elev))
        final = np.hstack((final,np.zeros((final.shape[0],10))))
        
        #We generate the header for the output file
        header = (
        '<FILE>'
        '\n<HEADER>'
        '\nGENERATION DATE       : '+ str(nowtime) + 
        '\nANTENNA               : VIL-2' 
        '\nLATITUDE              : 40d26m44.2s' 
        '\nLONGITUDE             : -3d57m9.4s' 
        '\nHEIGHT            [KM]: 0.6648' 
        '\nTARGET                : SCANNING' 
        '\nTRAJECTORY DATA SOURCE: CESAR/JPL'
        '\nS -DL-FREQUENCY  [MHZ]: 2277.000'
        '\nX -DL-FREQUENCY  [MHZ]: 0.000'
        '\nKA-DL-FREQUENCY  [MHZ]: 0.000'
        '\nANALYSIS PERIOD-START : '+ str(obs_time[0]) + 
        '\nANALYSIS PERIOD-END   : '+ str(obs_time[-1]) +
        '\nNUMBER OF PASSES      : 2'
        '\n</HEADER>'
        '\n<PASS>\n'
        + str(obs_time[0]) + '  ' + str(obs_time[-1]) +
        '\n<ZPASS>'
        '\n</ZPASS>'
        '\n<WRAP>'
        '\n</WRAP>'
        '\n<INIT_TRAVEL_RANGE>'
        '\n<LOWER/>'
        '\n</INIT_TRAVEL_RANGE>'
        '\n   Date - Time        AZ (Deg) EL (Deg) TxRx dXEl (deg) TxRx dEl (deg)  Range (km) Range Rate (km/s)    S-Dop (Hz)      X-Dop (Hz)      Ka-Dop(Hz)      S-EIRP(dBw)     X-EIRP(dBW)     Ka-EIRP(dBW)'
        '\n-------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        
        obs_time.out_subfmt = 'date'
        np.savetxt('datos/scan-'+str(nowtime)+'.txt',final, fmt="%s",
                   delimiter=" ", header=header, footer='</PASS>\n</FILE>', comments='')
        f = open('datos/scan-'+str(nowtime)+'.txt')
        
        inter = (
        '\n<PASS>\n'
        +str(nowtime)+
        '\n<ZPASS>'
        '\n</ZPASS>'
        '\n<WRAP>'
        '\n</WRAP>'
        '\n<INIT_TRAVEL_RANGE>'
        '\n<LOWER/>'
        '\n</INIT_TRAVEL_RANGE>'
        '\n   Date - Time        AZ (Deg) EL (Deg) TxRx dXEl (deg) TxRx dEl (deg)  Range (km) Range Rate (km/s)    S-Dop (Hz)      X-Dop (Hz)      Ka-Dop(Hz)      S-EIRP(dBw)     X-EIRP(dBW)     Ka-EIRP(dBW)'
        '\n-------------------------------------------------------------------------------------------------------------------------------------------------------------------------')      
        
        obs_time.out_subfmt = 'date_hms'
    
    else:
        raise ValueError("Invalid observing mode")

    
    #CHEQUEAR DOCUMENTACION DE ASTROPY.COORDINATES Y ASTROPY.TIME PARA VER LOS 
    #SEGUNDOS EXTRA (CADA 6 MESES) SI LOS METE, SI TIENE EN CUENTA NUTACION Y PRECESION 
    
    # COMENTARIOS
    #Diferencias entre coords Fortran y Python: 1.3 segundos en elevation, 3.2 en 
    #azimuth (2.3 media). La diferencia es menor en elevación en general así que
    # propongo 3.2 segundos para cuadrar el azimuth. --> azimuth idéntico y 
    #diferencia en elevación = 0.003º = 0.18' = 10.8". De la otra manera clavando 
    #la elevación la diferencia en azimuth es de 0.009º = 0.54' = 32" (3 veces más). 
    #Sin tocar nada la diferencia es de 0.02º = 1.2' azimut, 0.002º = 0.12' = 7.2" elev.
    
    # No entiendo que no haya ningún momento en el que las coordenadas coincidan:
    # diferentes sistemas de referencia? Chequear: tiene que ser cosa de las coords,
    # no del tiempo (creo)
    
    # Si se puede modificar la cabecera estaría bien añadir el tipo de observación:
    # Transit, Tracking o Scanning
