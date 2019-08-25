from .lib.air_quality_pb2 import DataPoint

class Default:
    topic = "AIR.QUALITY"
    rpcURL = "127.0.0.1:5555"

class Type:
    PM2_5 = DataPoint.PM2_5            
    PM10 = DataPoint.PM10     
    NO = DataPoint.NO  
    NO2 = DataPoint.NO2      
    NOX = DataPoint.NOX    
    NH3 = DataPoint.NH3    
    SO2 = DataPoint.SO2    
    CO = DataPoint.CO    
    OZONE = DataPoint.OZONE      
    BENZENE = DataPoint.BENZENE
    TOLUENE = DataPoint.TOLUENE
    TEMP = DataPoint.TEMP
    RH = DataPoint.RH 
    WS = DataPoint.WS     
    WD = DataPoint.WD     
    BP = DataPoint.BP      