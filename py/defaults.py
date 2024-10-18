# guess the system
import os
system="sherlock"
hostname=os.environ.get('HOSTNAME')
if hostname[0:2] == "sh" and 'stanford' in hostname:
    system="sherlock"
elif hostname[0:3] == "sdf":
    system="s3df"

# command line parameters
cparams = {
    'N'      : {'val' : 1024, 'type' : int, 'desc' : 'N_part'},
    'Npm'    : {'val' : 2048, 'type' : int, 'desc' : 'N_pmgrid'},
    'Ntasks' : {'val' :   96, 'type' : int, 'desc' : 'N_tasks'},
    'drylev' : {'val' :    0, 'type' : int, 'desc' : 'dry level'},
    'boxsize': {'val' :   200, 'type' : float, 'desc' : 'boxsize [Mpc/h]'},
    'soft'   : {'val' : 0.025, 'type' : float, 'desc' : 'rsoft [grid spacing]'},
    'basedir': {'val' : "scratch",     'type' : str, 'desc' : 'run directory'},
    'systype': {'val' : "Generic-gcc", 'type' : str, 'desc' : 'systype'},
    'system' : {'val' : system,        'type' : str, 'desc' : 'system'}}

# all parameters
allparams = {
    'cparams' : cparams
}