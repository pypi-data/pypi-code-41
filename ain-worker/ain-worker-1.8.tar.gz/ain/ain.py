import click
from ain.workerMgr import Worker
import ain.constants as constants

@click.group()
@click.option('--type/--no-type', default=False)
def call(type):
  pass

@call.command()
@click.argument("command", type=click.Choice(['start', 'stop', 'status', 'log', 'init', 'version']))
@click.option('--name', default="", help="Ain Worker name")
@click.option('--limit-count', default="", help="maximum number of Instances")
@click.option('--price', default="", help="ain/h")
@click.option('--mnemonic', default="", help="mnemonic")
@click.option('--description', default="empty", help="description")
@click.option('--server-ip', default="empty", help="Cloud Server IP")
@click.option('--gpu', default="false", help="gpu")

def worker(command, name, limit_count, price, mnemonic, description, server_ip, gpu):

  optionRun = {
    'NAME': name,
    'LIMIT_COUNT': limit_count,
    'MNEMONIC': mnemonic,
    'PRICE': price,
    'DESCRIPTION': description,
    'GPU': gpu,
    'SERVER_IP': server_ip
  }

        
  w = Worker()  
  if (command == "start"):
    w.start(optionRun)
  elif (command == "stop"):
    w.stop()
  elif (command == "status"):
    w.status()
  elif (command == "log"):
    w.log()
  elif (command == "init"):
    w.init()
  elif (command == "version"):
    w.version()
    
if __name__ == '__main__':
  call()
