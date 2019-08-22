
def pull_model_attributes(df_in, attributes):
    df = df_in.copy()
    for (model_name, attributes) in attributes.items():
        for attr in attributes:
            df[model_name+'_'+attr] = df[model_name].apply(lambda x: x[attr])
    return df
