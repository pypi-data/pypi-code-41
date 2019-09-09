import matplotlib as __mpl__

__mpl__.rcParams['grid.color'] =  'lightgray'
__mpl__.rcParams['grid.linestyle'] = '-'
__mpl__.rcParams['grid.linewidth'] = 1
__mpl__.rcParams['axes.grid.which'] = 'both'
__mpl__.rcParams['axes.grid']=True 
__mpl__.rcParams['xtick.minor.visible']=True
__mpl__.rcParams['ytick.minor.visible']=True
__mpl__.rcParams['xtick.top']=True
__mpl__.rcParams['ytick.right']=True
__mpl__.rcParams['xtick.direction']='inout'
__mpl__.rcParams['ytick.direction']='inout'
__mpl__.rcParams['font.size'] = 14
__mpl__.rcParams['figure.facecolor'] = 'w'

def make_independant_legend(legend_lines,legened_labels,legend_title):
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    
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
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    
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

def corr_matrix(df_corr, cbar_label = 'Correlation Coeff.', vmin = None, vmax = None):
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    
    fig, ax = plt.subplots(1,1)
    cax = ax.matshow(df_corr, vmin = vmin, vmax = vmax)
    cbar = fig.colorbar(cax)
    cbar.set_label(cbar_label, labelpad=15, ha='center', va='center', rotation=90)
    ax.grid(which='both',visible=False)
    ax.set_xticklabels([0]+list(df_corr.columns), rotation='vertical')
    ax.set_yticklabels([0]+list(df_corr.columns))
    plt.show()

def corr_pareto(df_corr,label, rect = (0, 0, 1, 1), ylim = None):
    
    '''
    Plot plot pareto bar-chart for 1 label of interest within a correlation dataframe
    Arguments:
    ---------
        df_corr: pandas DataFrame correlation matrix
        label: column/header for which you want to plot the bar-chart pareto for
        size: vertical and horizontal size correlation chart
    Returns:
    --------
        df_correlations, df_label_pareto, df_label_pareto_sorted
    '''

    import matplotlib as mpl
    import matplotlib.pyplot as plt

    #Fetch pareto for selected label
    df_label_pareto = df_corr[label]
    df_label_pareto_sorted = df_corr[label].sort_values(ascending=False)
    df_label_pareto_sorted = df_label_pareto_sorted.drop(label)

    fig, ax = plt.subplots(1,1)
    ax.bar(df_label_pareto_sorted.index, df_label_pareto_sorted)
    
    ax.set_ylabel(label+" Correlation Factor")
    ax.set_title(label+" Correlation Factor Pareto\n")
    ax.grid(which='both', visible=False)
    ax.set_ylim(ylim)
    
    ax.set_xticklabels(df_label_pareto_sorted.index, rotation = 'vertical')

    fig.tight_layout(rect = rect )
    plt.show()

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
    import numpy as np
    
    df = df.copy()
    
    
    fig, ax_list = plt.subplots(1, n_plot_columns)
    if n_plot_columns == 1:
        ax_list = [ax_list]
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
                
                ax_list[p].bar(bottom[header], bottom['counts'], label = 'bottom counts')
                ax_list[p].bar(top[header], top['counts'], label = 'top counts')
                
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