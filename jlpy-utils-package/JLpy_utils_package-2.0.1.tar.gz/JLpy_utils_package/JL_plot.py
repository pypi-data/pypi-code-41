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

def plot_corr_and_pareto(df,label,size=10):
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

def plot_by_color_group_and_line_group(df,
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