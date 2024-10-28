# guess the system
import os
system="sh4-cscale"
hostname=os.environ.get('HOSTNAME')
if hostname[0:2] == "sh" and 'stanford' in hostname:
    system="sh4-cscale"
    modules="gcc openmpi py-numpy/1.26.3_py312"
elif hostname[0:3] == "sdf":
    system="s3df-milano"
    modules="mpi/mpich-x86_64 hdf5/mpich-EPEL"

# command line parameters
cparams = {
    'N'      : {'val' : 1024, 'type' : int, 'desc' : 'N_part'},
    'Npm'    : {'val' : 2048, 'type' : int, 'desc' : 'N_pmgrid'},
    'Ntasks' : {'val' :   96, 'type' : int, 'desc' : 'N_tasks'},
    'drylev' : {'val' :    0, 'type' : int, 'desc' : 'dry level'},
    'totmem' : {'val' :    0, 'type' : int, 'desc' : 'total memory [GB]'},
    'boxsize': {'val' :   200, 'type' : float, 'desc' : 'boxsize [Mpc/h]'},
    'soft'   : {'val' : 0.025, 'type' : float, 'desc' : 'rsoft [grid spacing]'},
    'basedir': {'val' :     "scratch", 'type' : str, 'desc' : 'run directory'},
    'systype': {'val' : "Generic-gcc", 'type' : str, 'desc' : 'systype'},
    'system' : {'val' :        system, 'type' : str, 'desc' : 'system'},
    'modules': {'val' :       modules, 'type' : str, 'desc' : 'mpi module'},
    'runname': {'val' :            "", 'type' : str, 'desc' : 'run name'},
    'bench'  : {'val' :            "", 'type' : str, 'desc' : 'benchmark name'}}

# all parameters
allparams = {
    'cparams' : cparams
}

# simulations
sims = {
    "bench-0" : {
        'N'       : 1024,
        'Npm'     : 2048,
        'boxsize' : 200,
        'totmem'  : 720
    },
    "bench-1" : {
        'N'       : 2048,
        'Npm'     : 4096,
        'boxsize' : 400,
        'totmem'  : 8*720
    }
}

# benchmarks
benchmarks = {
    "sh3-cbase-0"  : { 'Ntasks'  :  96, 'system': 'sh3-cbase',   'sim': 'bench-0'},
    "sh3-cbase-1"  : { 'Ntasks'  : 768, 'system': 'sh3-cbase',   'sim': 'bench-1'},

    "sh4-cscale-0" : { 'Ntasks'  :  96, 'system': 'sh4-cscale',  'sim': 'bench-0'},
    "sh4-cscale-1" : { 'Ntasks'  : 768, 'system': 'sh4-cscale',  'sim': 'bench-1'},

    "sh4-cbase-0"  : { 'Ntasks'  :  96, 'system': 'sh4-cbase',   'sim': 'bench-0'},
    "sh4-cbase-1"  : { 'Ntasks'  : 768, 'system': 'sh4-cbase',   'sim': 'bench-1'},

  "s3df-milano-0"  : { 'Ntasks'  : 192, 'system': 's3df-milano', 'sim': 'bench-0'},
  "s3df-milano-1"  : { 'Ntasks'  : 720, 'system': 's3df-milano', 'sim': 'bench-1'},

  "s3df-milano-0-ompi"  : { 'Ntasks'  : 192, 'system': 's3df-milano', 'sim': 'bench-0',
                            'modules' : 'mpi/openmpi-x86_64'},

}
