def save(obj, filename, format_, path_dir) :
    """
    Save an arbitrary object with the specified filename and format_ in the path_dir
    """

    import os, sys

    if os.path.isdir(path_dir)==False:
        os.makedirs(path_dir)

    if format_ == 'h5':

        import h5py

        path_save_file = os.path.join(path_dir, filename+'.h5' )

        file = h5py.File(path_save_file, 'w')
        file.create_dataset(filename, data=obj)
        file.close()

    elif format_ == 'csv':

        import numpy as np

        path_save_file = os.path.join(path_dir,filename+'.csv')

        if type(obj)==np.ndarray:
            np.savetxt(path_save_file, obj, delimiter=',')
        else:
            obj.to_csv(path_save_file, index=False)

    elif format_ == 'json':

        import json
        path_save_file = os.path.join(path_dir, filename+'.json')
        file = open(path_save_file, 'w')
        json.dump(obj, file)
        file.close()

    elif format_ == 'dill':
        import dill
        path_save_file = os.path.join(path_dir, filename+'.dill')
        file = open(path_save_file, 'wb')
        dill.dump(obj, file)
        file.close()
        
    elif format_ =='h5_csv': #try saving as h5, otherwise save as csv
        try:
            import h5py

            path_save_file = os.path.join(path_dir, filename+'.h5' )

            file = h5py.File(path_save_file, 'w')
            file.create_dataset(filename, data=obj)
            file.close()
        except:
            file.close()
            os.remove(path_save_file)
            
            import numpy as np

            path_save_file = os.path.join(path_dir,filename+'.csv')

            if type(obj)==np.ndarray:
                np.savetxt(path_save_file, obj, delimiter=',')
            else:
                obj.to_csv(path_save_file, index=False)
            


def load(filename, format_, path_dir, header='infer'):
    
    """
    Load an arbitrary object with the specified filename and format_ in the path_dir
    """
    
    import os, sys

    if format_ == 'h5': 

        import h5py

        path_save_file = os.path.join(path_dir, filename+'.h5')
        file = h5py.File(path_save_file, 'r')
        obj = file[filename][:]
        file.close()

    elif format_ == 'csv':

        import pandas as pd

        path_save_file = os.path.join(path_dir, filename+'.csv')
        obj = pd.read_csv(path_save_file, low_memory = False, header = header)

    elif format_ == 'json':
        import json
        path_save_file = os.path.join(path_dir, filename+'.json')
        file = open(path_save_file, 'r')
        obj = json.load(file)
        file.close()

    elif format_ == 'dill':
        import dill
        path_save_file = os.path.join(path_dir, filename+'.dill')
        file = open(path_save_file, 'rb')
        obj = dill.load(file)
        file.close()
        
    elif format_ =='h5_csv': #try loading as h5, otherwise save as csv
        try:
            import h5py

            path_save_file = os.path.join(path_dir, filename+'.h5')
            file = h5py.File(path_save_file, 'r')
            obj = file[filename][:]
            file.close()
        except:
            import pandas as pd

            path_save_file = os.path.join(path_dir, filename+'.csv')
            obj = pd.read_csv(path_save_file, low_memory = False, header = header)



    return obj