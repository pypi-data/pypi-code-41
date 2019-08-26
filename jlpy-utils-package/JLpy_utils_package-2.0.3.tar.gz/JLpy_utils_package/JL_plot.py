import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.rcParams['grid.color'] =  'lightgray'
mpl.rcParams['grid.linestyle'] = '-'
mpl.rcParams['grid.linewidth'] = 1
mpl.rcParams['axes.grid.which'] = 'both'
mpl.rcParams['axes.grid']=True 
mpl.rcParams['xtick.minor.visible']=True
mpl.rcParams['ytick.minor.visible']=True
mpl.rcParams['xtick.top']=True
mpl.rcParams['ytick.right']=True
mpl.rcParams['xtick.direction']='inout'
mpl.rcParams['ytick.direction']='inout'
mpl.rcParams['font.size'] = 14
mpl.rcParams['figure.facecolor'] = 'w'

import numpy as np
import pandas as pd

def make_independant_legend(legend_lines,legened_labels,legend_title):
    plt.legend(legend_lines,legened_labels,title=legend_title)
    plt.grid(which='both')
    plt.axis('off')
    plt.show()

def fetch_color_map_for_primary_color(primary_color, n_colors, 
                                      color_space_range = None):
    """
    Default color_space_range = {'R': (0.1,0.7),
                                 'G': (0.4,0.6),
                                 'B': (0,0.3)}
    """
    if color_space_range == None: # Apply default setting
        color_space_range = {'R': (0.1,0.7),
                             'G': (0.4,0.6),
                             'B': (0,0.3)}
        color_space_range = color_space_range[primary_color]
        
    if primary_color == 'R':
        color_map = plt.cm.hot(np.linspace(color_space_range[0],color_space_range[1],n_colors))    
    elif primary_color == 'G':
        color_map = plt.cm.nipy_spectral(np.linspace(color_space_range[0],color_space_range[1],n_colors))    
    elif primary_color == 'B':
        color_map = plt.cm.jet(np.linspace(color_space_range[0],color_space_range[1],n_colors))    
    return color_map

def corr_matrix(df_corr):
    fig, ax = plt.subplots(1,1)
    cax = ax.matshow(df_corr)
    fig.colorbar(cax)
    ax.grid(which='both',visible=False)
    ax.set_xticklabels([0]+list(df_corr.columns), rotation='vertical')
    ax.set_yticklabels([0]+list(df_corr.columns))
    plt.show()

def corr_and_pareto(df,label,size=10):
    '''
    Description: 
        Plt correlation matrix for entire data frame, then plot pareto bar-chart for 1 label of interest
    Inputs:
        df: pandas DataFrame
        label: column/header for which you want to plot the bar-chart pareto for
        size: vertical and horizontal size correlation chart
    Returns:
        df_correlations, df_label_pareto, df_label_pareto_sorted
        '''
    
    #plot correlation chart
    df_correlations = plot_corr(df,size)
    plt.show()
    
    #Fetch pareto for selected label
    df_label_pareto = df_correlations[label]
    df_label_pareto_sorted = df_correlations[label].sort_values(ascending=False)

    plt.bar(df_label_pareto_sorted.index,df_label_pareto_sorted)
    plt.xticks(rotation = 'vertical')
    plt.ylabel(label+" Correlation Factor",fontsize = 14)
    plt.title(label+" Correlation Factor Pareto", fontsize = 14)
    plt.tick_params(axis='both',labelsize = 14)
    plt.show()
    
    return df_correlations, df_label_pareto, df_label_pareto_sorted

def by_color_group_and_line_group(df,
                                       color_group,
                                       line_group,
                                       x_label,
                                       y_label,
                                       x_scale):
    
    df = df.sort_values(x_label).reset_index(drop=True)
    Color_ID = str(df['Color'].unique()[0])
    
    df_color_group = df.groupby(by=color_group)
    
    legend_labels = list(df[color_group].unique())
    colors = fetch_color_map_for_primary_color(Color_ID, len(legend_labels))
    legend_lines = [mpl.lines.Line2D([0], [0], color=c, lw=1) for c in colors]
    
    c = 0
    for color_group_ID, df_by_color_group in df_color_group:
        df_line_group = df_by_color_group.groupby(line_group)
        for line_group_ID, df_by_line_group in df_line_group:
            plt.plot(df_by_line_group[x_label],df_by_line_group[y_label],color = colors[c], linestyle='-')
        c+=1
    if x_scale == 'log':
        plt.xscale('log')
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.show()
    make_independant_legend(legend_lines, legend_labels,color_group)
    
    
def hist_or_bar(df, n_plot_columns = 3, 
                 categorical_headers = [None]):
    """
    Iterate through each column in a pandas dataframe and plot the histogram or bar chart for the data.
    
    Arguments:
        df: pandas dataframe
        n_plot_columns: number of plots to print on a single row of plots
        categorical_headers: string. The name of the categorical headers which will be plotted as bar charts. If [None], object type headers will be plotted as bar charts.
    """
    import matplotlib.pyplot as plt
    import datetime
    import sklearn.impute
    
    df = df.copy()
    
    fig, ax_list = plt.subplots(1, n_plot_columns)
    p=0
    for header in df:
        
        type_ = df[header].dtype
        
        #plot as bar char if object and not date time
        if (type_ == 'O' and isinstance(df[header].iloc[0], datetime.time)==False) or header in categorical_headers:
            
            df[header] = df[header].fillna('NaN')
            
            df_counts = df[header].value_counts().reset_index()
            df_counts.columns = [header, 'counts']
            df_counts = df_counts.sort_values('counts').reset_index(drop=True)
            df_counts[header] = df_counts[header].astype(str)
            
            #only allow up to max_labels to be plotted, otherwise just plot the top and bottom most frequent labels
            max_labels = 10
            if df_counts.shape[0]>max_labels:
                
                bottom = df_counts.iloc[:int(max_labels/2), :]
                top = df_counts.iloc[-int(max_labels/2):, :]
                
                ax_list[p].bar(top[header], top['counts'], label = 'top counts')
                ax_list[p].bar(bottom[header], bottom['counts'], label = 'bottom counts')
                
                ax_list[p].set_xticklabels(list(top[header])+list(bottom[header]), rotation=90)
                ax_list[p].legend()
            else:
                ax_list[p].bar(df_counts[header],df_counts['counts'])
                
                ax_list[p].set_xticklabels(df_counts[header], rotation=90)
        
        #plot counts vs time if time pts
        elif isinstance(df[header].iloc[0], datetime.time):
            slice_ = df[[header]]
            slice_ = slice_.dropna()
            
            df_counts = slice_[header].value_counts().reset_index()
            df_counts.columns = [header, 'counts']
            df_counts = df_counts.sort_values(header)
            
            ax_list[p].plot(df_counts[header], df_counts['counts'])
            
            
        else: #plot as histogram
            slice_ = df[[header]]
            slice_ = slice_.dropna()
            
            ax_list[p].hist(slice_[header], bins = np.min((100, df[header].nunique())))
            
        ax_list[p].grid(which='both',visible=False)
        
        if len(header)>20:
            xlabel = '\n'.join(header.split(' '))
        else:
            xlabel = header
        
        ax_list[p].set_xlabel(xlabel)
        ax_list[p].set_ylabel('counts')
        ax_list[p].ticklabel_format(axis='y', style='sci', scilimits=(-2,2))
        
        p+=1
        
        if p==n_plot_columns:
            
            try:
                fig.tight_layout(rect=(0,0,int(n_plot_columns/1.2),1))
            except:
                try:
                     fig.tight_layout()
                except Exception as e: 
                    print('Exception: '+ str(e))
                
            plt.show()
            
            #generate new plot if this isn't the last header
            if header != list(df.columns)[-1]:
                
                fig, ax_list = plt.subplots(1, n_plot_columns)
                #fill in dummy plots
                for ax in ax_list:
                    ax.grid(which='both',visible=False)
                p=0

    #ensure last plot is formated and shown
    if p!=n_plot_columns:
        try:
            fig.tight_layout(rect=(0,0,int(n_plot_columns/1.2),1))
        except:
            try:
                 fig.tight_layout()
            except Exception as e: 
                print('Exception: '+ str(e))

        plt.show()