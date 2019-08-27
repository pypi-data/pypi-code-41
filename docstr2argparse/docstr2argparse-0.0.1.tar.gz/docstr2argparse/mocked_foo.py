def apex3d(raw_folder,
           output_dir,
           lock_mass_z2=785.8426,
           lock_mass_tol_amu=.25,
           low_energy_thr=300,
           high_energy_thr=30,
           lowest_intensity_thr=750,
           write_xml=True,
           write_binary=True,
           write_csv=False,
           max_used_cores=1,
           path_to_apex3d='C:/SYMPHONY_VODKAS/plgs/Apex3D64.exe',
           PLGS=True,
           cuda=True,
           unsupported_gpu=True,
           debug=False,
           **kwds):
    """A wrapper around the infamous Apex3D.
    
    Args:
        raw_folder (str): a path to the input folder with raw Waters data.
        output_dir (str): Path to where to place the output.
        lock_mass_z2 (float): The lock mass for doubly charged ion (which one, dunno, but I guess a very important one).
        lock_mass_tol_amu (float): Tolerance around lock mass (in atomic mass units, amu).
        low_energy_thr (int): The minimal intensity of a precursor ion so that it ain't a noise peak.
        high_energy_thr (int): The minimal intensity of a fragment ion so that it ain't a noise peak.
        lowest_intensity_thr (int): The minimal intensity of a peak to be analyzed.
        write_xml (boolean): Write the output in an xml in the output folder.
        write_binary (boolean): Write the binary output in an xml in the output folder.
        write_csv (boolean): Write the output in a csv in the output folder (doesn't work).
        max_used_cores (int): The maximal number of cores to use.
        path_to_apex3d (str): Path to the "Apex3D.exe" executable.
        PLGS (boolean): No idea what it is.
        cuda (boolean): Use CUDA.
        unsupported_gpu (boolean): Try using an unsupported GPU for calculations. If it doesn't work, the pipeline switches to CPU which is usually much slower.
        debug (boolean): Debug mode.
        kwds: other parameters for 'subprocess.run'.
    
    Returns:
        tuple: the path to the outcome (no extension: choose it yourself and believe more in capitalism) and the completed process.
    """
    pass