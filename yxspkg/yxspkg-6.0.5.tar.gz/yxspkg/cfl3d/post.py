import postprocessing 
from yxspkg import tecfile 

if __name__=='__main__':
    cfl3d_case = '/home/yxs/F/learning/CFL3D/323_0409/ok/series/323_new_bound_0001/rotate323_0409_lref1_output.szplt'
    numeca_case='/home/yxs/F/learning/CFL3D/323_0409/ok/new_grid_323_0409_nogap/323_0409_steady/323_0409_steady/323_0409_steady_323_0411_STEADY_Frozen_106/323_0409_steady_323_0411_STEADY_Frozen_106.szplt'
    f = tecfile.read(numeca_case)
    postprocessing.cal_average(f)