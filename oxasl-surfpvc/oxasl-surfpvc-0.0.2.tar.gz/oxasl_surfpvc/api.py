"""
OXASL_SURFPVC: Surface-based partial volume estimates for OXASL pipeline

Thomas Kirk

Copyright (c) 2018-2019 Univerisity of Oxford
"""

import os.path as op 

from fsl.data.image import Image

import toblerone

def prepare_surf_pvs(wsp):
    """
    Prepare model fitting run using surface-based partial volume estimates

    Workspace attributes updated:

     - ``basil_options`` - Dictionary updated with ``pwm`` and ``pgm`` attributes
                           which are WM/GM partial volume estimates
    """

    # Pipeline: 
    # Do an initial run of oxford_asl using just ASL data to get a perfusion image
    # Register (epi_reg, BBR) the structural to this perfusion image 
    # Run Toblerone in the space of the perfusion image
    # Motion correct the ASL data to the perfusion image 
    # Run oxford_asl with PVEc from surface estimates
    # Optional: run oxford_asl with PVEc from FAST estimates

    # Estimate WM and GM PVs
    struct2asl = wsp.reg.struc2asl
    ref = wsp.reg.regfrom.dataSource
    struct = wsp.reg.regto.dataSource
    wsp.sub('surf_pvs')

    if not toblerone.utils.check_anat_dir(wsp.fslanat):
        raise RuntimeError("fsl_anat dir not complete with surfaces")

    if True: 
        pvs, _ = toblerone.estimate_all(ref=ref, anat=wsp.fslanat, struct2ref=struct2asl, flirt=True)

        spc = toblerone.classes.ImageSpace(ref)
        for k, v in pvs.items():
            spc.saveImage(v, op.join(wsp.surf_pvs.savedir, k + '.nii.gz'))
        
    wm, gm = [
        Image(op.join(wsp.surf_pvs.savedir, 'all_%s.nii.gz' % t)) 
        for t in ['WM', 'GM'] 
    ]
    wsp.basil_options.update({"pwm" : wm, "pgm" : gm})
