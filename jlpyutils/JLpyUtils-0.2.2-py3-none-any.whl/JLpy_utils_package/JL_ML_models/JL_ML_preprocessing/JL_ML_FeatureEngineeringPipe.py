def save_X_X_field(X, X_field, path_feat_eng_case_dir, overwrite = False, format_ = 'h5'):
    
    if os.path.isdir(path_feat_eng_case_dir)==False:
        os.makedirs(path_feat_eng_case_dir)
        
    if format_ == 'h5':    
        
        path_save_file = os.path.join(path_feat_eng_case_dir,'X_field.h5')
        if os.path.isfile(path_save_file)==False or overwrite ==True: 
            file = h5py.File(path_save_file, 'w')
            file.create_dataset('X_field', data=X_field)
            file.close()

        path_save_file = os.path.join(path_feat_eng_case_dir,'X.h5')
        if os.path.isfile(path_save_file)==False or overwrite ==True: 
            file = h5py.File(path_save_file, 'w')
            file.create_dataset('X', data=X_field)
            file.close()
            
    elif format_ == 'csv':
        
        path_save_file = os.path.join(path_feat_eng_case_dir,'X_field.csv')
        if os.path.isfile(path_save_file)==False or overwrite ==True: 
            X_field.to_csv(path_save_file,index=False)

        path_save_file = os.path.join(path_feat_eng_case_dir,'X.csv')
        if os.path.isfile(path_save_file)==False or overwrite ==True: 
            X.to_csv(path_save_file, index=False)

        
def load_X_X_field(path_feat_eng_case_dir, format_ = 'h5'):
    
    if format_ == 'h5': 
        
        path_save_file = os.path.join(path_feat_eng_case_dir,'X_field.h5')
        file = h5py.File(path_save_file, 'r')
        X_field = file['X_field'][:]
        file.close()

        path_save_file = os.path.join(path_feat_eng_case_dir, 'X.h5')
        file = h5py.File(path_save_file, 'r')
        X = file['X'][:]
        file.close()
        
    elif format_ == 'csv':
        
        path_save_file = os.path.join(path_feat_eng_case_dir,'X_field.csv')
        X_field = pd.read_csv(path_save_file,low_memory = False)

        path_save_file = os.path.join(path_feat_eng_case_dir,'X.csv')
        X = pd.read_csv(path_save_file,low_memory = False)

    return X, X_field

def check_for_existing_X_X_field_files(path_feat_eng_case_dir, format_ = 'h5'):
    all_data_found=True
    
    if format_=='h5':
        files = ['X.h5', 'X_field.h5']
        
    elif format_=='csv':
        files = ['X.csv', 'X_field.csv']
        
    for file in files:
        path_save_file = os.path.join(path_feat_eng_case_dir,file)
        if os.path.isfile(path_save_file)==False:
            all_data_found = False
    return all_data_found
        

def train_test_split_save(X, y, test_size = 0.33, path_save_dir= '.', format_ = 'npy'):
    arr_rand = np.random.rand(X.shape[0])
    split = arr_rand < np.percentile(arr_rand, int((1-test_size)*100))
    
    if format_ == 'npy':
        np.save(os.path.join(path_save_dir,'X_train'), X[split])
        np.save(os.path.join(path_save_dir,'y_train'), y[split])

        np.save(os.path.join(path_save_dir,'X_test'), X[~split])
        np.save(os.path.join(path_save_dir,'y_test'), y[~split])
        
    elif format_ == 'h5':
        file = h5py.File(os.path.join(path_save_dir,'X_train.h5'), 'w')
        file.create_dataset('X_train', data=X[split])
        file.close()
        
        file = h5py.File(os.path.join(path_save_dir,'y_train.h5'), 'w')
        file.create_dataset('y_train', data=y[split])
        file.close()
        
        file = h5py.File(os.path.join(path_save_dir,'X_test.h5'), 'w')
        file.create_dataset('X_test', data=X[~split])
        file.close()
        
        file = h5py.File(os.path.join(path_save_dir,'y_test.h5'), 'w')
        file.create_dataset('y_test', data=y[~split])
        file.close()
    

def Build_and_save_feat_eng_case_datasets(X, y,
                                          X_field, 
                                          headers_dict, 
                                          Scalers_dict, ScalerID,
                                          Imputer_categorical_ID, categorical_estimatorID,
                                          Imputer_continuous_ID, continuous_estimatorID, 
                                          OneHot_case,
                                          path_report_dir,
                                          verbose = 0,
                                          overwrite = False
                                          ):
    #build feat_eng_case_dir
    path_feat_eng_case_dir = os.path.join(path_report_dir,
                                          'ScalerID['+ScalerID+']',
                                          'Imputer_categorical_ID['+Imputer_categorical_ID+']',
                                          'categorical_estimatorID['+str(categorical_estimatorID)+']',
                                          'Imputer_continuous_ID['+Imputer_continuous_ID+']',
                                          'continuous_estimatorID['+str(continuous_estimatorID)+']',
                                          'OneHot_case['+str(OneHot_case)+']')
    if os.path.isdir(path_feat_eng_case_dir)==False:
        os.makedirs(path_feat_eng_case_dir)
    
    #check if all the required files are saved in the dir
    all_data_previously_saved = True
    for file in ['X_field.h5', 'X_test.h5', 'y_test.h5', 'X_train.h5', 'y_train.h5', 'headers_dict.json']:
        path_save_file = os.path.join(path_feat_eng_case_dir, file)
        if os.path.isfile(path_save_file)==False:
            all_data_previously_saved = False
    if all_data_previously_saved==False or overwrite == True: 
        X = X.copy()
        X_field = X_field.copy()
        headers_dict = headers_dict.copy()
        
        ####### Scale #########
        if verbose>=1: print('\n----Scale:',ScalerID,'-----')
        
        path_feat_eng_case_dir = os.path.join(path_report_dir, 'ScalerID['+ScalerID+']')
        format_ = 'csv'
        if check_for_existing_X_X_field_files(path_feat_eng_case_dir, format_ = format_ )==False or overwrite==True:

            X, Scaler = Scale.continuous_features(X, headers_dict, Scaler = Scalers_dict[ScalerID])

            X_field[headers_dict['continuous_features']] = Scaler.transform(X_field[headers_dict['continuous_features']])
            assert(X_field.shape[1] == X.shape[1]),'X and X_field have different number of columns (X_field.shape[1]:'+str(X_field.shape[1])+', X.shape[1]:'+X.shape[1]+')'
            
            #save
            save_X_X_field(X, X_field, path_feat_eng_case_dir, overwrite = overwrite, format_ = format_)
            
        else:
            X, X_field = load_X_X_field(path_feat_eng_case_dir, format_ =format_)
            
        ####### Impute Categorical Features #########
        if verbose>=1: print('\n----Impute Categorical Features:',Imputer_categorical_ID,'[',categorical_estimatorID,']. n_features:',X.shape[0],'----')
        
        path_feat_eng_case_dir = os.path.join(path_feat_eng_case_dir, 
                                              'Imputer_categorical_ID['+Imputer_categorical_ID+']',
                                              'categorical_estimatorID['+str(categorical_estimatorID)+']')
        format_ = 'csv'
        if check_for_existing_X_X_field_files(path_feat_eng_case_dir, format_ = format_ )==False or overwrite==True:
            #fetch the estimator object of interest if using iterative
            if Imputer_categorical_ID == 'iterative':
                categorical_iterative_estimator = Impute.fetch_iterative_estimators_dict(n_features = X.shape[0])[categorical_estimatorID]
            else:
                categorical_iterative_estimator = None

            X, headers_dict, Imputer = Impute.categorical_features(X, 
                                                                    headers_dict, 
                                                                    strategy = Imputer_categorical_ID, 
                                                                    estimator = categorical_iterative_estimator,
                                                                    verbose= 0)
            
            X_field[headers_dict['categorical_features']] = Imputer.transform(X_field[headers_dict['categorical_features']])
            assert(X_field.shape[1] == X.shape[1]),'X and X_field have different number of columns (X_field.shape[1]:'+str(X_field.shape[1])+', X.shape[1]:'+X.shape[1]+')'
            
            #save
            save_X_X_field(X, X_field, path_feat_eng_case_dir, overwrite = overwrite, format_ = format_)
            
        else:
            X, X_field = load_X_X_field(path_feat_eng_case_dir, format_ =format_)
            
        ###### Impute Continuous Features ########
        if verbose>=1: print('\n----Impute continuous Features:',Imputer_continuous_ID,'[',continuous_estimatorID,']. n_features:',X.shape[0],'----')
        
        path_feat_eng_case_dir = os.path.join(path_feat_eng_case_dir, 
                                              'Imputer_continuous_ID['+Imputer_continuous_ID+']',
                                              'continuous_estimatorID['+str(continuous_estimatorID)+']')
        format_ = 'csv'
        if check_for_existing_X_X_field_files(path_feat_eng_case_dir, format_ = format_ )==False or overwrite==True:
            #fetch the estimator object of interest if using iterative
            if Imputer_continuous_ID == 'iterative':
                continuous_iterative_estimator = Impute.fetch_iterative_estimators_dict(n_features = X.shape[0])[continuous_estimatorID]
            else:
                continuous_iterative_estimator = None

            X, headers_dict, Imputer = Impute.continuous_features(X, 
                                                                    headers_dict, 
                                                                    strategy = Imputer_continuous_ID, 
                                                                    estimator = continuous_iterative_estimator,
                                                                    verbose= 0)
            X_field[headers_dict['continuous_features']] = Imputer.transform(X_field[headers_dict['continuous_features']])
            assert(X_field.shape[1] == X.shape[1]),'X and X_field have different number of columns (X_field.shape[1]:'+str(X_field.shape[1])+', X.shape[1]:'+X.shape[1]+')'
            
            #save
            save_X_X_field(X, X_field, path_feat_eng_case_dir, overwrite = overwrite, format_ = format_)
            
        else:
            X, X_field = load_X_X_field(path_feat_eng_case_dir, format_ =format_)
            
        ##### One Hot Encode #####
        path_feat_eng_case_dir = os.path.join(path_feat_eng_case_dir, 'OneHot_case['+str(OneHot_case)+']')
        
        format_ = 'h5'
        if check_for_existing_X_X_field_files(path_feat_eng_case_dir, format_ = format_ )==False or overwrite==True:
            
            if verbose>=1: print('\n----One Hot Encode:','[',OneHot_case,']. n_features:',X.shape[0],'----')

            if OneHot_case:
                return_format='npArray'
                X, headers_dict, OneHotEncoder = OneHotEncode.categorical_features(X, 
                                                                                    headers_dict,
                                                                                    return_format=return_format)
                X_field, headers_dict = OneHotEncode.transform(X_field, headers_dict, OneHotEncoder, return_format)
            else:
                headers_dict['headers_after_OneHot'] = list(X.columns)
                X = np.array(X)
                X_field = np.array(X_field) 
            assert(X_field.shape[1] == X.shape[1]),'X and X_field have different number of columns (X_field.shape[1]:'+str(X_field.shape[1])+', X.shape[1]:'+X.shape[1]+')'
            
            #save
            save_X_X_field(X, X_field, path_feat_eng_case_dir, overwrite = overwrite, format_ = format_)
            
        else:
            X, X_field = load_X_X_field(path_feat_eng_case_dir, format_ =format_)
        
        headers_dict['headers_after_feat_eng'] = headers_dict['headers_after_OneHot']
        
        if verbose>=1:print('\n----final n_features:',X.shape[0],'----')

        print('\npath_feat_eng_case_dir:', path_feat_eng_case_dir)


        #train test split
        if verbose>=1: print('\n----train-test split-----')

        #run very simple train test split with saving (no loading to memory) to prevent crashing
        all_train_test_data_saved=True
        for file in ['X_test.h5','y_test.h5','X_train.h5','y_train.h5']:
            path_save_file = os.path.join(path_feat_eng_case_dir,file)
            if os.path.isfile(path_save_file)==False:
                all_train_test_data_saved = False

        if all_train_test_data_saved==False or overwrite ==True: 
            train_test_split_save(X, y, 
                                    test_size = 0.33, 
                                    path_save_dir = path_feat_eng_case_dir,
                                    format_ = 'h5')

        #save the headers dict
        path = os.path.join(path_feat_eng_case_dir,'headers_dict.json')
        if os.path.isfile(path)==False or overwrite ==True: 
            file = open(path, 'w')
            json.dump(headers_dict, file)
            file.close()

        del X, y, X_field

        print('...feature engineering case datasets saved')
    else:
        print('\n pre-existing saved data found at path_feat_eng_case_dir:', path_feat_eng_case_dir)
        print('...moving to next feature engineering case')

def run(df, df_field, path_report_dir = './outputs', verbose = 1, overwrite=False):
    """
    Arguments:
        df: pandas dataframe containing features and labels of interest
        df_field: pandas dataframe containing field data for which the labels are unknown.
    """
    
    df = df.copy()
    df_field = df_field.copy()
    
    if verbose>=2: 
        print('df.info():')
        df.info()
        print('\ndf_field.info():')
        df_field.info()
    
    headers_dict = fetch_headers_dict()
    
    #drop the unique ID columns
    df = df.drop(columns=[headers_dict['UID']])
    df_field = df_field.drop(columns=[headers_dict['UID']])
    
    path_feat_eng_case_dir = os.path.join(path_report_dir, 'feature_engineering_tree')
    if check_for_existing_X_X_field_files(path_feat_eng_case_dir, format_ = 'h5')==False or overwrite==True:

        #slice out features and labels
        X = df[headers_dict['features']];
        y = df[headers_dict['labels']];
        del df

        X_field =  df_field[headers_dict['features']]; del df_field
        
        # save
        save_X_X_field(X, X_field, path_feat_eng_case_dir, overwrite = overwrite, format_ = 'csv')
    else:
        X, X_field = load_X_X_field(path_feat_eng_case_dir, format_ = 'csv')
    
    if verbose>=1: print('\n----LabelEncode-----')
                        
    #label encode X
    path_feat_eng_case_dir = os.path.join(path_feat_eng_case_dir, 'LabelEncode')
    if check_for_existing_X_X_field_files(path_feat_eng_case_dir, format_ = 'h5')==False or overwrite==True:
        X, headers_dict, LabelEncoders = LabelEncode.categorical_features(X, headers_dict, verbose = 0)

        #label encode field data
        X_field = LabelEncode.transform(X_field, LabelEncoders)
        
        #save
        save_X_X_field(X, X_field, path_feat_eng_case_dir, overwrite = overwrite, format_ = 'csv')
    else:
        X, X_field = load_X_X_field(path_feat_eng_case_dir, format_ = 'csv')
        
    Scalers_dict = Scale.fetch_Scalers_dict()
    for ScalerID in Scalers_dict.keys():

        #impute categorical features
        for Imputer_categorical_ID,  categorical_iterative_estimators in [['most_frequent',[None]],
                                                                          ['iterative', list(Impute.fetch_iterative_estimators_dict(1).keys())]]:

            for categorical_estimatorID in categorical_iterative_estimators:

                #impute continuous features
                for Imputer_continuous_ID,  continuous_iterative_estimators in [['mean',{None:None}],
                                                                                     ['median',{None:None}],
                                                                                     ['iterative', list(Impute.fetch_iterative_estimators_dict(1).keys())]]:

                    for continuous_estimatorID in continuous_iterative_estimators:

                        #One Hot Encode:
                        for OneHot_case in [True, False]:

                            Build_and_save_feat_eng_case_datasets(X, y,
                                  X_field, 
                                  headers_dict, 
                                  Scalers_dict, ScalerID,
                                  Imputer_categorical_ID, categorical_estimatorID,
                                  Imputer_continuous_ID, continuous_estimatorID, 
                                  OneHot_case,
                                  path_report_dir = path_feat_eng_case_dir,
                                  verbose = verbose,
                                  overwrite = overwrite)
                            

    print('----!Finished!-----')