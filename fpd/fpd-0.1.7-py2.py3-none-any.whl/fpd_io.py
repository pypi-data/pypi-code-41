from __future__ import print_function

import os
import h5py
import numpy as np
from tqdm import tqdm
import xml.etree.cElementTree as ET
from .fpd_processing import _block_indices
from .fpd_file import _create_emd
from . import __version__ as fpd_pkg_version


def topspin_app5_to_hdf5(app5, h5fn=None, TEM='ARM200cF', prec_angle=0.0, chunk_dim_size=16, compression_opts=4):
    '''
    Function for converting Topspin .app5 files into multidimensional hdf5 format.
    The detector data is saved in a 4-D EMD dataset with compression and chunking.
    The survey image, virtual aperture image and header attributes are stored as EMD.
    Sum images for the scan and detector axes, generated during conversion, are also
    stored in the same hdf5 file.

    Parameters
    ----------
    app5 : str
        The name of the .app5 file to be converted. The extension is added if missing.
    h5fn : str
        The name of the file to be created. If None, the input filename is used.
    TEM : str
        Name of the acquisition microscope.
    prec_angle : float
        Precession angle in degrees. See Notes.
    chunk_dim_size : int
        Length of one side of a chunk. Chunks are uniform along all dimensions.
    compression_opts : int
        GZIP compression level to be used when writing data to hdf5 file.

    Returns
    -------
    output_fn : str
        String containing path and name of generated hdf5 file.

    Notes
    -----
    The precession angle is critical to a PED experiment but appears to be missing
    from the app5 metadata. Until resolved, the user is asked to supply this (in degrees).
    '''

    _version_major = 0
    _version_minor = 4

    if not app5.endswith('.app5'):
        app5 += '.app5'
    
    location = os.path.dirname(app5)
    filePath = os.path.join(location, app5)
    if os.path.isfile(filePath):
        h5f = h5py.File(filePath, 'r')
    else:
        raise Exception('Specified file either does not exist or is not in app5 format.')
    
    # This creates a top level list of the file contents
    contents = list(h5f.keys())
    # contents should now contain 3 items.  Two with data and one called 'Version'
    a = h5f.get(contents[0])
    b = h5f.get(contents[1])
    c = h5f.get(contents[2])
    # We've now created references to each of the items in the top level keys
    # We should now retrieve keys from each of these sets where valid
    try:
        aKeys = list(a.keys())
    except:
        aKeys = None
    try:
        bKeys = list(b.keys())
    except:
        bKeys = None
    try:
        cKeys = list(c.keys())
    except:
        cKeys = None
    # We know that only two of these contain real data, and one of these is just 
    # version information.  We should figure this out and discard.
    if aKeys == None:
        topspin = a
        aKeys = cKeys
        a = c
    if bKeys == None:
        topspin = b
        bKeys = cKeys
        b = c
    # after these two if statements, we should be left with all the real data in 
    # sets a and b, and the remainder is cast into the value 'topspin' (in case we
    # should need to refer to this later).
    del c, cKeys
    
    # Now the next thing we need to check is which of the two remaining trees is
    # the survey image and which contains the main dataset.  Based on what we know
    # of the file structure, we know that only one of these should contain a
    # subgroup.  We'll use this to distinguish them. To do this, we need to 
    # recognise the difference between data and groups. Using the get() function,
    # we can check the class against the two forms:
    # h5py._hl.dataset.Dataset and h5py._hl.group.Group
    aHasSubgroup = 0
    bHasSubgroup = 0
    for aKeyi in aKeys:
        if a.get(aKeyi, getclass=True) == h5py.Group:
            aHasSubgroup = 1
            break
    for bKeyi in bKeys:
        if b.get(bKeyi, getclass=True) == h5py.Group:
            bHasSubgroup = 1
            break
    
    # Based on the values of xHasSubgroup, we now know which branch contains the
    # survey image and which contains the main dataset.  We Should assign these.
    if aHasSubgroup == 1 and bHasSubgroup == 0:
        dataBranch = a
        surveyBranch = b
    elif aHasSubgroup == 0 and bHasSubgroup == 1:
        dataBranch = b
        surveyBranch = a
    else:
        raise Exception('Unexpected file structure encountered.')
    # Some cleanup
    del a, b, aKeys, bKeys
    # We should now have references to the survey and main data
    # in surveyBranch and dataBranch
    

    #---------------------------------------------------------
    # Create a new file which we will flush friendly data into
    if h5fn is None:
        h5fn = app5.rsplit('.', 1)[0]
        output_fn = os.path.join(location, h5fn + '.hdf5')
    if os.path.isfile(output_fn):
        h5f.close()
        raise Exception('File to be written to already exists. Conversion aborted.')
    else:
        newFile = h5py.File(output_fn, 'w')
    # create top-level group which all data falls under
    topGroup = newFile.create_group('fpd_expt')
    # create additional top-level groups expected in EMD format
    microGroup = newFile.create_group('microscope')
    userGroup = newFile.create_group('user')
    sampleGroup = newFile.create_group('sample')
    
    # fpd package version
    vmajor, vminor, vpatch = [int(x) for x in fpd_pkg_version.split('.')]
    newFile.attrs['fpd_pkg_version'] = fpd_pkg_version
    newFile.attrs['fpd_pkg_version_major'] = vmajor
    newFile.attrs['fpd_pkg_version_minor'] = vminor
    newFile.attrs['fpd_pkg_version_patch'] = vpatch

    # EMD version
    newFile.attrs['version_major'] = 0 
    newFile.attrs['version_minor'] = 2

    # version for topspin data conversion
    topGroup.attrs['PED_version_major'] = _version_major 
    topGroup.attrs['PED_version_minor'] = _version_minor
    topGroup.attrs['experiment_type'] = 'Scanning Precession Diffraction'


    #---------------------------------------------------------
    # First, lets pull out the survey image.  The branch 'surveyBranch' should 
    # contain keys called 'Metadata', 'Thumbnail' and 'Version' as well as one
    # with a funky name that actually contains the image we want.
    # a quick for loop allows us to run through the keys and find the one w/o
    # a straightforward name, which we identify as the data.
    for sbKeyi in list(surveyBranch.keys()):
        if (sbKeyi != 'Metadata') and (sbKeyi != 'Thumbnail') and (sbKeyi != 'Version'):
            surveyImage = surveyBranch.get(sbKeyi)
            break
    
    # parse metadata
    surveyMD = ET.fromstring(surveyBranch['Metadata'].value.decode())
    xOffset = float(surveyMD.find('ProcedureData/Item/Value/Calibration/X/Offset').text) / (1E-9)
    xScale = float(surveyMD.find('ProcedureData/Item/Value/Calibration/X/Scale').text) / (1E-9)
    yOffset = float(surveyMD.find('ProcedureData/Item/Value/Calibration/Y/Offset').text) / (1E-9)
    yScale = float(surveyMD.find('ProcedureData/Item/Value/Calibration/Y/Scale').text) / (1E-9)
    nPoints = int(surveyMD.find('ProcedureData/Item/Value/NumberOfPoints').text) # survey image should always be square.

    xRange = np.arange(0, nPoints)*xScale + xOffset
    yRange = np.arange(0, nPoints)*yScale + yOffset

    surveyData = _create_emd(topGroup,
                             'survey_image',
                             True,
                             ['scanY', 'scanX'],
                             [yRange, xRange],
                             ['n_m', 'n_m'],
                             data_name='survey_image',
                             data_units='counts',
                             shape=surveyImage.shape,
                             dtype=surveyImage.dtype,
                             data=None,
                             compression="gzip",
                             compression_opts=compression_opts)

    surveyData[:] = surveyImage
    surveyData.flush()
    # Cleanup once we have what we want from surveyBranch
    del surveyBranch, xOffset, xScale, yOffset, yScale, nPoints, xRange, yRange, surveyImage


    #---------------------------------------------------------
    # Now, in dataBranch, we need to identify the survey image as well as the 
    # 4dSTEM dataset branch
    for dKeyi in list(dataBranch.keys()):
        if (dKeyi != 'Metadata') and (dKeyi != 'Thumbnail') and (dKeyi != 'Version'):
            if dataBranch.get(dKeyi, getclass=True) == h5py.Group:
                STEM4d = dataBranch.get(dKeyi)
            elif dataBranch.get(dKeyi, getclass=True) == h5py.Dataset:
                virtIm = dataBranch.get(dKeyi)

    imMD = ET.fromstring(dataBranch['Metadata'].value.decode())
    # determine scan calibrations from metadata, converted into nanometres
    xOffset = float(imMD.find('ProcedureData/Item/Value/Calibration/X/Offset').text) / (1E-9)
    xScale = float(imMD.find('ProcedureData/Item/Value/Calibration/X/Scale').text) / (1E-9)
    yOffset = float(imMD.find('ProcedureData/Item/Value/Calibration/Y/Offset').text) / (1E-9)
    yScale = float(imMD.find('ProcedureData/Item/Value/Calibration/Y/Scale').text) / (1E-9)
    nPoints = int(imMD.find('ProcedureData/Item/Value/NumberOfPoints').text) # survey image should always be square.
    yPoints, xPoints = virtIm.shape

    xRange = np.arange(0, xPoints)*xScale + xOffset
    yRange = np.arange(0, yPoints)*yScale + yOffset
    yRange = yRange[::-1] * -1 # This flip keeps calibration consistent with data, which is read in backwards
    # create EMD dataset for the virtual STEM image calculated by the topspin software
    virtualData = _create_emd(topGroup,
                              'virtual_image',
                              True,
                              ['scanY', 'scanX'],
                              [yRange, xRange],
                              ['n_m', 'n_m'],
                              data_name='virtual_image',
                              data_units='counts',
                              shape=virtIm.shape, 
                              dtype=virtIm.dtype,
                              data=None,
                              compression="gzip",
                              compression_opts=compression_opts)

    virtualData[:] = virtIm
    virtualData.flush()
    # cleanup!
    del dataBranch
    
    
    #---------------------------------------------------------
    nFrames = xPoints * yPoints
    first = STEM4d['0']['Data']
    det_y, det_x = first.shape
    dpMD = ET.fromstring(STEM4d['0']['Metadata'].value.decode())
    # determine detector calibrations (probably wrong) from metadata
    det_xOffset = float(dpMD.find('Calibration/X/Offset').text)
    det_xScale = float(dpMD.find('Calibration/X/Scale').text)
    det_yOffset = float(dpMD.find('Calibration/Y/Offset').text)
    det_yScale = float(dpMD.find('Calibration/Y/Scale').text)

    det_xRange = np.arange(0, det_x)*det_xScale + det_xOffset
    det_yRange = np.arange(0, det_y)*det_yScale + det_yOffset
    
    # create EMD dataset to hold 4d data
    mainData = _create_emd(topGroup,
                           'fpd_data',
                           True,
                           ['scanY', 'scanX', 'detY', 'detX'],
                           [yRange, xRange, det_yRange, det_xRange],
                           ['n_m', 'n_m', 'm_rad', 'm_rad'],
                           data_name='data',
                           data_units='counts',
                           shape=(yPoints, xPoints, det_y, det_x),
                           dtype=first.dtype,
                           data=None,
                           chunks=(chunk_dim_size,)*4,
                           compression="gzip",
                           compression_opts=compression_opts)
    # create EMD dataset for the r-space sum image representing the data
    sum_im = _create_emd(topGroup,
                         'fpd_sum_im',
                         True,
                         ['scanY', 'scanX'],
                         [yRange, xRange],
                         ['n_m', 'n_m'],
                         data_name='sum_im',
                         data_units='counts',
                         shape=virtIm.shape, 
                         dtype=first.dtype,
                         data=None,
                         compression="gzip",
                         compression_opts=compression_opts)
    # create EMD dataset for the summed diffraction pattern of the data
    sum_dif = _create_emd(topGroup,
                          'fpd_sum_dif',
                          True,
                          ['detY', 'detX'],
                          [det_yRange, det_xRange],
                          ['m_rad', 'm_rad'],
                          data_name='sum_dif',
                          data_units='counts',
                          shape=first.shape, 
                          dtype=first.dtype,
                          data=np.zeros(first.shape),
                          compression="gzip",
                          compression_opts=compression_opts)
    
    
    #---------------------------------------------------------
    # calculate indices for chunking
    r_if, c_if = _block_indices(dshape=virtIm.shape, nrnc=(chunk_dim_size,)*2)

    print('Parsing 4d data...')
    # iterate through chunks and pull individual diffraction patterns into 4d structure
    with tqdm(total=(yPoints*xPoints), unit='images') as pbar:
        #iterate at chunk level
        for i, (ri, rf) in enumerate(r_if):
            for j, (ci, cf) in enumerate(c_if):
                s = np.s_[ri:rf, ci:cf]
                data = np.empty([rf-ri, cf-ci, 256, 256], dtype=first.dtype)
                # iterate through points within chunk
                for k in range(ri, rf, 1):
                    for l in range(ci, cf, 1):
                        index = xPoints*yPoints - xPoints + l - k*xPoints 
                        # index calculated to flip data vertically
                        # this accounts for the topspin data origin being in the bottom left, rather than top left
                        dp = STEM4d[str(index)]['Data'][:]
                        data[k-ri, l-ci] = dp
                        # calculate sum images on the fly
                        sum_im[k, l] = sum(sum(dp))
                        sum_dif[:] += dp
                mainData[s] = data
                pbar.update((rf-ri)*(cf-ci))

    # flush all data calculated in the loop
    mainData.flush()
    sum_im.flush()
    sum_dif.flush()

    # conversion of metadata from XML format in app5 to hdf5 attributes
    getint = lambda obj, term : int(obj.find(term).text)
    getflt = lambda obj, term : float(obj.find(term).text)
    getstr = lambda obj, term : obj.find(term).text
    getbool = lambda obj, term : bool(obj.find(term).text)

    dataTags = {'NumberPrecessionCycles'    : { 'data': mainData, 'attr': 'Number_Precessions', 'func': getint, 'val': 'Value' },
                'FrameTime'                 : { 'data': mainData, 'attr': 'DwellTime', 'func': getflt, 'val': 'Value' },
                'IsPrecessionEnabled'       : { 'data': mainData, 'attr': 'Precession_Enabled', 'func': getbool, 'val': 'Value' },
                'Camera'                    : { 'data': mainData, 'attr': 'Detector', 'func': getstr, 'val': 'Value' },
                'Scanning'                  : { 'data': mainData, 'attr': 'Scan_Hardware', 'func': getstr, 'val': 'Value' },
                'DiffractionCameraLength'   : { 'data': mainData, 'attr': 'Camera_Length', 'func': getflt, 'val': 'Value' },
                'GunHighVoltage'            : { 'data': microGroup, 'attr': 'voltage', 'func': getflt, 'val': 'Value' },
                'DiffractionToStemRotation' : { 'data': mainData, 'attr': 'Diffraction_To_Scan_Rotation', 'func': getflt, 'val': 'Value' },
                'ScanRotation'              : { 'data': mainData, 'attr': 'Scan_Rotation', 'func': getflt, 'val': 'Value' },
                'VirtualStemIntegration'    : { 'data': virtualData, 'attr': 'Virtual_STEM_Type', 'func': getstr, 'val': 'Value' },
                'VirtualStemMask'           : { 0: { 'data': virtualData, 'attr': 'Virtual_Aperture_Cx', 'func': getflt, 'val': './/X' },
                                                1: { 'data': virtualData, 'attr': 'Virtual_Aperture_Cy', 'func': getflt, 'val': './/Y'},
                                                2: { 'data': virtualData, 'attr': 'Virtual_Aperture_Width', 'func': getflt, 'val': './/Width'},
                                                3: { 'data': virtualData, 'attr': 'Virtual_Aperture_Height', 'func': getflt, 'val': './/Height'}}
                }

    microGroup.attrs['name'] = TEM
    sampleGroup.attrs['ID'] = imMD.find('Specimen').text
    userGroup.attrs['name'] = imMD.find('CreatedBy').text
    mainData.attrs['precession_angle'] = prec_angle
    
    print('Parsing Metadata...')
    for item in imMD.findall('.//Item'):
        name = item.find('Name').text

        log = dataTags.get(name)
        if log is not None:
            # e.g. mainData.attrs['Camera'] = getstr(item, 'Value')
            if log.get(0) is not None:
                for i in range(len(log)):
                    sub = log.get(i)
                    sub.get('data').attrs[sub.get('attr')] = sub.get('func')(item, sub.get('val'))
            else:
                log.get('data').attrs[log.get('attr')] = log.get('func')(item, log.get('val'))
    
    
    #---------------------------------------------------------
    # print('Parsed data can be found in file created at: '+output_fn)
    print('Done')
    h5f.close()
    newFile.close()
    return output_fn

