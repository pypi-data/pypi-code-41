def dockerd():
    import os 
    os.popen('/usr/bin/dockerd --log-level fatal')
