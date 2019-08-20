import socket
import os

###########################
# USER TO CHANGE
###########################

machine = socket.getfqdn()
if "bsc.mn" in machine:
    SCHRODINGER = "/gpfs/projects/bsc72/SCHRODINGER_ACADEMIC"
    PELE = "/gpfs/projects/bsc72/PELE++/nord/rev090518"
    PELE_BIN = "PELE-1.5_mpi"
    MPIRUN = "/apps/INTEL/2017.4/impi/2017.3.196/bin64"
    LICENSE = "/gpfs/projects/bsc72/PELE++/license"
    MMSHARE = None
    # Provisional workaround until best_struct.py is fixed
    ACCEPTED_STEPS_NAME = "numberOfAcceptedPeleSteps"
    CRITERIA = "sasaLig"

elif "mn.bsc" in machine:
    SCHRODINGER = "/gpfs/projects/bsc72/SCHRODINGER_ACADEMIC_NORD"
    PELE = "/gpfs/projects/bsc72/PELE++/nord/rev090518"
    PELE_BIN = "PELE-1.5_mpi"
    MPIRUN = "/apps/OPENMPI/1.8.1-mellanox/bin"
    LICENSE = "/gpfs/projects/bsc72/PELE++/license"
    MMSHARE = None
    # Provisional workaround until best_struct.py is fixed
    ACCEPTED_STEPS_NAME = "AcceptedSteps"
    CRITERIA = "SASA"

elif "bsccv" in machine:
    SCHRODINGER = "/data2/bsc72/SCHRODINGER_ACADEMIC"
    PELE = "/data/EAPM/PELE/PELE++/life/rev12489"
    PELE_BIN = "PELE-1.5_mpi"
    MPIRUN = "/data2/apps/OPENMPI/1.6.1/bin"
    #LICENSE = "/gpfs/projects/bsc72/PELE++/license"
    MMSHARE = None
    LICENSE = "/data/EAPM/PELE/PELE++/license"
    # MMSHARE = "/data2/bsc72/SCHRODINGER_ACADEMIC/mmshare-v3.9/bin/Linux-x86_64"
    # SCHRODINGER_PYTHON_LIBS = "/data2/bsc72/SCHRODINGER_ACADEMIC/mmshare-v3.9/lib/Linux-x86_64/lib/python2.7/site-packages/"
    # Provisional workaround until best_struct.py is fixed
    ACCEPTED_STEPS_NAME = "AcceptedSteps"
    CRITERIA = "SASA"
else:
    SCHRODINGER = "/opt/schrodinger2018-1/"
    PELE = "/opt/PELE/"
    PELE_BIN = "/opt/PELE/bin/PELE-1.5" 
    MPIRUN = "/usr/lib64/openmpi/bin/"
    LICENSE = "/home/ywest/"
    MMSHARE = None
    # Provisional workaround until best_struct.py is fixed
    ACCEPTED_STEPS_NAME = "numberOfAcceptedPeleSteps"
    CRITERIA = "sasaLig"



############################
# PRIVATE CONSTANTS
#############################


# DEFAULTS
# --------

COMPLEX = "complex.pdb"
RESULTS = "results"
LIG_RES = "LIG"
LIG_CHAIN = "Z"
FORCEFIELD = "OPLS2005"
PELE_CONFILE = "pele.conf"
CPUS = 140
RESTART = "true"
CLUSTERS = 40
PLATFORM_RESTART = "all"
EQ_STEPS = 50
GRIDRES = '10.0'
NATIVE = '''
                                   {{
       
                                      "type": "rmsd",
       
                                      "Native": {{\n\
                                       "path":\n\
                                       "{}" }},\n\
       
                                      "selection": {{ "chains": {{ "names": [ "{}" ] }} }},\n\
       
                                      "includeHydrogens": false,\n\
       
                                      "doSuperposition": false,\n\
       
                                      "tag" : "ligandRMSD"\n\
       
                                   }},\n\
       
       
            '''
        
WATER_ENERGY =             '''
                            {{
                            "type": "bindingEnergy",\n\
                            "boundPartSelection": {{ "chains": {{ "names": ["{0}"] }} }},\n\
                            "tag": "water{0}"\n\
                            }},\n\
                           '''
DISTANCE_ATOMS =     '''
                     {{
                     "type":"com_distance",
                     "tag":"distance{2}",
                     "selection_group_1":{{
                     "atoms": {{ "ids":["{0}"]}}
                     }},
                     "selection_group_2":{{
                     "atoms": {{ "ids":["{1}"]}}
                     }}
                     }},
                     '''




#TEMPLATE KEYWORDS
#------------------

GLIDE_TEMPLATE = ["INPUT", "PRECISION"]

#RESTARTS:
#-----------

FIRST_RESTART = ["all",]
SECOND_RESTART = ["all", "adaptive"]
THIRD_RESTART = ["all", "adaptive", "pele"]
FOURTH_RESTART = ["all", "adaptive", "pele", "msm"] 

#PATHS
#-------

DIR = os.path.dirname(__file__)
ADAPTIVE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "Adaptive/clusterAdaptiveRun.py"))

#MESSAGES&ERRORS
#-----------------

CLUSTER_ERROR = "Number of cpus ({}) must be bigger than clusters ({})"
SYSTEM = "System {} checked successfully\n\t**Missing residues found {}\n\t**Gaps found {}\n\t**Metals found {}"
