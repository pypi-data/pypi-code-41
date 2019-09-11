from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions
from LocToWeatherAPI.main import driver

app = FlaskAPI(__name__)

@app.route("/", methods=['GET'])
def rules():
    if request.method == 'GET':
        rules = (
        "1.(/<Name of Place>/ or /<Name of Place>/1/ - Today's weather for Place.) "
        "2.(/<Name of Place>/2/ - Monthly forecast for place.) "
        "3.(/<Name of Place>/3/ - 5 days forecast for place.) "
        "4.(/<Name of Place>/4/ - 10 days forecast for place.) "
        "5.(/<Name of Place>/<Date>/ - <Date>'s forecast for place.) "
        )
        return {"rules":rules}

@app.route("/<string:place>/", methods=['GET'])
def place_daily_data(place):
    ret=[]
    if request.method == 'GET':
        ret,a,b,place_name = driver(place)
        return {place_name:ret}

@app.route("/<string:place>/<int:selector>", methods=['GET'])
def place_selection_data(place,selector):
    returns=[]
    if request.method == 'GET':
        if selector==1:
            return place_daily_data(place)
        else:
            ret,a,b,place_name = driver(place,type_of_forecast=str(selector))
            if selector==2:
                return {place_name:ret}
            if selector==3:
                records=5
            if selector==4:
                records=10
            for i in range(records):
                temp_data={}
                temp_data.update(ret[i])
                temp_data.update(a[i])
                temp_data.update(b[i])
                returns.append(temp_data)
            return {place_name:returns}

@app.route("/<string:place>/<string:date>", methods=['GET'])
def place_selection_date(place,date):
    returns=[]
    count1=0
    if request.method == 'GET':
        ret,a,b,place_name = driver(place,date=date)
        for i in range(len(ret)):
            if date in str(ret[i]["validDate"]):
                count1=count1+1
                temp_data={}
                temp_data.update(ret[i])
                temp_data.update(a[i])
                temp_data.update(b[i])
                returns.append(temp_data)
        if count1!=0:
            return {place_name:returns}
        else:
            return {place_name:"No Data found for date : "+str(date)}

def start():
    app.run()

if __name__ == "__main__":
    start()
