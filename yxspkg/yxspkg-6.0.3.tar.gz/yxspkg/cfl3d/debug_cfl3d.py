import os
import shutil
from pathlib import Path 
import sys
import time
def compile_(mpi = False):
    source_cfl3d = Path('/home/yxs/F/learning/CFL3D/CFL3D/source/cfl3d')
    dist = source_cfl3d / 'dist'
    libs = source_cfl3d / 'libs'
    fortran_F = list(dist.glob('*.F')) + list(libs.glob('*.F')) + list(libs.glob('*.F90')) + list(dist.glob('*.F90'))

    F_time = {i.stem:(i,i.lstat().st_mtime) for i in fortran_F}


    assert len(F_time) == len(fortran_F)
    if mpi:
        seq_source = source_cfl3d.parent.parent / 'build' / 'cfl' / 'mpi'
    else:
        seq_source = source_cfl3d.parent.parent / 'build' / 'cfl' / 'seq'
    libs_source = source_cfl3d.parent.parent / 'build' / 'cfl' / 'libs'
    O_time_list = list(seq_source.glob('*.o')) + list(libs_source.glob('*.o'))
    O_time = {i.stem:(i,i.lstat().st_mtime) for i in O_time_list}

    # assert len(O_time) == len(O_time_list)
    delete_files = []
    old_time = 0
    for key,value in O_time.items():
        Opath, Omtime = value 
        value_F = F_time[key]
        Fpath, Fmtime = value_F
        if Fmtime > Omtime:
            os.remove(Opath)
            if Fmtime > old_time:
                old_time = Fmtime
            print("Delete ",Opath)
            delete_files.append(str(Fpath))

    for i in delete_files:
        rsync_file(i)
        print("同步到e2",i)
    build_path = source_cfl3d.parent.parent / 'build'
    os.chdir(build_path)
    print('当前目录',os.getcwd())
    if mpi:
        os.system('make cfl3d_mpi')
        p = build_path / 'cfl' /'mpi'/'cfl3d_mpi'
    else:
        os.system('make cfl3d_seq')
        p = build_path / 'cfl' /'seq'/'cfl3d_seq'
    new_time = p.lstat().st_mtime 
    if new_time < old_time or old_time == 0:
        input("本次编译对执行文件没有产生任何变化，是否继续[y]")
    
    return p 
def exit_mpi():
    k = os.popen('ps -A | grep mpi').read()
    cm = k.split()
    if cm:
        os.system('kill {}'.format(cm[0]))
def rsync_file(filename):
    n = filename.find('CFL3D/source')
    if n != -1:
        dest = filename[n:]
    else:
        return
    command = f'rsync {filename} public@e2:/home/public/yxs/{dest}'
    os.system(command)
if __name__=='__main__':
    arg1 = sys.argv[1]
    # f = Path(sys.argv[1]).absolute()
    # print(f)
    if  arg1.startswith('-'):
        f = Path(sys.argv[2]).absolute()
        print(f)
        p = compile_(True)
        mpif = f.parent / 'cfl3d_mpi'
        if mpif.exists():
            os.remove(mpif)
        shutil.copy(p,f.parent)
        os.chdir(f.parent)
        print('当前目录',os.getcwd())
        print("开始运行")
        os.system('mpirun -np {} ./cfl3d_mpi < {}'.format(int(arg1[1:]),f.name))
        try:
            time.sleep(365*24*60*60)
        except:
            print('exit mpi')
            exit_mpi()
    else:
    
        f = Path(arg1).absolute()
        print(f)
        p = compile_()
        shutil.copy(p,f.parent)
        os.chdir(f.parent)
        print('当前目录',os.getcwd())
        print("开始运行")
        os.system('./cfl3d_seq < {}'.format(f.name))