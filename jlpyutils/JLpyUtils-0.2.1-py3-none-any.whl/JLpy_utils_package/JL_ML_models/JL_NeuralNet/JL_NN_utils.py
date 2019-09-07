import tensorflow as tf
import tensorflow.keras as keras
import tensorflow.keras.preprocessing
import tensorflow.keras.layers as layers

def Apply_BatchNorm_Dropouts(model_dict, BatchNorm_Dropout_dict, idx_dict, g, gl):
    for [layer_name, key, layer] in [['BatchNorm', 'batch_norm_rate' ,
                                      layers.BatchNormalization(name = 'G'+str(g)+'_L'+str(gl)+'_'+'BatchNorm')], 
                                     ['Dropout'  , 'dropout_layer_rate', 
                                      layers.Dropout(BatchNorm_Dropout_dict['dropout_rate'],
                                                     name = 'G'+str(g)+'_L'+str(gl+1)+'_'+'Dropout')]]:
        if BatchNorm_Dropout_dict[key]!=None:
            if idx_dict[key] % BatchNorm_Dropout_dict[key] == 0:
                name = 'G'+str(g)+'_L'+str(gl)+'_'+layer_name
                model_dict[name] = layer(model_dict[list(model_dict.keys())[-1]])
                idx_dict[key]=0
            idx_dict[key]+=1
            gl+=1
    return model_dict, BatchNorm_Dropout_dict, idx_dict, g, gl