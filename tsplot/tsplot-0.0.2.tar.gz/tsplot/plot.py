import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 25})
import numpy as np # used for xpoints only

class SeriesSub:

    def __init__(self,xlabels_l1=[None,None],xlabels_l2=[None,None],xlabels_l3=[None,None],ycolor='k',sub1=3,sub2=1,figsize=(27, 12),dpi=60):
        '''
            Initialise figure for plotting time series

            Parameters
            ----------

            xlabels_l1 : list of length 2
                [labels,tick positions] for xaxis 1
            xlabels_l2 : list of length 2
                [labels,tick positions] for xaxis 2
            ylabel : string
                label for variable Y

            Returns
            '''''''
            None

        '''
        self.fig, self.ax 	= plt.subplots(sub1,sub2,figsize=figsize, dpi=dpi, facecolor='w', edgecolor='k')
        self.xlabels_l1      = xlabels_l1
        self.xlabels_l2      = xlabels_l2
        self.xlabels_l3      = xlabels_l3

        if not None in xlabels_l1:
            self.ax[0].set_xticks(xlabels_l1[1])
            self.ax[0].set_xticklabels(xlabels_l1[0])

        self.ax[0].grid(True)            

        if not None in xlabels_l2:
            self.ax2  = []
            self.ax2.append(self.ax[0].twiny())
            self.ax2[0].set_xticks(xlabels_l2[1])
            self.ax2[0].set_xticklabels(xlabels_l2[0])
            self.ax2[0].xaxis.set_ticks_position('bottom') # set the position of the second x-axis to bottom
            self.ax2[0].spines['bottom'].set_position(('outward', 36))
            self.ax2[0].set_xlim((0,max(xlabels_l1[1])))

        if not None in xlabels_l3:
            self.ax3  = []
            self.ax3.append(self.ax[0].twiny())
            self.ax3[0].set_xticks(xlabels_l3[1])
            self.ax3[0].set_xticklabels(xlabels_l3[0])
            self.ax3[0].xaxis.set_ticks_position('bottom') # set the position of the second x-axis to bottom
            self.ax3[0].spines['bottom'].set_position(('outward', 72))
            self.ax3[0].set_xlim((0,max(xlabels_l1[1])))

        # self.ax2.set_xlim(self.ax.get_xlim())

        # This can be adjusted in limits() - it is applied here to sync axis
        self.ax[0].set_xlim((0,max(xlabels_l1[1])))
        
        

        # if not None in xlim:
        #     self.ax.set_xlim((xlim[0],xlim[1]))
        #     self.ax2.set_xlim((xlim[0],xlim[1]))


        # if not None in ylim:
        #     self.ax.set_ylim((ylim[0],ylim[1]))

        self.fig.tight_layout()

        self.lineplotnum = 0
        self.scatplotnum = 0


    def xlimits(self,xmin,xmax,xlabels_l1=True, xlabels_l2=False, xlabels_l3=False,plot=0):
        if xlabels_l1: self.ax[plot].set_xlim((xmin,xmax))
        if xlabels_l2: self.ax2[plot].set_xlim((xmin,xmax))
        if xlabels_l3: self.ax3[plot].set_xlim((xmin,xmax))

    def ylimits(self,ymin,ymax,plot=0):
        self.ax[plot].set_ylim((ymin,ymax))

    def set_ylabel(self,label,plot=0,c='k'):
        self.ax[plot].set_ylabel(label,color=c)

    def labelmatch(self,plot=1):
        
        if not None in self.xlabels_l1:
            self.ax[plot].set_xticks(self.xlabels_l1[1])
            self.ax[plot].set_xticklabels(self.xlabels_l1[0])

        if not None in self.xlabels_l2:
            self.ax2.append(self.ax[plot].twiny())
            self.ax2[plot].set_xticks(self.xlabels_l2[1])
            self.ax2[plot].set_xticklabels(self.xlabels_l2[0])
            self.ax2[plot].xaxis.set_ticks_position('bottom') # set the position of the second x-axis to bottom
            self.ax2[plot].spines['bottom'].set_position(('outward', 36))
            self.ax2[plot].set_xlim((0,max(self.xlabels_l1[1])))

        if not None in self.xlabels_l3:
            self.ax3.append(self.ax[plot].twiny())
            self.ax3[plot].set_xticks(self.xlabels_l3[1])
            self.ax3[plot].set_xticklabels(self.xlabels_l3[0])
            self.ax3[plot].xaxis.set_ticks_position('bottom') # set the position of the second x-axis to bottom
            self.ax3[plot].spines['bottom'].set_position(('outward', 72))
            self.ax3[plot].set_xlim((0,max(self.xlabels_l1[1])))

        # This can be adjusted in limits() - it is applied here to sync axis
        self.ax[plot].set_xlim((0,max(self.xlabels_l1[1])))
        self.ax[plot].grid(True)

    def scatter(self,X,Y,s=10,alpha=1,c='mediumblue',label=None,plot=0):   

        '''
        X : array
            time index
        Y: array
            variable values
        '''     

        splot = self.ax[plot].scatter(X,Y,s=s,alpha=alpha,c=c,label=label)

        # splot.set_alpha(1)  # Change alpha for data points to be shown in legend.
        self.scatplotnum+=1

    def line(self,X,Y,linewidth=2,c='midnightblue',label=None,alpha=1,plot=0):
 
        lplot = self.ax[plot].plot(X,Y,linewidth=linewidth,c=c,label=label,alpha=alpha)
        # lplot.set_alpha(1)  # Change alpha for data points to be shown in legend.
        self.lineplotnum+=1

    def legend(self,plot=0,fontsize=18,linewidth=80.0,framealpha=0.5):
        # self.legend = self.ax.legend()
        self.lgnd = self.ax[plot].legend(loc="best",prop={'size':fontsize},framealpha=framealpha)  

        for handle in self.lgnd.legendHandles:
            try:
                handle.set_alpha(1)
                handle.set_sizes([pointsize])
            except:
                handle.set_linewidth(linewidth)

        #     try:handle._legmarker.set_alpha(0)
        #     except: continue 
        #     try: handle.set_alpha(1)
        #     except: continue


    def fixplot(self):
        '''
            adjust figure
        '''
        self.fig.tight_layout()

    def save(self,path='figure.png'):      
        '''
        Parameters
        ----------
        
        save : string
            figure save path
        '''
        self.fig.savefig(path)      


    def show(self):
        plt.show()


    def close(self):
        plt.close()

class Series:

    def __init__(self,xlabels_l1=[None,None],xlabels_l2=[None,None],xlabels_l3=[None,None],ylabel=None,ycolor='k',figsize=(27,9),dpi=60):
        '''
            Initialise figure for plotting time series

            Parameters
            ----------

            xlabels_l1 : list of length 2
                [labels,tick positions] for xaxis 1
            xlabels_l2 : list of length 2
                [labels,tick positions] for xaxis 2
            ylabel : string
                label for variable Y

            Returns
            '''''''
            None

        '''
        self.fig, self.ax 	= plt.subplots(figsize=figsize, dpi=dpi, facecolor='w', edgecolor='k')

        if not None in xlabels_l1:
            self.ax.set_xticks(xlabels_l1[1])
            self.ax.set_xticklabels(xlabels_l1[0])

        plt.grid(True)
        if not ylabel == None:
            plt.ylabel(ylabel,color=ycolor)
       

        if not None in xlabels_l2:
            # Set scond x-axis
            self.ax2 = self.ax.twiny()
            self.ax2.set_xticks(xlabels_l2[1])
            self.ax2.set_xticklabels(xlabels_l2[0])
            self.ax2.xaxis.set_ticks_position('bottom') # set the position of the second x-axis to bottom
            self.ax2.spines['bottom'].set_position(('outward', 36))
            self.ax2.set_xlim((0,max(xlabels_l1[1])))

        if not None in xlabels_l3:
            self.ax3 = self.ax.twiny()
            self.ax3.set_xticks(xlabels_l3[1])
            self.ax3.set_xticklabels(xlabels_l3[0])
            self.ax3.xaxis.set_ticks_position('bottom') # set the position of the second x-axis to bottom
            self.ax3.spines['bottom'].set_position(('outward', 72))
            self.ax3.set_xlim((0,max(xlabels_l1[1])))

        # self.ax2.set_xlim(self.ax.get_xlim())

        # This can be adjusted in limits() - it is applied here to sync axis
        self.ax.set_xlim((0,max(xlabels_l1[1])))
        
        

        # if not None in xlim:
        #     self.ax.set_xlim((xlim[0],xlim[1]))
        #     self.ax2.set_xlim((xlim[0],xlim[1]))


        # if not None in ylim:
        #     self.ax.set_ylim((ylim[0],ylim[1]))

        self.fig.tight_layout()

        self.lineplotnum = 0
        self.scatplotnum = 0

    def yaxis2(self,label=None,c='k'):
        '''
        Create a second y-axis on the right-hand side of the figure

        '''
        self.axy2 = self.ax.twinx()
        # if not label == None:
        self.axy2.set_ylabel(label,color=c)
        self.axy2.tick_params('y',color=c)
        self.axy2.grid(True)
        self.fig.tight_layout()

    def xlimits(self,xmin,xmax,xlabels_l1=True, xlabels_l2=False, xlabels_l3=False):
        if xlabels_l1: self.ax.set_xlim((xmin,xmax))
        if xlabels_l2: self.ax2.set_xlim((xmin,xmax))
        if xlabels_l3: self.ax3.set_xlim((xmin,xmax))

    def ylimits(self,ymin,ymax):
        self.ax.set_ylim((ymin,ymax))

    def ylimits2(self,ymin,ymax):
        self.axy2.set_ylim((ymin,ymax))

    def scatter(self,X,Y,s=10,alpha=1,c='mediumblue',label=None,axis=1):   

        '''
        X : array
            time index
        Y: array
            variable values
        '''     
        if axis==1:
            splot = self.ax.scatter(X,Y,s=s,alpha=alpha,c=c,label=label)
        if axis==2:
            splot = self.axy2.scatter(X,Y,s=s,alpha=alpha,c=c,label=label)
        # splot.set_alpha(1)  # Change alpha for data points to be shown in legend.
        self.scatplotnum+=1

    def line(self,X,Y,linewidth=2,c='midnightblue',label=None,axis=1,alpha=1):
        if axis==1:
            lplot = self.ax.plot(X,Y,linewidth=linewidth,c=c,label=label,alpha=alpha)
        elif axis==2:
            lplot = self.axy2.plot(X,Y,linewidth=linewidth,c=c,label=label,alpha=alpha)
        # lplot.set_alpha(1)  # Change alpha for data points to be shown in legend.
        self.lineplotnum+=1

    def legend(self,fontsize=18,pointsize=80,linewidth=2.0):
        # self.legend = self.ax.legend()
        self.lgnd = self.ax.legend(loc="best",prop={'size':fontsize})  

        for handle in self.lgnd.legendHandles:
            try:
                handle.set_alpha(1)
                handle.set_sizes([pointsize])
            except:
                handle.set_linewidth(linewidth)

        # if self.axy2: # if another y-axis was created - can this be integrated??
        #     self.lgnd = self.axy2.legend(loc=4,prop={'size':fontsize})  

        #     for handle in self.lgnd.legendHandles:
        #         try:
        #             handle.set_alpha(1)
        #             handle.set_sizes([pointsize])
        #         except:
        #             handle.set_linewidth(linewidth)

        #     try:handle._legmarker.set_alpha(0)
        #     except: continue 
        #     try: handle.set_alpha(1)
        #     except: continue


    def fixplot(self):
        '''
            adjust figure
        '''
        self.fig.tight_layout()

    def save(self,path='figure.png'):      
        '''
        Parameters
        ----------
        
        save : string
            figure save path
        '''
        self.fig.savefig(path)      


    def font(self,s=20):
        plt.rcParams.update({'font.size': s})

    def show(self):
        plt.show()


    def close(self):
        plt.close()



def egplot(X,Y,xlabels_l1=[None,None],xlabels_l2=[None,None],ylabel=None,xlim=[None,None]):

    '''
        Plot a time series of variable Y over time X

        Parameters
        ----------
        X : array
            time index
        Y: array
            variable values
        xlabels_l1 : list of length 2
            [labels,tick positions] for xaxis 1
        xlabels_l2 : list of length 2
            [labels,tick positions] for xaxis 2
        ylabel : string
            label for variable Y
        save : string
            figure save path
        Returns
        '''''''
        None

    '''
    fig, ax 	= plt.subplots(figsize=(27, 9), dpi=60, facecolor='w', edgecolor='k')
    ax.plot(X,Y,linewidth=3)
    # ax.scatter(X,Y,s=10)

    if not None in xlabels_l1:
        ax.set_xticks(xlabels_l1[1])
        ax.set_xticklabels(xlabels_l1[0])

    
    plt.grid(True)
    if not ylabel == None:
        plt.ylabel(ylabel)
    ax.set_ylim((min(Y),max(Y)))

    # if not None in xlabels_l2:
    # Set scond x-axis
    ax2 = ax.twiny()
    ax2.set_xlim(ax.get_xlim())
    ax2.set_xticks(xlabels_l2[1])
    ax2.set_xticklabels(xlabels_l2[0])

    ax2.xaxis.set_ticks_position('bottom') # set the position of the second x-axis to bottom
    ax2.spines['bottom'].set_position(('outward', 36))

    if None in xlim:
        ax.set_xlim((min(X),max(X)))
        ax2.set_xlim((min(X),max(X)))
    else:
        ax.set_xlim((xlim[0],xlim[1]))
        ax2.set_xlim((xlim[0],xlim[1]))

    fig.tight_layout()
    # if not save == None:
    #     plt.savefig(save)
    # if show:
    plt.show()