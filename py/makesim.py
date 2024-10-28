import numpy as np
import sys
import yaml
import pathlib
import subprocess
import os
import shutil
import defaults as spd
import math

def parsecommandline():
    import argparse

    parser   = argparse.ArgumentParser(description='Commandline interface to ptflow')

    for params in spd.allparams:
        for param in spd.allparams[params]:
            pdval = spd.allparams[params][param]['val']
            ptype = spd.allparams[params][param]['type']
            pdesc = spd.allparams[params][param]['desc']
            parser.add_argument('--'+param, default=pdval, help=f'{pdesc} [{pdval}]', type=ptype)

    return vars(parser.parse_args())

params = parsecommandline()

configfile  = str(pathlib.Path(__file__).parent.resolve())+'/../config/config.yaml'
templatedir = str(pathlib.Path(__file__).parent.resolve())+'/../templates'
email = os.environ.get('EMAIL')

with open(configfile) as fx:
    config = yaml.safe_load(fx)

# guess total memory requirement if not provided
if params['totmem'] == 0:
    params['totmem'] = 720 * (params['N']/1024)**3

# if benchmark specified, override parameters accordingly
if len(params['bench']):
    benchname = params['bench']
    if params['runname'] == "":
        params['runname'] = benchname
    bench = spd.benchmarks[benchname]

    for benchkey in bench:
        if benchkey == 'sim':
            simname = bench['sim']
            sim = spd.sims[simname]
            for simkey in sim:
                key = simkey
                value = sim[key]
        else:
            key = benchkey
            value = bench[key]
        if params[key] != value:
            print(f"  benckmark {benchname}: overriding {key} with {value}")
            params[key] = value

# get system configuration
for key in config[params['system']]:
    params[key] = config[params['system']][key]
for key in params:
    print(f'{key+": ":>15} {str(params[key])}')

if params['runname'] == "":
    params['runname'] = str(params['boxsize'])+"Mpc_n"+str(params['N'])+"_p"+str(params['Npm'])

# convenience variables
N           = params['N']
Npm         = params['Npm']
Ntasks      = params['Ntasks']
systype     = params['systype']
commit      = params['commit']
env         = params['env']
system      = params['system']
constraint  = params['constraint']
taskpernode = params['taskpernode']
mempernode  = params['mempernode']
partition   = params['partition']
acct        = params['acct']
mpiexe      = params['mpiexe']
runname     = params['runname']
totmem      = params['totmem']
modules     = params['modules']

# # derived parameters
boxsize = params['boxsize']
N_nodes = math.ceil(Ntasks / taskpernode)
nodemem = str(mempernode)+'G'

taskpernode = math.ceil(Ntasks / N_nodes)        
maxmem = str(int(totmem/Ntasks*1024))

nlisten = 1
if taskpernode > 64:
    nlisten = 2

rsoft   = boxsize / params['N'] * params['soft']
if boxsize%1.0 == 0:
    boxsize = int(boxsize)

# # make run directories
basedir = params['basedir']
if basedir == 'scratch':
    basedir = os.environ.get('SCRATCH')
rundir = basedir+"/simpipe/"+runname
srcdir = rundir+"/gadget4"
outdir = rundir+"/output"

if os.path.isdir(rundir):
    user_input = input(f"  {rundir} exists, delete? [y/N] ") 
    if user_input.lower() == 'y':
        shutil.rmtree(rundir)
    else:
        exit()
os.makedirs(rundir)
os.makedirs(outdir)

# get gadget source
if params['drylev'] >= 3:
    print(f"  DRY RUN: git clone https://gitlab.mpcdf.mpg.de/vrs/gadget4.git {srcdir}")
    print(f"  DRY RUN: cd {srcdir} ; git reset --hard {commit}")
    print(f"  DRY RUN: sed -i -e 's/errflag = 1/errflag = 0/g' {srcdir}/src/data/mymalloc.cc")
    subprocess.call(f"mkdir -p {srcdir}/buildsystem &> /dev/null", shell=True)
else:
    print("  downloading Gadget4 ...")
    if os.path.isdir(srcdir):
        shutil.rmtree(srcdir)
    subprocess.call(f"git clone https://gitlab.mpcdf.mpg.de/vrs/gadget4.git {srcdir} &> /dev/null", shell=True)
    subprocess.call(f"cd {srcdir} ; git reset --hard {commit} &> /dev/null", shell=True)
    # disable error when /dev/shmem is too small
    subprocess.call(f'sed -i -e "s/errflag = 1/errflag = 0/g" {srcdir}/src/data/mymalloc.cc', shell=True)

# configuration file
subprocess.call(f'cp {templatedir}/Config-template.sh {srcdir}/tmpfile', shell=True)
subprocess.call(f'sed -i -e "s/N_REPLACE/{N}/g"         {srcdir}/tmpfile', shell=True)
subprocess.call(f'sed -i -e "s/NPM_REPLACE/{Npm}/g"     {srcdir}/tmpfile', shell=True)
subprocess.call(f'sed -i -e "s/LST_REPLACE/{nlisten}/g" {srcdir}/tmpfile', shell=True)
subprocess.call(f'mv {srcdir}/tmpfile {srcdir}/Config.sh', shell=True)

# parameter file
subprocess.call(f'cp {templatedir}/param-template.txt   {rundir}/tmpfile', shell=True)
subprocess.call(f'sed -i -e "s/N_REPLACE/{N}/g"         {rundir}/tmpfile', shell=True)
subprocess.call(f'sed -i -e "s/SOFT_REPLACE/{rsoft}/g"  {rundir}/tmpfile', shell=True)
subprocess.call(f'sed -i -e "s/BOX_REPLACE/{boxsize}/g" {rundir}/tmpfile', shell=True)
subprocess.call(f'sed -i -e "s:DIR_REPLACE:{rundir}:g"  {rundir}/tmpfile', shell=True)
subprocess.call(f'sed -i -e "s:MXM_REPLACE:{maxmem}:g"  {rundir}/tmpfile', shell=True)

subprocess.call(f'mv {rundir}/tmpfile {rundir}/param.txt', shell=True)

# systype file
subprocess.call(f'cp {templatedir}/Makefile-template.systype {srcdir}/tmpfile', shell=True)
subprocess.call(f'sed -i -e "s/SYSTYPE_REPLACE/{systype}/g" {srcdir}/tmpfile', shell=True)
subprocess.call(f'mv {srcdir}/tmpfile {srcdir}/Makefile.systype', shell=True)

# generic library file
subprocess.call(f'cp {templatedir}/Makefile-template.gen.libs {srcdir}/tmpfile', shell=True)
subprocess.call(f'sed -i -e "s:ENVPATH_REPLACE:{env}:g" {srcdir}/tmpfile', shell=True)
subprocess.call(f'mv {srcdir}/tmpfile {srcdir}/buildsystem/Makefile.gen.libs', shell=True)

# batch script
if "s3df" in system:
    subprocess.call(f'cat {templatedir}/launch-template.sh | grep -v CONST | grep -v osc_sm > {rundir}/tmpfile', shell=True)
    subprocess.call(f'sed -i -e "s/ACCT_REPLACE/{acct}/g" {rundir}/tmpfile', shell=True)
else:
    subprocess.call(f'cat {templatedir}/launch-template.sh | grep -v ACCT  | grep -v ulimit > {rundir}/tmpfile', shell=True)
    subprocess.call(f'sed -i -e "s/CONST_REPLACE/{constraint}/g" {rundir}/tmpfile', shell=True)
subprocess.call(f'sed -i -e "s:MLOAD_REPLACE:{modules}:g"   {rundir}/tmpfile', shell=True)
subprocess.call(f'sed -i -e "s/PART_REPLACE/{partition}/g"  {rundir}/tmpfile', shell=True)
subprocess.call(f'sed -i -e "s/NODES_REPLACE/{N_nodes}/g"   {rundir}/tmpfile', shell=True)
subprocess.call(f'sed -i -e "s/RUN_REPLACE/{runname}/g"     {rundir}/tmpfile', shell=True)
subprocess.call(f'sed -i -e "s:DIR_REPLACE:{rundir}:g"      {rundir}/tmpfile', shell=True)
subprocess.call(f'sed -i -e "s/EMAIL_REPLACE/{email}/g"     {rundir}/tmpfile', shell=True)
subprocess.call(f'sed -i -e "s/TPN_REPLACE/{taskpernode}/g" {rundir}/tmpfile', shell=True)
subprocess.call(f'sed -i -e "s/MPN_REPLACE/{totmem}/g"      {rundir}/tmpfile', shell=True)
subprocess.call(f'sed -i -e "s/EMAIL_REPLACE/{email}/g"     {rundir}/tmpfile', shell=True)
subprocess.call(f'sed -i -e "s:ENVPATH_REPLACE:{env}:g"     {rundir}/tmpfile', shell=True)
subprocess.call(f'sed -i -e "s/NTASK_REPLACE/{Ntasks}/g"    {rundir}/tmpfile', shell=True)
subprocess.call(f'sed -i -e "s/MPIEXE_REPLACE/{mpiexe}/g"   {rundir}/tmpfile', shell=True)
subprocess.call(f'mv {rundir}/tmpfile {rundir}/launch.sh', shell=True)

# launch job
if params['drylev'] >= 1:
    print(f"  DRY RUN: sbatch {rundir}/launch.sh")
else:
    subprocess.call(f"sbatch {rundir}/launch.sh", shell=True)

