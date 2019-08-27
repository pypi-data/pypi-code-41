from yxspkg import plot3d
from pathlib import Path
import os
import shutil
import math
from . import one2one as o2o
class inputFile:
    def __init__(self,workdir,gridfile,timestep=1,turbulence_model=5,ALPHA=90,BETA=0,
                input_filename = 'input.inp',keyword_driven=False,work_name="CFL3D Case configuration",
                **kargs):
        #环境温度 默认 300K
        self.env_temperature = kargs['env_temperature']
        #环境压力 默认 101000Pa
        self.env_pressure = kargs['env_pressure']
        #介质比热比 默认空气 1.4
        self.env_gamma = kargs['env_gamma']
        #气体常数R= 287.14
        self.env_R = kargs.get('env_R',287.14)
        #入口速度  单位m/s 
        self.xmach = kargs['xmach']
        #动力年度 应力与应变速率之比 国际单位 Pa.s
        self.env_viscosity = kargs['env_viscosity']
        #LREF 相当于fluent中设置单位的选项
        self.LREF = kargs['LREF']
        if abs(self.LREF - 1) > 1e-9:
            self.scale_mesh = self.LREF 
            self.LREF = 1
        else:
            self.scale_mesh = None
        #计算声速
        self.env_acusitic_velocity = (self.env_gamma*self.env_R*self.env_temperature)**0.5
        #reue
        self.reue = self.env_pressure/(self.env_R*self.env_temperature)*self.xmach*self.env_acusitic_velocity / self.env_viscosity*1e-6
        #攻角
        self.envAlpha = ALPHA
        self.envBeta = BETA
        #CFL数
        self.CFL_number = kargs.get('CFL_number',5)
        #时间步数
        self.number_of_time_step = kargs.get('number_of_time_step',1)
        #时间步长
        self.time_step = kargs.get('time_step',0)
        #ita 这个参数表示迭代策略和精度  |ITA|=2 表示二阶时间精度
        self.ITA = kargs.get('ITA',-2)
        #DT
        self.DT = kargs.get('DT',None)
        #IREST 是否继续上次的算列算 
        self.IREST = kargs.get('IREST',0)
        #iflags 时间步是否是可变的
        self.IFLAGTS = kargs.get('IFLAGTS',0)
        #fmax 时间步变化的最大倍数，当iflagts>0时可用
        self.FMAX = kargs.get('FMAX',1)
        #将boundary的faceId都调整为大写
        kargs['BOUNDARY'] = {key.upper():{t.upper():v for t,v in value.items()} for key,value in kargs['BOUNDARY'].items()}

        self.workdir = workdir
        self.pwd = os.getcwd()
        os.chdir(workdir)
        self.gridfile_name = gridfile
        self.timestep = timestep
        self.turbulence_model = turbulence_model
        self.fp = open(input_filename,'w')
        self.input_filename = input_filename
        self.keyword_driven = keyword_driven 
        self.kargs = kargs
        self.work_name = work_name
    def start_write(self):
        #当前目录位于 workdir
        kargs = self.kargs
        fp = self.fp 
        fp.write('I/O FILES\n') #文件开头
        #self.gridfile_name 存储输入文件的名字，self.gridfile 存储将网格放入workdir后的名字
        self.gridfile = self.read_gridfile(self.gridfile_name)
        # p = Path(self.gridfile)
        fp.write(self.gridfile+'\n')
        # fp.write('output.g\noutput.q\n')
        t = self.input_filename[:-4]+'_'
        
        other_files = ['output.g','output.q','cfl3d.out','cfl3d.res','cfl3d.turres','cfl3d.blomax','cfl3d.out15',
                       'cfl3d.prout','cfl3d.out20','ovrlp.bin','patch.bin\n']
        fp.write('\n'.join([t+i for i in other_files]))
        restart_file = self.get_restart_file()
        fp.write(restart_file+'\n')
        self.write_keyword_driven()
        #写入工程名称
        fp.write('  {}\n'.format(self.work_name.strip()))
        self.write_IYXS_block()
        self.write_XMACH_line()
        self.write_SREF_line()
        self.write_DT_line()
        self.write_NGRID_line()
        self.write_NCG_line()
        self.write_IDIM_line()
        #指定层流区
        self.write_ILAMLO_line()
        #嵌入网格 Embedded Mesh Specifications
        self.write_INEWG_line()
        #矩阵求逆和通量限制
        self.write_IDIAG_line()
        #空间差分
        self.write_IFDS_line()
        #边界条件段 和 重叠网格 默认无重叠网格
        self.write_IOVRLP_line()
        #边界条件设置
        self.write_BOUNDARY_block()
        #关于多重网格迭代的设置
        self.write_MSEQ_line()
        #光顺
        self.write_ISSC_line()
        #迭代步数和多重网格的一些设定
        self.write_NCYC_line()
        #粗网格迭代
        self.write_MIT1_line()
        #1-1 block data
        self.write_One_to_One_block()
        #交接面信息
        self.write_NINTER_block()
        #输出数据设置
        self.write_OUTPUT_block()
        #控制面信息，检测某一个面的流量，力，速度的设置 
        self.write_CONTROL_SURFACE_block()
        #平移网格设置
        self.write_TRANS_block()
        #旋转网格的设置
        self.write_ROTATE_block()
        #动网格交界面插值设置
        self.write_DYNAMIC_PATCH_block()
    def get_restart_file(self):
        t = self.input_filename[:-4]+'_'
        restart_file = self.kargs.get('restart_file')
        if restart_file:
            ff = t+'restart.bin'
            shutil.copy(restart_file,ff)
            self.kargs['IREST'] = 1
            return ff
        else:
            return t+'restart.bin'
    def write_keyword_driven(self):
        if self.keyword_driven:
            pass 
        else:
            return None
    def read_gridfile(self,filename):
        if isinstance(filename,str):
            k = plot3d.read(filename)
        else:
            k = filename
        if self.scale_mesh is not None:
            k = [{key:val*self.scale_mesh for key,val in i.items()} for i in k]
        self.blocks = k
        ftype = k[0]['X'].dtype 
        if ftype == 'float32':
            k = [{key:v.astype('float64') for key,v in i.items()} for i in k]
        self.NGRID = -len(k)
        self.blocks_ijk = [i['X'].shape for i in k]
        fname = self.input_filename[:-4]+'_'+'mesh.g'
        plot3d.write(fname,k)
        return fname
    def write_IYXS_block(self):
        if self.kargs.get('IYXS') is None:
            return
        fp = self.fp 
        fp.write('    IYXS\n     {}\n'.format(self.kargs.get('IYXS')))
        init_file = self.kargs.get('init_file')
        if init_file is not None:
            ifile = 2
            if init_file != 'init.q':
                shutil.copy(init_file,'init.q')
                init_file = 'init.q'
        else:
            init_file = 'init.q'
            ifile = 0
        fp.write("     init_file ig yxs_g  iq yxs_q\n")
        fp.write('     {}  {}  0   yxs.g   0  yxs.q\n'.format(ifile,init_file))
        fp.write('     noninflag\n       0\n')
        fp.write('     mean\n       0\n')
        fp.write('     underrelaxed\n       0\n')
    def write_XMACH_line(self):
        title = '     XMACH     ALPHA      BETA  REUE,MIL   TINF,DR     IALPH    IHSTRY\n'
        self.fp.write(title)
        
        self.envMach = self.xmach
        IALPH = self.kargs.get('IALPH',0)
        XMACH = self.xmach 
        ALPHA = self.envAlpha 
        BETA  = self.envBeta
        REUE = self.reue 
        TINF = self.env_temperature*9/5
        IHSTRY = 0
        fstr = '{:>10.4f}'*5+'{:>10d}{:>10d}\n'
        self.fp.write(fstr.format(XMACH,ALPHA,BETA,REUE,TINF,IALPH,IHSTRY))
    def write_SREF_line(self):
        #不太清楚这一栏是干嘛的 先写成这样的值吧
        title ='      SREF      CREF      BREF       XMC       YMC       ZMC\n'
        value ='   1.00000   1.00000    1.0000    0.00000   0.0000    0.0000\n'
        self.fp.write(title)
        self.fp.write(value)
    def write_DT_line(self):
        kargs = self.kargs
        title = '        DT     IREST   IFLAGTS      FMAX     IUNST   CFL_TAU\n'
        self.fp.write(title)
        DT = kargs.get('DT')
        if self.number_of_time_step == 1:
            DT = str(-self.CFL_number)
        if DT is None:
            
            DT = self.time_step*self.env_acusitic_velocity
            DT /= self.LREF
            DT = '+{}'.format(DT)[:7]
        else:
            DT = str(DT)
        #IREST 是否继续上次的算列算 
        IREST = kargs.get('IREST',0)
        #iflags 时间步是否是可变的
        IFLAGTS = kargs.get('IFLAGTS',0)
        #fmax 时间步变化的最大倍数，当iflagts>0时可用
        FMAX = kargs.get('FMAX',1)
        #iunst 网格是否是定常的
        IUNST = kargs.get('IUNST',0)
        #CFL数的大小，当ITA<0时
        CFL_TAU = kargs.get('CFL_TAU')
        if float(DT) < 0:
            CFL_TAU = 0
        if CFL_TAU is None:
            if self.ITA < 0:
                CFL_TAU = self.CFL_number
        fstr = '{:>10s}{:>10d}{:>10d}{:>10.6f}{:>10d}{:>10.6f}\n'
        self.fp.write(fstr.format(DT,IREST,IFLAGTS,FMAX,IUNST,CFL_TAU))
    def write_NGRID_line(self):
        title = '     NGRID   NPLOT3D    NPRINT    NWREST      ICHK       I2D    NTSTEP       ITA\n'
        self.fp.write(title)
        NGRID = self.NGRID
        NPLOT3D = abs(NGRID)
        NWREST = self.kargs.get('NWREST',1000000)
        NPRINT = self.kargs.get("NPRINT",0)
        ICHK = self.kargs.get('ICHK',0)
        I2D = self.kargs['I2D']
        NTSTEP = self.kargs.get('NTSTEP',self.number_of_time_step)
        ITA = self.kargs.get('ITA',-2)
        fstr = '{:>10d}'*8+'\n'
        self.fp.write(fstr.format(NGRID,NPLOT3D,NPRINT,NWREST,ICHK,I2D,NTSTEP,ITA))
    def write_NCG_line(self):
        title = '       NCG       IEM  IADVANCE    IFORCE  IVISC(I)  IVISC(J)  IVISC(K)\n'
        self.fp.write(title)
        NCG = self.kargs.get('NCG',0)
        self.multigrid = NCG
        IEM = 0
        IADVANCE = 0
        IFORCE = 0
        fstr = '{:>10d}'*7+'\n'
        m = self.turbulence_model
        if self.kargs.get('I2D',1) == 1:
            m2d = 0 
        else:
            m2d = m
        for _ in range(abs(self.NGRID)):
            self.fp.write(fstr.format(NCG,IEM,IADVANCE,IFORCE,m2d,m,m))
    def write_IDIM_line(self):
        title = '      IDIM      JDIM      KDIM\n'
        self.fp.write(title)
        fstr = '{:>10d}'*3+'\n'
        for i,j,k in self.blocks_ijk:
            self.fp.write(fstr.format(i,j,k))
    def write_ILAMLO_line(self):
        title = '    ILAMLO    ILAMHI    JLAMLO    JLAMHI    KLAMLO    KLAMHI\n'
        self.fp.write(title)
        fstr = '{:>10d}'*6+'\n'
        for _ in range(abs(self.NGRID)):
            self.fp.write(fstr.format(0,0,0,0,0,0))
    def write_INEWG_line(self):
        title = '     INEWG    IGRIDC        IS        JS        KS        IE        JE        KE\n'
        self.fp.write(title)
        fstr = '{:>10d}'*8+'\n'
        for _ in range(abs(self.NGRID)):
            self.fp.write(fstr.format(0,0,0,0,0,0,0,0))
    def write_IDIAG_line(self):
        #矩阵求逆 和 通量限制
        
        title = '  IDIAG(I)  IDIAG(J)  IDIAG(K)  IFLIM(I)  IFLIM(J)  IFLIM(K)\n'
        self.fp.write(title)
        fstr = '{:>10d}'*6+'\n'
        for _ in range(abs(self.NGRID)):
            self.fp.write(fstr.format(1,1,1,0,0,0))
    def write_IFDS_line(self):
        #空间差分
        self.fp.write('   IFDS(I)   IFDS(J)   IFDS(K)  RKAP0(I)  RKAP0(J)  RKAP0(K)\n')
        fstr = '{:>10d}'*3+'{:>10.5f}'*3+'\n'
        for _ in range(abs(self.NGRID)):
            self.fp.write(fstr.format(1,1,1,1/3,1/3,1/3))
    def write_IOVRLP_line(self):
        #边界条件段和重叠网格 默认无重叠网格
        self.fp.write('      GRID     NBCI0   NBCIDIM     NBCJ0   NBCJDIM     NBCK0   NBCKDIM   IOVRLP \n')
        fstr = '{:>10d}'*8+'\n'
        for i in range(abs(self.NGRID)):
            self.fp.write(fstr.format(i+1,1,1,1,1,1,1,0))

    def SetBoundaryLine(self,faceId):
        #faceId:Nmn  N:blockid,m:I or J or K, n:0 or E or e
        fstr = '{:>10d}'*8+'\n'
        blockId = int(faceId[:-2])
        boundary = self.kargs['BOUNDARY'].get(faceId)
        if not boundary:
            return fstr.format(blockId,1,0,0,0,0,0,0)
        bctype = boundary['BCTYPE']
        if bctype == 0:
            result = fstr.format(blockId,1,0,0,0,0,0,0)
        elif abs(bctype) == 2004:#无滑移
            result = fstr.format(blockId,1,bctype,0,0,0,0,2)
            result += 'Tw      Cq\n0.      0.\n'
        elif bctype == 2003:#入口条件
            result = fstr.format(blockId,1,2003,0,0,0,0,5)
            result +='Mach  Pt/Pinf  Tt/Tinf  alpha  beta\n'
            inFstr = '{:5.4f}{:>8.5f} {:>9.5f} {:>7.5f} {:>6.5f}\n'
            Pt,Tt = boundary['DATA']
            Tt/=self.env_temperature 
            Pt/=self.env_pressure
            result += inFstr.format(self.envMach,Pt,Tt,self.envAlpha,self.envBeta)
        elif bctype == 2002:#压力出口条件
            result = fstr.format(blockId,1,bctype,0,0,0,0,1)
            pressure = boundary.get('PRESSURE')
            if pressure is None:
                pressure = self.kargs['output_pressure']
            result += 'pexit/pinf\n{:.5f}\n'.format(pressure/self.env_pressure)
        elif bctype == 2006:#适合叶轮机械的压力径向平衡的出口条件
            result = fstr.format(blockId,1,bctype,0,0,0,0,4)
            ngridc,p_p,intdir,axcoord = boundary['DATA']
            if p_p == 0:
                p_p = self.kargs['output_pressure'] / self.env_pressure
            result += 'ngridc  P/Pinf  intdir axcoord\n{:d} {:.4f} {:+4d} {:4d}\n'.format(
                ngridc,p_p,intdir,axcoord)
        elif bctype == 2005:
            t = [(i,j) for i,j in boundary['ONE2ONE'][:3] if i!=j]
            t = [i for v in t for i in v]
            result = fstr.format(blockId,1,bctype,*t,4)
            result += '    ngridp      dthx      dthy      dthz\n{:d} {:.6f} {:6f} {:6f}\n'.format(*boundary['AUXDATA'])
        else:
            raise Exception('bctype error!!')
        return result
        


    def write_BOUNDARY_block(self):
        title = '{:<6s}GRID   SEGMENT    BCTYPE      JSTA      JEND      KSTA      KEND    NDATA\n'
        
        for i in ['I0:','IDIM:','J0:','JDIM:','K0:','KDIM:']:
            self.fp.write(title.format(i))
            for j in range(abs(self.NGRID)):
                faceId = '{}{}'.format(j+1,i[:2].replace('D','E'))
                boundLine = self.SetBoundaryLine(faceId)
                self.fp.write(boundLine)
    def write_MSEQ_line(self):
        title = '      MSEQ    MGFLAG    ICONSF       MTT      NGAM\n'
        fstr='{:>10d}'*5+'\n'
        #MSEQ:多重网格计算过程中的排序方式,这个参数会涉及到restat文件的保存内容 （目前理解可能存在偏差）,默认参数1
        MSEQ = self.kargs.get('MSEQ',1)
        #MGFLAG：是否采用多重网格的标志，默认不采用多重网格
        MGFLAG = self.kargs.get('MGFLAG',0)
        if self.multigrid is not 0 and MGFLAG is 0:
            MGFLAG = 1
        #NGAM：多重网格迭代方式 V W 重叠网格不推荐W型,默认采用V型
        NGAM = self.kargs.get('NGAM',1)
        #ICONSF 关于嵌入网格通量计算时的设置，默认取1
        ICONSF = self.kargs.get('ICONSF',1)
        #官方推荐0
        MTT = self.kargs.get('MTT',0)
        self.fp.write(title)
        self.fp.write(fstr.format(MSEQ,MGFLAG,ICONSF,MTT,NGAM))
    def write_ISSC_line(self):
        title = '      ISSC  EPSSC(1)  EPSSC(2)  EPSSC(3)      ISSR  EPSSR(1)  EPSSR(2)  EPSSR(3)\n'
        fstr=('{:>10d}'+'{:>10.4f}'*3)*2+'\n'
        self.fp.write(title)
        #
        ISSC = self.kargs.get('ISSC',0)
        #
        EPSSC1 = self.kargs.get('EPSSC1',1/3)
        EPSSC2 = self.kargs.get('EPSSC2',1/3)
        EPSSC3 = self.kargs.get('EPSSC3',1/3)
        #
        ISSR = self.kargs.get('ISSR',0)
        EPSSR1 = self.kargs.get('EPSSR1',1/3)
        EPSSR2 = self.kargs.get('EPSSR2',1/3)
        EPSSR3 = self.kargs.get('EPSSR3',1/3)
        self.fp.write(fstr.format(ISSC,EPSSC1,EPSSC2,EPSSC3,ISSR,EPSSR1,EPSSR2,EPSSR3))
    def write_NCYC_line(self):
        title = '      NCYC    MGLEVG     NEMGL     NITFO\n'
        fstr = '{:>10d}'*4+'\n'

        NCYC = self.kargs.get('NCYC',10)
        MGLEVG = self.kargs.get('MGLEVG',1)
        if self.multigrid is not 0 and MGLEVG is 1:
            MGLEVG = 2
        NEMGL = self.kargs.get('NEMGL',0)
        NITFO = self.kargs.get('NITFO',0)
        self.fp.write(title)
        self.fp.write(fstr.format(NCYC,MGLEVG,NEMGL,NITFO))
    def write_MIT1_line(self):
        title = '      MIT1      MIT2      MIT3      MIT4      MIT5\n'
        fstr = '{:>10d}'*5+'\n'
        self.fp.write(title)
        self.fp.write(fstr.format(1,1,1,1,1))
    def write_One_to_One_block(self):
        oneone_block = self.kargs.get('oneOne','1-1 blocking data:\n')
        if not isinstance(oneone_block,str):
            oneone_block = o2o.transfer_one2one_str(oneone_block)
        self.fp.write(oneone_block.rstrip())
        self.fp.write('\n')
    def write_NINTER_block(self):
        title = '  PATCH SURFACE DATA:\n    NINTER\n'
        self.fp.write(title)
        NINTER = self.kargs.get('NINTER',0)
        assert NINTER == 0
        self.fp.write('{:>10d}\n'.format(0))
    def write_OUTPUT_block(self):
        title = '  PLOT3D OUTPUT:\n   GRID IPTYPE ISTART   IEND   IINC JSTART   JEND   JINC KSTART   KEND   KINC\n'
        self.fp.write(title)
        IPTYPE = self.kargs.get('IPTYPE',0)
        MOVIE = self.kargs.get('MOVIE',0)
        fstr = '{:>7d}'*11+'\n'
        for i in range(abs(self.NGRID)):
            self.fp.write(fstr.format(i+1,IPTYPE,0,0,0,0,0,0,0,0,0))
        self.fp.write('{:>7s}\n{:>7d}\n'.format('MOVIE',MOVIE))

        #PRINT OUT
        title2 = '  PRINT OUT:\n  BLOCK IPTYPE ISTART   IEND   IINC JSTART   JEND   JINC KSTART   KEND   KINC\n'
        self.fp.write(title2)
    def write_CONTROL_SURFACE_block(self):
        title = ' CONTROL SURFACES:\n   NCS\n'
        self.fp.write(title)
        NCS = self.kargs.get('NCS',0)
        assert NCS == 0
        self.fp.write('{:>6d}\n  GRID   ISTA  IEND  JSTA  JEND  KSTA  KEND IWALL INORM\n'.format(NCS))
    def write_TRANS_block(self):
        #动网格设置
        title = '  MOVING GRID DATA - TRANSLATION\n  NTRANS\n{:>8d}\n'
        NTRANS = self.kargs.get('NTRANS',0)
        self.fp.write(title.format(NTRANS))
        if NTRANS != 0:
            pass 
        else:
            tt = '    LREF\n    GRID ITRANS   RFREQ   UTRANS   VTRANS   WTRANS\n    GRID  DXMAX   DYMAX    DZMAX\n'
            self.fp.write(tt)

    def write_ROTATE_block(self):
        #旋转网格设置
        title = '  MOVING GRID DATA - ROTATION\n  NROTAT\n{:>8d}\n'
        rotatedBlocks = self.kargs.get('rotatedBlocks',None)
        rotated_center = self.kargs.get('rotated_center',True)
        if rotated_center:
            rcenter = 1 
        else:
            rcenter = 0
        if rotatedBlocks is not None:
            NROTAT = len(rotatedBlocks)+rcenter 
        else:
            NROTAT = 0
        self.fp.write(title.format(NROTAT))
    
        if NROTAT != 0:
            rotatedBlocks = list(rotatedBlocks.items())
            rotatedBlocks.sort(key=lambda x:x[0])
            LREF = 1/self.LREF
            IROTAT = self.kargs.get('IROTAT',1)
            assert IROTAT == 1
            tt = '    LREF\n    GRID IROTAT   RFREQ   OMEGAX   OMEGAY   OMEGAZ   XORIG   YORIG   ZORIG\n    GRID   THXMAX   THYMAX   THZMAX\n'
            self.fp.write('    LREF\n{:>8.3f}\n'.format(LREF))
            self.fp.write('    GRID IROTAT   RFREQ   OMEGAX   OMEGAY   OMEGAZ   XORIG   YORIG   ZORIG\n')
            fstr = '{:>8d}{:>7d}{:>8d}{:>9.6f}{:>9.6f}{:>9.6f}'+'{:>8.5f}'*3+'\n'
            for blockId,vData in rotatedBlocks:
                xo,yo,zo = vData.get('axis',(0,0,1))
                rpm = vData['rpm']
                omega = rpm/60/self.env_acusitic_velocity
                norm0 = (xo**2+yo**2+zo**2)**0.5
                omegax = omega*xo/norm0
                omegay = omega*yo/norm0
                omegaz = omega*zo/norm0
                rfreq = 0
                self.fp.write(fstr.format(blockId,IROTAT,rfreq,omegax,omegay,omegaz,xo,yo,zo))
            if rotated_center:
                self.fp.write(fstr.format(0,IROTAT,rfreq,omegax,omegay,omegaz,xo,yo,zo))

            self.fp.write('    GRID   THXMAX   THYMAX   THZMAX\n')
            fstr = '{:>8d}'+' {:>9.6f}'*3+'\n'
            for blockId,vData in rotatedBlocks:
                xo,yo,zo = vData.get('axis',(0,0,1))
                deltaAngle = vData['max']
                norm0 = (xo**2+yo**2+zo**2)**0.5
                deltaAnglex = deltaAngle*xo/norm0
                deltaAngley = deltaAngle*yo/norm0
                deltaAnglez = deltaAngle*zo/norm0
                self.fp.write(fstr.format(blockId,deltaAnglex,deltaAngley,deltaAnglez))
            if rotated_center:
                self.fp.write(fstr.format(0,deltaAnglex,deltaAngley,deltaAnglez))

        else:
            tt = '    LREF\n    GRID IROTAT   RFREQ   OMEGAX   OMEGAY   OMEGAZ   XORIG   YORIG   ZORIG\n    GRID   THXMAX   THYMAX   THZMAX\n'
            self.fp.write(tt)

            
        
    def write_DYNAMIC_PATCH_block(self):
        patchedData = self.kargs.get('patchedData',None)
        if not (patchedData and self.kargs.get('IUNST')>0):
            return 
        ITOSS = self.kargs.get('ITOSS',0)
        ITMAX = self.kargs.get('ITMAX',0)
        if not isinstance(patchedData,str):
            patchedData = o2o.translatePatcheDataToString(self.blocks, patchedData, ITOSS, ITMAX)
        self.fp.write(patchedData.rstrip())
        self.fp.write('\n')

if __name__=='__main__':
    boundary={
        '1ke':{'bctype':2003},
        '4ke':{'bctype':2003},
        '5k0':{'bctype':2003},

        '1je':{'bctype':2004},
        '2je':{'bctype':2004},
        '3je':{'bctype':2004},
        '4je':{'bctype':2004},
        '5je':{'bctype':2004},

        '1j0':{'bctype':2004},
        '2j0':{'bctype':2004},
        '3j0':{'bctype':2004},
        '4j0':{'bctype':2004},
        '5j0':{'bctype':2004},

        '3i0':{'bctype':2004},

        '6je':{'bctype':-2004},
        '7je':{'bctype':-2004},
        '8je':{'bctype':-2004},
        '9je':{'bctype':-2004},
        '10je':{'bctype':-2004},

        '6j0':{'bctype':2004},
        '7j0':{'bctype':2004},
        '8j0':{'bctype':2004},
        '9j0':{'bctype':2004},
        '10j0':{'bctype':2004},

        '8i0':{'bctype':2004},

        '12k0':{'bctype':2002,'pressure':None},
        '14k0':{'bctype':2002,'pressure':None},
        '15ke':{'bctype':2002,'pressure':None},

        '15je':{'bctype':2004},
        '11je':{'bctype':2004},
        '12je':{'bctype':2004},
        '13je':{'bctype':2004},
        '14je':{'bctype':2004},

        '15j0':{'bctype':2004},
        '11j0':{'bctype':2004},
        '12j0':{'bctype':2004},
        '13j0':{'bctype':2004},
        '14j0':{'bctype':2004},

        '13i0':{'bctype':2004},

    }
    t = plot3d.read( '/home/yxs/F/pythonAPP/cfl3d_pyui/test_work/mesh_no_gap.g')

    k = o2o.one2one(t,periodic_faces=[((8,'IE'),(10,'IE'),True),((3,'IE'),(4,'IE'),True),((14,'IE'),(15,'IE'),True)])
    
    p1 = o2o.PatchedInterfaceRotated(t,[(14,'Ie'),], [(15,'Ie'),],0,0,True)
    p2 = o2o.PatchedInterfaceRotated(t,[(1,'K0'),(3,'K0'),(4,'Ke')], [(5,'Ke'),(8,'Ke'),(9,'Ie')],0,1)
    p3 = o2o.PatchedInterfaceRotated(t,[(11,'Ke'),(14,'Ke'),(15,'K0')], [(6,'K0'),(8,'K0'),(10,'Ke')],0,1)
    ttt = 2*math.pi
    print(p2[0][1]/3.1415926*180,'degree',ttt/p2[0][1])
    print(p2[1][1]/3.1415926*180,'degree',ttt/p2[1][1])
    print(p3[0][1]/3.1415926*180,'degree',ttt/p3[0][1])

    patchedData = o2o.patched([[o2o.BlockIdPlus(t) for t in p] for p in [p1,p2,p3]])

    blocks, oneData, patchedData = o2o.MergeBlocks(t,9,10,k,patchedData)

    rotatedBlocks={
        6:{'axis':(0,0,1),'max':14.4, 'rpm':10.},
        7:{'axis':(0,0,1),'max':14.4, 'rpm':10.},
        8:{'axis':(0,0,1),'max':14.4, 'rpm':10.},
        9:{'axis':(0,0,1),'max':14.4, 'rpm':10.},
        10:{'axis':(0,0,1),'max':14.4,'rpm':10.},
        11:{'axis':(0,0,1),'max':14.4,'rpm':10.},
    }
    #存在的问题，转子上壁面应该是一个绝对静止的无滑移边条，但是现在给的是一个bc2004边条
    #如果速度还有问题
    #在numeca上计算一个动网格算列
    a = inputFile(
        workdir='/home/yxs/F/pythonAPP/cfl3d_pyui/rotate_work',
        gridfile = blocks,
        input_filename='rotate5.inp',
        iterations=90,
        LREF = 1.0/1000,
        CFL_number=2,
        in_x_velocity = 0,in_y_velocity=0,in_z_velocity=200,
        in_density = 1.2,in_viscosity=1.716e-5,
        turbulence_model=5,
        output_pressure = 106000,
        I2D = 0,IUNST=1,MOVIE=100,rotated_center=True,NWREST=100,
        number_of_time_step=10000,time_step = 0.00005,
        BOUNDARY = boundary,
        oneOne = oneData,
        patchedData = patchedData,ITOSS = 0,ITMAX = 500,
        rotatedBlocks = rotatedBlocks,
        # restart_file = '/home/yxs/F/pythonAPP/cfl3d_pyui/rotate_work/rotate_restart.bin',
        ITA = -2,
        NCG = 0,
        init_file='/home/yxs/F/learning/CFL3D/323_0409/numeca_0409_323_steady/new_grid_323_0409_nogap/323_0409_steady/323_0409_steady/323_0409_steady_323_0411_STEADY/323_0409_steady_323_0411_STEADY.q',

    )
    a.start_write()
