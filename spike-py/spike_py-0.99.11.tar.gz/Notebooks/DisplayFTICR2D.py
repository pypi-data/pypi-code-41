#!/usr/bin/env python
# coding: utf-8

# <h1>Table of Contents<span class="tocSkip"></span></h1>
# <div class="toc"><ul class="toc-item"><li><span><a href="#To-use-it," data-toc-modified-id="To-use-it,-1"><span class="toc-item-num">1&nbsp;&nbsp;</span>To use it,</a></span><ul class="toc-item"><li><span><a href="#Initialization-of-the-environment" data-toc-modified-id="Initialization-of-the-environment-1.1"><span class="toc-item-num">1.1&nbsp;&nbsp;</span>Initialization of the environment</a></span></li><li><span><a href="#Choose-the-file" data-toc-modified-id="Choose-the-file-1.2"><span class="toc-item-num">1.2&nbsp;&nbsp;</span>Choose the file</a></span></li><li><span><a href="#to-come" data-toc-modified-id="to-come-1.3"><span class="toc-item-num">1.3&nbsp;&nbsp;</span>to come</a></span></li></ul></li></ul></div>

# # Display utility for 2D FTICR Spectra
# 
# *This little utility allows to interactively explore large 2D FTICR-MS datasets.*
# 
# You find here a simple interface the reads and displays the multiresolution 2D files created by `SPIKE` when processing 2D data-sets (usually called `xxx_mr.msh5`).
# 
# It is based on the capabilities of both the `SPIKE` library and the `jupyter notebook` interface.
# Thanks to the technology behind, these extremely large files can be accessed rapidly, even on a laptop computer.
# 
# This program supersedes the old `Visu2D` program, developped in `Qt`, which could no longer be maintained.
# 
# *This is a work inprogress - additional utilities should come soon !*

# ## To use it, 
# execute each executable cell (marked with the `In[]`) either by cliking on the Run icon on the top of the window, or by hitting *shift-Return* on the keyboard

# ### Initialization of the environment
# the following cell should be run only once, at the beginning of the processing

# In[1]:


from IPython.display import display, HTML, Markdown, Image
display(Markdown('## STARTING Environment...'))
get_ipython().run_line_magic('matplotlib', 'notebook')
import spike.Interactive.INTER as I
from spike.Interactive.FTICR_INTER import MR, MR_interact
from spike.Interactive.ipyfilechooser import FileChooser
I.hidecode()


# ### Choose the file
# Use `FileChooser()` to choose a file on your disk - The optional `base` argument, starts the exploration on a given location.
# 
# 2D processed files are `*.msh5` files.

# In[2]:


FC = FileChooser('/DATA',filetype='y*.msh5', mode='r')
display(FC)


# the `MR` tool simply loads and describe the content of the file

# In[4]:


MR(FC.selected)


# `MR_interact` loads and display the data-set.
# 
# It can be called directly

# In[10]:


MR_interact(FC.selected);


# - 🔍 in  : zoom win
# - 🔍out : zoom out
# - ◀︎ : moves the zoom window left
# - ▶︎ : moves the zoom window right
# - ▲ : moves the zoom window up
# - ▼ : moves the zoom window down
# - ⍇ : back in zoom list
# - ⍈ : forward in zoom list
# - you can also directly enter the zoom coordinates, the click on Update
# - × : lower the levels used for the display
# - ÷ : raise the levels used for the display
# - ≡ : reset default levels
# - ⌘ : reset to initial view
# 
# Note that the 2D files contain several version of the spectrum at different resolution - zooming and out may modify the look of the region you are looking to.
# Only the closest zoom contains the unbiaised verion of the spectrum.
# 
# Some additional options are possible:
# 
# - store the view into a python variable (we'll see other usage below)
# - store the created view into a python variable
# - define behaviour at start-up
# - overload the initial view

# In[5]:


# complete initialisation, and storing the view into a python var
DI = MR_interact(FC.selected,
                report=False,   # inhibits parameter printing
                show=False,     # does not display on start-up
                figsize=(15,15),# Size of initial display (in cm)
                Debug=False     # Enables live debugging if True
               )
DI._zoom = (380, 700, 380, 700)     # set the initial zoom view, in m/z (F1low , F1High , F2low , F2High)
DI.scale = 3.0                      # set the initial scale
DI.show()                           # and finally show


# In[16]:


S = 0
for d in DI.data:
    S += d.size1*d.size2
print(S/1E9, 'Gpixels')
print(8*S/1E9, 'Gb')


# There is 1D extraction tool which is handy to examine carefully the details
# 
# Just use your stored view and append `.I1D()` to it

# In[18]:


830/(0.508-0.448),502/(2.31-1.51)


# In[25]:


DI.data[0].axis1.mztoh(400), DI.data[0].axis1.mztoh(700)


# In[22]:


DI.data[0].axis1.specwidth, DI.data[0].axis2.specwidth


# In[17]:


DI.I1D()


# ### to come
# - calibration
# - peak detection
# - superimposition
# - exctaction of arbitrary 1D 
# - locate artifacts due to harmonics

# In[ ]:




