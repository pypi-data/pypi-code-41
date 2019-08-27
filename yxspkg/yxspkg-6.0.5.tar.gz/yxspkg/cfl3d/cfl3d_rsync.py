import pexpect
import paramiko
import os
#在e2节点编译CFL3D
def run():
    command_source = 'rsync -r /home/yxs/F/learning/CFL3D/CFL3D/source public@e2:/home/public/yxs/CFL3D/'
    os.system(command_source)
if __name__=='__main__':
    run()