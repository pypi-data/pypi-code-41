import requests
from datetime import datetime

def placeapi(place):
    placeapi="https://api.weather.com/v3/location/search?apiKey=d522aa97197fd864d36b418f39ebb323&format=json&language=en-IN&locationType=locale&query="+place;
    l=[]
    l.append(placeapi)
    r = requests.get(placeapi)
    if r.status_code == 200:
        p=r.json()
        lat=str(p["location"]["latitude"][0])
        lon=str(p["location"]["longitude"][0])
        l.append(lat)
        l.append(lon)
    
    return(l)



def dailycall(lat,lon):
    da="https://api.weather.com/v2/turbo/vt1observation?apiKey=d522aa97197fd864d36b418f39ebb323&format=json&geocode="+lat+"%2C"+lon+"&language=en-IN&units=m"
    r = requests.get(da)
    if r.status_code == 200:
        p=r.json()
        obs=str(p["vt1observation"])
        print(obs)
    else:
        print("Invalid")


def monthlycall(lat,lon):
    mon="https://api.weather.com/v2/turbo/vt1dailyForecast?apiKey=d522aa97197fd864d36b418f39ebb323&format=json&geocode="+lat+"%2C"+lon+"&language=en-IN&units=m"
    r = requests.get(mon)
    v=[]
    if r.status_code == 200:
        p=r.json()
        obs= p["vt1dailyForecast"]["day"]
        obs1= p["vt1dailyForecast"]["night"]
        v1 = [dict(zip(obs,t)) for t in zip(*obs.values())]
        v2 = [dict(zip(obs1,t)) for t in zip(*obs1.values())]
        for i in range(len(v1)):
            vtemp=[]
            vtemp.append(v1[i])
            vtemp.append(v2[i])
            v.append(vtemp)
        return(v)
            

    else:
        print("Invalid")


def returnNo_of_Dayscall(v):
    
    for i in v:
        print(i)
        print("\n")

def findDateCall(date1,lat,lon):
    mon="https://api.weather.com/v2/turbo/vt1dailyForecast?apiKey=d522aa97197fd864d36b418f39ebb323&format=json&geocode="+lat+"%2C"+lon+"&language=en-IN&units=m"
    r = requests.get(mon)
    if r.status_code==200:
        obs = r.json()["vt1dailyForecast"]
        obs1 = r.json()["vt1dailyForecast"]["day"]
        obs2 = r.json()["vt1dailyForecast"]["night"]
        obs = [dict(zip(obs,t)) for t in zip(*obs.values())]
        obs1 = [dict(zip(obs1,t)) for t in zip(*obs1.values())]
        obs2 = [dict(zip(obs2,t)) for t in zip(*obs2.values())]

        for i in range(len(obs)):
            if str(date1) in str(obs[i]["validDate"]):
                print(obs[i])
                print(obs1[i])
                print(obs2[i])
    



def start(place1,dateinp=datetime.today().strftime('%Y-%m-%d'),type="daily"):

    place=place1
    date1=dateinp
    
    type_of_forecast=type

    out=placeapi(place)
    lat=out[1]
    lon=out[2]
    print(place,"\n",date1,"\n",type_of_forecast,"\n",out)
    if(type_of_forecast=='daily'):
        dailycall(lat,lon)
    
    if(type_of_forecast=='monthly'):
        monthly=monthlycall(lat,lon)
        for i in monthly:
            print(i)
            print("\n")
    
    
    if(type_of_forecast=='5days'):
        val=monthlycall(lat,lon)
        returnNo_of_Dayscall(val[0:5])
    
    if(type_of_forecast=='10days'):
        val=monthlycall(lat,lon)
        returnNo_of_Dayscall(val[0:10])
    
    if(type_of_forecast=='datewise'):
        findDateCall(date1,lat,lon);




