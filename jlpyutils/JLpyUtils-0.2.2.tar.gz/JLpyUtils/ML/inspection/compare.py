
def model_metrics(models_dict, metrics, verbose = 1):
    """
    Iterate throught the models in the models_dict & analyize the metrics for each model, compiling all the metrics into a df_metrics pandas dataframe object.
    
    Arguments:
    ----------
        models_dict: dictionary containing trained models from ML_models.hyperparams.search... methods
        metrics: [[key(str), method(sklearn.metrics...)]'
    Returns:
        models_dict: passed models_dict with metrics added as new key
        df_metrics: pandas dataframe summarizing the metrics
    Notes:
        The function assumes the first metric in the list of metrics is the most important metric and will sort the results according to this metric
    """
    import pandas as pd
    
    metrics_dict = {}
    metrics_dict['model'] =[]
    for key in models_dict.keys():
        metrics_dict['model'].append(key)
        for metric_key in metrics.keys():
            models_dict[key][metric_key] = metrics[metric_key](models_dict[key]['y_test'], 
                                                               models_dict[key]['y_pred'])
            if metric_key not in metrics_dict.keys():
                metrics_dict[metric_key]=[]
            metrics_dict[metric_key].append(models_dict[key][metric_key])
    df_metrics = pd.DataFrame.from_dict(metrics_dict).sort_values(list(metrics.keys())[0]).reset_index(drop=True)
    if verbose >=1:
        display(df_metrics)
    return models_dict, df_metrics
            