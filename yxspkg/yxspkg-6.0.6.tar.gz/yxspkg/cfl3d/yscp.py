import pexpect
import sys 
import os
def run(terminal = True):
    def deal(command):
        command = command.strip()
        n = command.find(':')
        if n !=-1:
            command = command[:n+1]+'/home/public/yxs/'+command[n+1:]
            command = 'public@'+command 
            return command
        else:
            return command
    v = [deal(i) for i in sys.argv[1:]]
    com ='scp '+ ' '.join(v)
    print(com)
    if terminal:
        os.system(com)
    else:
        t = pexpect.spawn(com)
        f = t.expect('.password:')
        if f==0:
            t.sendline('public')
            t.read()
def tianhe():
    for i in sys.argv[1:]:
        if i.find('blsc605:')!=-1:
            break 
    else:
        return False
    command = ' '.join(sys.argv[1:]).replace('blsc605:','blsc605@gz:/PARA/blsc605/')
    command = '/home/yxs/F/learning/tianhe/papp_cloud-2.6.11/papp_cloud_linux64 scp -i /home/yxs/F/learning/tianhe/papp_cloud-2.6.11/blsc605.id '+command 
    print(command)
    os.system(command)
    return True

if __name__=='__main__':
    is_tianhe = tianhe()
    if not is_tianhe:
        run()