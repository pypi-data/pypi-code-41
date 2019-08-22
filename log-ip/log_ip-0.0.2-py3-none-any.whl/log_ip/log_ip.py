import urllib.request
import socket   
import datetime 


def get_private_ip():
    hostname = socket.gethostname()
    print(hostname)
    return socket.gethostbyname(hostname)    

    
def get_public_ip():
    return urllib.request.urlopen('https://ident.me').read().decode('utf8')

     
def dump_in_file(tag, entries, filename='log-ip.txt'):
    with open(filename, 'a+') as f:
        for k, v in entries.items():
            f.write(tag + '\t' + k + '\t' + v + "\n")


def main():
   pr = get_private_ip()
   pu = get_public_ip()
   now = datetime.datetime.now()
   hostname = socket.gethostname()
   print("Private", pr)
   print("Public", pu)
   dump_in_file(str(now) + '\t' + hostname, dict(Private=pr, Public=pu))

