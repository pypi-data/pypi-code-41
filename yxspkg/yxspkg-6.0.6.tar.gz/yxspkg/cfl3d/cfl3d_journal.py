import sys 
import json
import os
import shutil
from os import path
def copy_data(inpdata,jdata,tag):
    inpfile = jdata['inpfile']
    dirname = ''.join(inpfile.split('.')[:-1])+'_{:04d}'.format(tag)
    if not path.exists(dirname):
        os.mkdir(dirname)
    inp = path.join(dirname,inpfile)
    fp = open(inp,'w')
    fp.write(''.join(inpdata))
    meshfile = inpdata[1].strip()
    restartfile = inpdata[13].strip()
    shutil.copy(meshfile,path.join(dirname,meshfile))
    shutil.copy(restartfile,path.join(dirname,restartfile))
    shutil.copy('./cfl3d_mpi',dirname)
    return dirname,inpfile
def run_cfl3d(dirname,inp):
    pwd = os.getcwd()
    os.chdir(dirname)
    os.system('mpirun -np 4 ./cfl3d_mpi < {}'.format(inp))
    os.chdir(pwd)
def set_bc(bctype,bcdata,inpdata,jdata,tag):
    n = -1
    while n < len(inpdata)-10:
        n += 1
        line = inpdata[n].split()
        if len(line) <8: continue
        if not line[2].isdigit():continue
        if int(line[2]) == int(bctype):
            inpdata[n+2] = bcdata.strip()+'\n'
            n += 2
    # print(inpdata)
    return copy_data(inpdata,jdata,tag)

def run(jfile):
    jdata = json.loads(open(jfile).read())
    inpdata = open(jdata['inpfile']).readlines()
    tag = 0
    for k in jdata:
        if k.startswith('bc'):
            bctype = k[2:]
            for bcdata in jdata[k]:
                tag += 1
                dirname,inp = set_bc(bctype,str(bcdata),inpdata,jdata,tag)
                run_cfl3d(dirname,inp)
if __name__=='__main__':
    run('./test.json')