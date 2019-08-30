import logging
import os
import pandas as pd
import time

from auger_ml.FSClient import FSClient
from auger_ml.data_source.data_source_api_pandas import DataSourceAPIPandas
from auger_ml.data_splitters.XYNumpyDataPrep import XYNumpyDataPrep
from auger_ml.Utils import remove_dups_from_list


class ModelExporter(object):
    def __init__(self, options):
        self.options = options

    def load_model(self, model_path):
        from auger_ml.preprocessors.space import ppspace_is_timeseries_model

        model = FSClient().loadObjectFromFile(os.path.join(model_path, "model.pkl.gz"))

        options = FSClient().readJSONFile(os.path.join(model_path, "options.json"))
        timeseries_model = options.get('timeSeriesFeatures') and ppspace_is_timeseries_model(options.get('algorithm_name'))

        return model, timeseries_model

    def preprocess_data(self, model_path, data_path=None, records=None, features=None, predict_value_num=None):
        from auger_ml.AugerMLPreprocessors import AugerMLPreprocessors
        from auger_ml.preprocessors.space import ppspace_is_timeseries_model, pspace_get_fold_group_names

        options = FSClient().readJSONFile(os.path.join(model_path, "options.json"))

        options['featureColumns'] = options.get('originalFeatureColumns')
        data_features = options['featureColumns'][:]
        if options.get('timeSeriesFeatures'):
            data_features.extend(options.get('timeSeriesFeatures'))
            data_features.append(options.get('targetFeature'))

        data_features = remove_dups_from_list(data_features)

        if features is None:
            features = data_features

        if data_path:
            ds = DataSourceAPIPandas({'data_path': data_path})
            ds.load(use_cache=False)
        else:
            ds = DataSourceAPIPandas({})
            ds.load_records(records, features=features, use_cache=False)

        if set(data_features).issubset(set(ds.columns)):
            #print("TEST: %s, %s"%(data_features, ds.columns))
            ds.df = ds.df[data_features]
        else:
            raise Exception("Prediction data missing columns:%s"%(set(data_features)-set(ds.columns)))

        transforms = FSClient().readJSONFile(os.path.join(model_path, "transformations.json"))
        ds.transform(transforms, cache_to_file=False)

        X_test, Y_test = None, None
        if options.get('timeSeriesFeatures'):

            if predict_value_num is not None:
                if predict_value_num == len(ds.df):
                    return None, None, None

                ds.df = ds.df.iloc[:(predict_value_num + 1)]  # truncate dataset

            pp = AugerMLPreprocessors(options)
            pp.transform_predicted_data(ds, model_path)

            X_test, Y_test = XYNumpyDataPrep(options).split_predict_timeseries(ds.df)

        else:
            X_test = {}
            if options.get('ensemble', False):
                fold_groups = pspace_get_fold_group_names(options.get('timeSeriesFeatures'))
                for fold_group in fold_groups:
                    options['fold_group'] = fold_group

                    ds2 = DataSourceAPIPandas(options)
                    ds2.df = ds.df.copy()

                    pp = AugerMLPreprocessors(options)
                    pp.transform_predicted_data(ds2, model_path)
                    X_test[fold_group] = XYNumpyDataPrep(options).split_predict(ds2.df)
            else:
                pp = AugerMLPreprocessors(options)
                pp.transform_predicted_data(ds, model_path)
                X_test = XYNumpyDataPrep(options).split_predict(ds.df)

        target_categoricals = FSClient().readJSONFile(os.path.join(model_path, "target_categoricals.json"))

        return X_test, Y_test, target_categoricals
                
    def predict_by_model(self, model_path, path_to_predict=None, records=None, features=None, threshold=None, predict_value_num=None):
        from auger_ml.preprocessors.space import ppspace_is_timeseries_model

        model, timeseries_model = self.load_model(model_path)
        X_test, Y_test, target_categoricals = self.preprocess_data(model_path, 
            data_path=path_to_predict, records=records, features=features, predict_value_num=predict_value_num)

        if X_test is None:
            return None

        options = FSClient().readJSONFile(os.path.join(model_path, "options.json"))

        ds = DataSourceAPIPandas({'data_path': path_to_predict})
        if options.get('timeSeriesFeatures'):
            if ppspace_is_timeseries_model(options.get('algorithm_name')):
                results = model.predict((X_test, Y_test, False))[-1:]
            else:
                results = model.predict(X_test.iloc[-1:])

            ds.df = pd.DataFrame({
                options['targetFeature']: results,
                options['timeSeriesFeatures'][0]: X_test.index[-1:]
            })
        else:
            results = None
            results_proba = None
            proba_classes = None
            try:
                if threshold:
                    if hasattr(model, 'predict_proba') and callable(getattr(model, 'predict_proba')):
                        try:
                            results_proba = model.predict_proba(X_test)
                        except AttributeError as e:
                            logging.info("predict_proba is property, try _predict_proba")
                            results_proba = model._predict_proba(X_test)

                    elif hasattr(model, 'decision_function'):
                        results_proba = model.decision_function(X_test)

                    if results_proba is not None:
                        results = []
                        proba_classes = model.classes_
                        for item in results_proba:
                            found = False
                            for idx, prob in enumerate(item):
                                if prob > threshold:
                                    results.append(proba_classes[idx])
                                    found = True
                                    break

                            if not found:
                                results.append(proba_classes[0])
            except:
                logging.exception("predict_proba failed.")

            if results is None: 
                results = model.predict(X_test)

            if options['targetFeature'] in target_categoricals:
                results = DataSourceAPIPandas.revertCategories(results,
                                              target_categoricals[options['targetFeature']]['categories'])
                if proba_classes is not None:
                    proba_classes = DataSourceAPIPandas.revertCategories(proba_classes,
                                              target_categoricals[options['targetFeature']]['categories'])
            if path_to_predict:
                ds.load(use_cache=False)
            else:
                ds.load_records(records, features=features, use_cache=False)

            try:
                results = list(results)
            except Exception as e:
                #print("INFO: Prediction result with type: %s convert to list failed: %s"%(type(results), str(e)))
                results = [results]

            ds.df[options['targetFeature']] = results
            if results_proba is not None:
                for idx, name in enumerate(proba_classes):
                    ds.df['proba_'+str(name)] = list(results_proba[:,idx])

        if path_to_predict:
            predict_path = os.path.splitext(path_to_predict)[0] + "_predicted.csv"
            FSClient().removeFile(predict_path)
            FSClient().createParentFolder(predict_path)

            with FSClient().save_local(predict_path) as local_path:
                ds.df.to_csv(local_path, index=False, encoding='utf-8')

            return predict_path
        else:
            return ds.df

    def predict_by_model_ts_recursive(self, model_path, path_to_predict=None, records=None, features=None,
                                      start_prediction_num=None):
        options = FSClient().readJSONFile(os.path.join(model_path, "options.json"))
        targetFeature = options['targetFeature']

        i = start_prediction_num
        result = []
        while True:
            res = self.predict_by_model(model_path, path_to_predict, records, features, predict_value_num=i)
            if res is None:
                break

            if path_to_predict is not None:
                ds = DataSourceAPIPandas({'data_path': res})
                ds.load(features = [targetFeature], use_cache = False)
                res = ds.df
                #res = pd.read_csv(res, encoding='utf-8', escapechar='\\', usecols=[targetFeature])

            #assert len(res) == 1
            result.append(res[targetFeature][0])
            i += 1

        return result

    def score_by_model(self, model_path, predict_path, test_path=None, start_prediction_num=20):
        from auger_ml.Utils import calculate_scores

        if test_path is None:
            test_path = predict_path

        res = {}
        options = FSClient().readJSONFile(os.path.join(model_path, "options.json"))
        targetFeature = options['targetFeature']
        y_pred = None

        if options.get('timeSeriesFeatures'):
            y_pred = self.predict_by_model_ts_recursive(model_path, path_to_predict=predict_path, start_prediction_num=start_prediction_num)
        else:
            predictions = self.predict_by_model(model_path, path_to_predict=predict_path)
            ds = DataSourceAPIPandas({'data_path': predictions})
            ds.load(features = [targetFeature], use_cache = False)
            y_pred = ds.df
            # y_pred = pd.read_csv(predictions, encoding='utf-8', escapechar="\\",
            #      usecols = [targetFeature])

        #TODO: support proba scores and threshold
        ds = DataSourceAPIPandas({'data_path': test_path})
        ds.load(features = [targetFeature], use_cache = False)

        y_true = ds.df
        if test_path == predict_path:
            y_true = y_true.tail(len(y_pred))

        res['all_scores'] = calculate_scores(options, y_test=y_true, y_pred=y_pred)
            
        return res

