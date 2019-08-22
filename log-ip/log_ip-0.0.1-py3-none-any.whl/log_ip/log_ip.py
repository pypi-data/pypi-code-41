import urllib.request
import socket   
import datetime 

def get_private_ip():
    hostname = socket.gethostname()    
    return socket.gethostbyname(hostname)    
    
def get_public_ip():
    return urllib.request.urlopen('https://ident.me').read().decode('utf8')
     
def dump_in_file(*args):
    with open("log.txt", 'a+') as f:
        for t, u in zip(['private', 'public'], (args)):
            f.write(t + '\t' + u + "\n")


def main():
   pr = get_private_ip()
   pu = get_public_ip()
   now = datetime.datetime.now()
   print("Private", pr)
   print("Public", pu)
   dump_in_file(pr + '\t' + str(now), pu + '\t' + str(now))
    