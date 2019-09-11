#!/usr/bin/env python
# coding: utf-8

# <h1>Table of Contents<span class="tocSkip"></span></h1>
# <div class="toc"><ul class="toc-item"><li><span><a href="#Initialization" data-toc-modified-id="Initialization-1"><span class="toc-item-num">1&nbsp;&nbsp;</span>Initialization</a></span><ul class="toc-item"><li><span><a href="#Choose-the-file" data-toc-modified-id="Choose-the-file-1.1"><span class="toc-item-num">1.1&nbsp;&nbsp;</span>Choose the file</a></span></li><li><span><a href="#Import-dataset" data-toc-modified-id="Import-dataset-1.2"><span class="toc-item-num">1.2&nbsp;&nbsp;</span>Import dataset</a></span></li></ul></li><li><span><a href="#Basic-Processing" data-toc-modified-id="Basic-Processing-2"><span class="toc-item-num">2&nbsp;&nbsp;</span>Basic Processing</a></span><ul class="toc-item"><li><span><a href="#Fourier-Transform" data-toc-modified-id="Fourier-Transform-2.1"><span class="toc-item-num">2.1&nbsp;&nbsp;</span>Fourier Transform</a></span></li><li><span><a href="#rephasing" data-toc-modified-id="rephasing-2.2"><span class="toc-item-num">2.2&nbsp;&nbsp;</span>rephasing</a></span></li></ul></li><li><span><a href="#Peak-Picker" data-toc-modified-id="Peak-Picker-3"><span class="toc-item-num">3&nbsp;&nbsp;</span>Peak-Picker</a></span></li><li><span><a href="#Integrate" data-toc-modified-id="Integrate-4"><span class="toc-item-num">4&nbsp;&nbsp;</span>Integrate</a></span></li><li><span><a href="#Interactive-composite-display" data-toc-modified-id="Interactive-composite-display-5"><span class="toc-item-num">5&nbsp;&nbsp;</span>Interactive composite display</a></span></li><li><span><a href="#Save-the-data-set" data-toc-modified-id="Save-the-data-set-6"><span class="toc-item-num">6&nbsp;&nbsp;</span>Save the data-set</a></span><ul class="toc-item"><li><span><a href="#Save-the-peak-list-to-a-csv-file" data-toc-modified-id="Save-the-peak-list-to-a-csv-file-6.1"><span class="toc-item-num">6.1&nbsp;&nbsp;</span>Save the peak list to a csv file</a></span></li><li><span><a href="#Save-the-integrals-to-a-csv-file" data-toc-modified-id="Save-the-integrals-to-a-csv-file-6.2"><span class="toc-item-num">6.2&nbsp;&nbsp;</span>Save the integrals to a csv file</a></span></li></ul></li><li><span><a href="#Export-a-buckelist" data-toc-modified-id="Export-a-buckelist-7"><span class="toc-item-num">7&nbsp;&nbsp;</span>Export a buckelist</a></span></li></ul></div>

# # 1D NMR Processing and Display
# 
# a simplified environment for processing 1D Bruker NMR datasets with `SPIKE`.
# 
# Run each python cell in sequence by using the ⇥Run button above (or typing *shift* Enter).
# 
# Cells are meant to be used in order, taking you to the complete analysis, but you can go back at any time.
# 
# The SPIKE code used for processing is visible in the cells, and can be used as a minimal tutorial.
# 
# ***Remark*** *to use this program, you should have installed the following packages:*
# 
# - *a complete scientific python environment* ( *tested with python 3.6 - [anaconda](https://www.anaconda.com/) 
#  but it should also work in python 2.7*)
# - [`spike`](https://www.bitbucket.org/delsuc/spike) ( *version 0.99.9 minimum* )
# - [`ipywidgets`](https://ipywidgets.readthedocs.io/en/latest/)  ( *tested with version 7.1* )
# 
# ## Initialization
# the following cell should be run only once, at the beginning of the processing

# In[1]:


# load all python and interactive tools
from __future__ import print_function, division
from IPython.display import display, HTML, Markdown, Image
display(Markdown('## STARTING Environment...'))
get_ipython().run_line_magic('matplotlib', 'notebook')
import os.path as op
from IPython.display import display, HTML, Markdown, Image
import spike
from spike.File.BrukerNMR import Import_1D
from spike.Interactive import INTER as I
from spike.Interactive.ipyfilechooser import FileChooser
display(Markdown('## ... program is ready'))
I.hidecode()


# ### Choose the file
# The `FileChooser()` tool creates a dialog box which allows to choose a file on your disk
# 
# - use the `Select` button
# - modify the ( *optional* ) `path` argument, to start the exploration on a given location
# - After the selection, the selected filename is found in `FC.selected`

# In[2]:


FC = FileChooser(path='/DATA/pharma/',filename='fid')
display(FC)


# ### Import dataset
# 
# This is simply done with the `Import_1D()` tool, which returns a `SPIKE` object.
# 
# We store the dataset into a variable, typing the variable name shows a summary of the dataset. 

# In[3]:


print('Reading file ',FC.selected)
d1 = Import_1D(FC.selected)
d1.filename = FC.selected
d1.set_unit('sec').display(title=FC.nmrname+" fid")
d1


# In the current set-up, the figure can be explored *(zoom, shift, resize, etc)* with the jupyter tools displayed  below the dataset.
# The figure can also be saved as a `png` graphic file.
# 
# At anytime, the figure can be frozen by clicking on the blue button on the upper right corner, just rerun the cell to make it interactive again.
# 
# ## Basic Processing
# We are going to use a basic processing set-up, check the documentation for advanced processing
# 
# ### Fourier Transform

# In[4]:


D1 = d1.copy() # copy the imported data-set to another object for processing
D1.apod_em(0.3).zf(4).ft_sim().bk_corr().apmin()  # chaining  apodisation - zerofill - FT - Bruker correction - autophase
D1.set_unit('ppm').display(title=FC.nmrname)  # chain  set to ppm unit - and display


# ### rephasing
# If is is required use the interactive phaser
# 
# Use `scale` and `zoom` to tune the display; then use `P0, P1, pivot` to optimize the phase.
# 
# Once finished, click on `Apply correction`

# In[5]:


I.Phaser1D(D1);


# ## Peak-Picker
# - moving the threshold determines the minimum peak intensity
# - peaks are searched only in the selected zoom window

# In[6]:


I.NMRPeaker(D1);


# ## Integrate
# Integration zones are computed from the peaks detected with the Peak-Picker above.
# 

# In[7]:


I.NMRIntegrate(D1)


# ## Interactive composite display
# Convenient to set-up your own figure

# In[ ]:


I.Show1D(D1,title=FC.nmrname)


# ## Save the data-set
# either as stand alone native SPIKE files, (there are other formats)

# In[ ]:


D1.save('example1.gs1')


# or as a `csv` text file, - in which case, it is probably better to remove the imaginary part, not useful there.
# 
# The file contains some basic informations in addition to the spectral data

# In[ ]:


D1.copy().real().save_csv('example.csv')


# ### Save the peak list to a csv file

# In[ ]:


D1.pk2pandas().to_csv('peaklist.csv')


# ### Save the integrals to a csv file

# In[ ]:


D1.integrals.to_pandas().to_csv('integrals.csv')


# ## Export a buckelist

# In[8]:


# adapt the parameters below
Zoom = (0.5,8)                    # zone to bucket       - in ppm
BucketSize = 0.04                 # width of the buckets - in ppm
Output = 'screen'                   # 'screen'  or  'file'  determines output
BucketFileName = 'bucket.csv'     #  the filename if Output (above) is 'file'  - don't forget the .csv extension.


# In[9]:


# the following cell executes the bucketing
if Output == 'file':
    with open(BucketFileName,'w') as F:
        D1.bucket1d(zoom=Zoom, bsize=BucketSize, pp=True, file=F)
    print('buckets written to %s\n'%op.realpath(BucketFileName))
else:
    D1.bucket1d(zoom=Zoom, bsize=BucketSize, pp=True);


# *Tools in this page is under intensive development - things are going to change rapidly.*
