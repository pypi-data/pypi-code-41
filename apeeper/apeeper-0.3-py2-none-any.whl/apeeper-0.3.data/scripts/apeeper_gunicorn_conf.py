import gunicorn
from apeeper.register import setup_apeeper
from apeeper.extras import remove_apeeper_iprules

workers = 1
bind = "0.0.0.0:5000"
gunicorn.SERVER_SOFTWARE = 'EC2ws'
default_proc_name = "ec2metadataservice"
proc_name = "ec2metadataservice"

def on_starting(server):
    setup_apeeper()

def on_exit(server):
    remove_apeeper_iprules()