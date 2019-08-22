from dotenv import load_dotenv
from pathlib import Path, PurePath
import os

dotenv_path = PurePath(Path.home(), '.wc/datanator.env')
load_dotenv(dotenv_path)


class Config:
    PRODUCTION = os.getenv("PRODUCTION", False)
    USERNAME = os.getenv("MONGO_USERNAME")
    PASSWORD = os.getenv("MONGO_PASSWORD")
    SERVER = os.getenv("MONGO_DATANATOR_SERVER")
    PORT = os.getenv("MONGO_PORT")
    REPLSET = os.getenv("MONGO_REPL")
    AUTHDB = os.getenv("MONGO_AUTHDB")
    SESSION_KEY = os.getenv("FLASK_SESSION_KEY")


class ProductionConfig(Config):

    PRODUCTION = True

class UserAccountConfig(Config):
	
	USERDAEMON = os.getenv("MONGO_USER_DAMON")
	USERDAEMON_PASSWORD = os.getenv("MONGO_USER_PASSWORD")
	USERDAEMON_AUTHDB = os.getenv("MONGO_USER_AUTHDB")

class FlaskProfiler(UserAccountConfig):
    url = ('mongodb://' + os.getenv("MONGO_AP_USER") + ':' + os.getenv("MONGO_AP_PASSWORD")
    + '@' + os.getenv("MONGO_DATANATOR_SERVER") + ':' + os.getenv("MONGO_PORT"))
    FLASKPROFILER = {
    "enabled": True,
    "storage": {
        "engine": "mongodb",
        "MONGO_URL": url,
        "DATABASE": 'flask_profiler',
        "COLLECTION": 'measurements'
    },
    "basicAuth":{
        "enabled": True,
        "username": os.getenv("MONGO_AP_USER"),
        "password": os.getenv("FLASK_PROFILER_PASSWORD")
    },
    "ignore": [
        "^/static/.*"
    ],
    "endpointRoot": "performance"
    }