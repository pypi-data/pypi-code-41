"""
This sub-module contains functions to evaluate how a model could maximize success for a given problem
"""

def dropping_label_categories(model, X, y, drop_label_categories, show_plot = True):
    """
    maximize success for a given problem by dropping the rows/samples containing the labels in the drop_label_categories list. This type of maximization is appropriate for problems such as credit default, where one wishes to simply ignore customers who will default.

    Arguments:
    ----------
        model: the model object of interest from which predictions will be made on the X dataset passed
        X, y: The features and labels the evaluation will be performed on
        drop_label_categories: list. The names of the label categories you wish to exclude for optimal results.

    Returns:
    -------
        df_lift: The lift score for each of the categories in the drop_label_categories list.
            - The lift is calculated as the original % of occurances / the % of occurances after dropping samples based on the predicted values
        y_drop: The true values corresponding to the samples selected after dropping the label categories from the y_pred 
        y_pred_drop: The remaining predicted values after dropping the samples with values matching those in the drop_label_categories list
        y_drop_value_counts: Pandas df containg the value counts for the label categories before dropping based on the predicted values
        y_drop_value_counts: Pandas df containg the value counts for the label categories after dropping based on the predicted values
    """
    import pandas as pd

    y_pred = model.predict(X)
    y_pred = pd.DataFrame(y_pred, columns = list(y.columns))

    y_pred.index = y.index

    y_pred_drop = y_pred[~(y_pred.iloc[:,0].isin(drop_label_categories))]
    drop_idx_list = list(y_pred[(y_pred.iloc[:,0].isin(drop_label_categories))].index.values)

    y_drop = y.drop(drop_idx_list)
    assert(y_drop.shape==y_pred_drop.shape)

    y_value_counts = y.iloc[:,0].value_counts().reset_index()
    y_value_counts.columns = [y.columns[0], 'counts']
    y_value_counts['% of Total'] = y_value_counts['counts']/y_value_counts['counts'].sum()*100

    y_drop_value_counts = y_drop.iloc[:,0].value_counts().reset_index()
    y_drop_value_counts.columns = [y_drop.columns[0], 'counts']
    y_drop_value_counts['% of Total'] = y_drop_value_counts['counts']/y_drop_value_counts['counts'].sum()*100

    df_lift = (y_value_counts['% of Total'][y_value_counts.iloc[:,0].isin(drop_label_categories)] / y_drop_value_counts['% of Total'][y_drop_value_counts.iloc[:,0].isin(drop_label_categories)]).reset_index()
    df_lift.columns = [y.columns[0],'lift']
    
    if show_plot:
        import matplotlib.pyplot as plt
        
        fig, ax_list = plt.subplots(1,2)
        p=0
        for ylabel in ['counts', '% of Total']:
            for df_counts, label in [[y_value_counts, 'before drop'],
                                     [y_drop_value_counts, 'after drop']]:
                ax_list[p].bar(df_counts[y.columns[0]].astype(str), 
                       df_counts[ylabel], label = label,alpha=0.5)

            ax_list[p].set_xticklabels(df_counts[y.columns[0]].astype(str), rotation=90)
            ax_list[p].legend()

            header = y.columns[0]
            if len(header)>20:
                xlabel = '\n'.join(header.split(' '))
            else:
                xlabel = header

            ax_list[p].ticklabel_format(axis='y', style='sci', scilimits=(-3,3))
            ax_list[p].set_xlabel(xlabel)
            ax_list[p].set_ylabel(ylabel)
            ax_list[p].grid(which='both',visible=False)
            p+=1
            
        fig.tight_layout(rect=(0,0,1.5,1))
        plt.show()

    return df_lift, y_drop, y_pred_drop, y_value_counts, y_drop_value_counts