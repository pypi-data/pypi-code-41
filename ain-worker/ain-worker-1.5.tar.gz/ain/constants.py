import os 

SHARED_PATH = os.path.dirname(os.path.abspath(__file__)) + "/share"
ENV_FILE_PATH = SHARED_PATH + "/worker.env"
IMAGE = "ainblockchain/ain-worker:1.0.0"
