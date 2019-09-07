
import tensorflow as __tf__


def Conv2D(img_shape = (256, 256, 3),
              batch_size = None ,
              n_outputs_per_img = 2,
              layers_per_group =  1,
              initial_filter_size = 16,
              max_filter_size = 512,
              filter_scaling_factor = 2,
              dense_scaling_factor = 20,
              kernel_size = (2,2),
              activation = __tf__.keras.layers.LeakyReLU(),
              pooling_layer = __tf__.keras.layers.MaxPool2D,
              pool_size = (2,2),
              batch_norm_rate = None,
              dropout_layer_rate = None,
              dropout_rate = 0.5,
              loss= __tf__.keras.losses.categorical_crossentropy,
              learning_rate = 0.001,
              optimizer= __tf__.keras.optimizers.Adam,
              metrics=['accuracy'],
              debug=False,
              verbose = 0):
    """
        Arguments:
            hyperparams_dict: Dictionary containing hyperparameters used to define neural net structure. 
                layers_per_group: how many Conv2D layers stacked back to back before each pooling operation
                initial_filter_size: size of first filter for first conv layer (i.e. the image has 3 colors channels & if 0th filter size is 64, this will be expanded to 64 channels)
                max_filter_size: upper limit on Conv2D filter size. After this limit is reach, the Conv2D layer will be flattened for input into the dense net  
                filter_scaling_factor: the multiplicative factor the filter size will be increased by for each group of conv2D layers
                dense_scaling_factor: the multiplicative factor the dense net units (following the conv net groups) will be decreased by for each group of Dense layers
                kernel_size: kernel size for Conv2D layers
                activation: activation function to be used
                pooling_layer: the type of pooling layer to be used (must be keras.layer method)
                batch_norm_rate: The rate at which a batch norm layer will be inserted. i.e. for a value of 2, a batch norm layer will be inserted on every other group of layers
                dropout_layer_rate: similar to batch_norm_rate, this defines the how often a dropout layer is inserted into a given group of layers
                dropout_rate: the number of nodes to be dropped in a given dropout layer
        """
    
    def compiler(img_shape = (256, 256, 3),
                  batch_size = None ,
                  n_outputs_per_img = 2,
                  layers_per_group =  1,
                  initial_filter_size = 16,
                  max_filter_size = 512,
                  filter_scaling_factor = 2,
                  dense_scaling_factor = 20,
                  kernel_size = (2,2),
                  activation = layers.LeakyReLU(),
                  pooling_layer = layers.MaxPool2D,
                  pool_size = (2,2),
                  batch_norm_rate = None,
                  dropout_layer_rate = None,
                  dropout_rate = 0.5,
                  loss=keras.losses.categorical_crossentropy,
                  learning_rate = 0.001,
                  optimizer=keras.optimizers.Adam,
                  metrics=['accuracy'],
                  debug=False,
                  verbose = 0):
        tf.reset_default_graph()
        keras.backend.clear_session()

        model_dict = {}

        model_dict['inputs'] = layers.Input(shape= img_shape, 
                                            batch_size= batch_size,
                                            dtype = tf.float32,
                                            name = 'inputs')

        flat_length = np.inf
        g = 0 #group index
        idx_dict = {'batch_norm_rate':0,
                    'dropout_layer_rate':0}

        #define function to apply batch norm and dropouts at appropriate group iteratation
        BatchNorm_Dropout_dict = {'batch_norm_rate':batch_norm_rate,
                                  'dropout_layer_rate': dropout_layer_rate,
                                  'dropout_rate':dropout_rate}

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

        #build groups of conv2d, batch norm, dropout, and pooling layers
        filters = initial_filter_size
        xy_shape = np.inf
        while filters <= max_filter_size and xy_shape != 1:
            for gl in range(layers_per_group):  #group layer index
                name = 'G'+str(g)+'_L'+str(gl)+'_Conv2D'
                model_dict[name] = layers.Conv2D(filters = filters, 
                                                   kernel_size = kernel_size, 
                                                   padding='same', 
                                                   activation=activation, 
                                                   kernel_initializer='glorot_uniform', 
                                                   bias_initializer='zeros',
                                                   name = name
                                                  )(model_dict[list(model_dict.keys())[-1]])
                if debug: print(name, model_dict[name])

            gl+=1
            model_dict, BatchNorm_Dropout_dict, idx_dict, g, gl = Apply_BatchNorm_Dropouts(model_dict, BatchNorm_Dropout_dict, idx_dict, g, gl)

            name = 'G'+str(g)+'_L'+str(gl)+'_Pool'
            model_dict[name] = pooling_layer(pool_size = pool_size,
                                                                 name = name
                                                                )(model_dict[list(model_dict.keys())[-1]])

            if debug: print(name, model_dict[name])
            gl+=1

            xy_shape = (model_dict[list(model_dict.keys())[-1]]).shape[1]
            if debug: print('xy_shape:',xy_shape)

            filters = int(filters * filter_scaling_factor)

            flat_length = layers.Flatten()(model_dict[list(model_dict.keys())[-1]]).shape[1]
            if debug: print('flat_length:',flat_length)

            g+=1

        #flatten the conv groups output
        gl=0
        name = 'G'+str(g)+'_L'+str(gl)+'_Flatten'
        model_dict[name] = layers.Flatten(name = name)(model_dict[list(model_dict.keys())[-1]])
        g+=1; gl+=1

        #build dense net layers
        units = int(int(flat_length)/dense_scaling_factor)

        while units > n_outputs_per_img:
            gl=0
            for gl in range(layers_per_group):  #group layer index
                name = 'G'+str(g)+'_L'+str(gl)+'_Dense'
                model_dict[name]= layers.Dense(units, 
                                               activation=activation, 
                                               kernel_initializer='glorot_uniform', 
                                               bias_initializer='zeros',
                                               name = name
                                              )(model_dict[list(model_dict.keys())[-1]])
                gl+=1 
                model_dict, BatchNorm_Dropout_dict, idx_dict, g, gl = Apply_BatchNorm_Dropouts(model_dict, BatchNorm_Dropout_dict, idx_dict, g, gl)

            units = units/dense_scaling_factor
            g+=1

        gl=0
        name = 'outputs'
        model_dict[name] = layers.Dense(n_outputs_per_img,
                                               activation = 'softmax',
                                               kernel_initializer='glorot_uniform', 
                                               bias_initializer='zeros',
                                              name = name
                                              )(model_dict[list(model_dict.keys())[-1]])
        model = keras.Model(inputs = model_dict['inputs'],
                                                outputs = model_dict['outputs'])
        model.compile(loss=loss,
                      optimizer=optimizer(lr=learning_rate),
                      metrics=metrics)
        return model
    
    model = compiler(img_shape,
                          batch_size  ,
                          n_outputs_per_img,
                          layers_per_group,
                          initial_filter_size,
                          max_filter_size,
                          filter_scaling_factor,
                          dense_scaling_factor,
                          kernel_size,
                          activation ,
                          pooling_layer,
                          pool_size ,
                          batch_norm_rate,
                          dropout_layer_rate,
                          dropout_rate ,
                          loss,
                          learning_rate,
                          optimizer,
                          metrics,
                          debug,
                          verbose)
    
    models_dict = {}
    models_dict['Conv2D'] = {}
    models_dict['Conv2D']['compiler'] = compiler
    models_dict['Conv2D']['model']= model
    if verbose >=1:
        print("\t---- models_dict['Conv2D']['model'].summary()----")
        models_dict['Conv2D']['model'].summary()

    #define default param grid for gridsearch
    models_dict['Conv2D']['param_grid'] = {'img_shape': [img_shape],
                                           'batch_size' : [batch_size],
                                           'n_outputs_per_img': [n_outputs_per_img],
                                           'layers_per_group': [1,2],
                                           'initial_filter_size': [16, 32, 64],
                                           'max_filter_size': [128, 256, 512, 1024],
                                           'filter_scaling_factor': [2, 3, 4],
                                           'dense_scaling_factor': [10,20,100, 1000],
                                           'kernel_size': [(2,2),(3,3),(4,4)],
                                           'activation': ['relu', 'elu'], #can't save models using layers.LeakyReLU()
                                           'pooling_layer': [layers.MaxPool2D, layers.AvgPool2D],
                                           'pool_size': [(2,2), (3,3), (4,4)],
                                           'batch_norm_rate': [None, 1, 2, 3],
                                           'dropout_layer_rate': [None, 1, 2, 3],
                                           'dropout_rate': [0.9,0.5,0.1],
                                           'loss': [loss],
                                           'learning_rate': [0.01, 0.001, 0.0001],
                                           'optimizer':[optimizer],
                                           'metrics': [metrics]}
    
    
    return models_dict

# model.compile(loss=keras.losses.categorical_crossentropy,
#               optimizer=keras.optimizers.Adam(lr=0.001),
#               metrics=['accuracy'])
# epochs = 10000
# history = model.fit_generator(generator = img_gen_train, 
#                               epochs = epochs,
#                               validation_data = img_gen_test,
#                               workers=-1,
#                               use_multiprocessing=True,
#                               verbose = 2)