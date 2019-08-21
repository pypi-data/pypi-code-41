import sys 
import os

def tianhe():
    for i in sys.argv[1:]:
        if i.find('blsc605:')!=-1:
            break 
    else:
        return False
    command = ' '.join(sys.argv[1:]).replace('blsc605:','blsc605@gz:/PARA/blsc605/')
    command = '/home/yxs/F/learning/tianhe/papp_cloud-2.6.11/papp_cloud_linux64 rsync -i /home/yxs/F/learning/tianhe/papp_cloud-2.6.11/blsc605.id '+command 
    print(command)
    os.system(command)
    return True

if __name__=='__main__':
    is_tianhe = tianhe()