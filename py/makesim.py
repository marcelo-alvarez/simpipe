import numpy as np
import sys
import yaml
import pathlib
import subprocess
import os
import shutil

def parsecommandline():
    import argparse
    import defaults as spd

    parsbool = argparse.BooleanOptionalAction
    parser   = argparse.ArgumentParser(description='Commandline interface to ptflow')

    for params in spd.allparams:
        for param in spd.allparams[params]:
            pdval = spd.allparams[params][param]['val']
            ptype = spd.allparams[params][param]['type']
            pdesc = spd.allparams[params][param]['desc']
            if ptype == 'bool':
                parser.add_argument('--'+param, default=pdval, help=f'{pdesc} [{pdval}]', action=parsbool)
            else:
                parser.add_argument('--'+param, default=pdval, help=f'{pdesc} [{pdval}]', type=ptype)

    return vars(parser.parse_args())

params = parsecommandline()

configfile  = str(pathlib.Path(__file__).parent.resolve())+'/../config/config.yaml'
templatedir = str(pathlib.Path(__file__).parent.resolve())+'/../templates'
email = os.environ.get('EMAIL')

with open(configfile) as fx:
    config = yaml.safe_load(fx)

maxkeylen=0
for key in config[params['system']]:
    params[key] = config[params['system']][key]
    maxkeylen=max(maxkeylen,len(key))
for key in params:
    print(f'{key+": ":>15} {str(params[key])}')

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

maxmem     = str(int(mempernode/taskpernode*1024))
mempernode = str(mempernode)+'G'

# # derived parameters
boxsize = params['boxsize']
N_nodes = max(1,Ntasks // taskpernode)
rsoft   = boxsize / params['N'] * params['soft']
if boxsize%1.0 == 0:
    boxsize = int(boxsize)
run     = str(boxsize)+"Mpc_n"+str(params['N'])+"_p"+str(params['Npm'])

# # make run directories
basedir = params['basedir']
if basedir == 'scratch':
    basedir = os.environ.get('SCRATCH')
rundir = basedir+"/simpipe/"+run
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
subprocess.call(f'sed -i -e "s/N_REPLACE/{N}/g"     {srcdir}/tmpfile', shell=True)
subprocess.call(f'sed -i -e "s/NPM_REPLACE/{Npm}/g" {srcdir}/tmpfile', shell=True)
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
if system == "s3df":
    subprocess.call(f'cat {templatedir}/launch-template.sh | grep -v CONST > {rundir}/tmpfile', shell=True)
    subprocess.call(f'sed -i -e "s/ACCT_REPLACE/{acct}/g" {rundir}/tmpfile', shell=True)
else:
    subprocess.call(f'cat {templatedir}/launch-template.sh | grep -v ACCT > {rundir}/tmpfile', shell=True)
    subprocess.call(f'sed -i -e "s/CONST_REPLACE/{constraint}/g" {rundir}/tmpfile', shell=True)

subprocess.call(f'sed -i -e "s/PART_REPLACE/{partition}/g"  {rundir}/tmpfile', shell=True)
subprocess.call(f'sed -i -e "s/NODES_REPLACE/{N_nodes}/g"   {rundir}/tmpfile', shell=True)
subprocess.call(f'sed -i -e "s/RUN_REPLACE/{run}/g"         {rundir}/tmpfile', shell=True)
subprocess.call(f'sed -i -e "s:DIR_REPLACE:{rundir}:g"      {rundir}/tmpfile', shell=True)
subprocess.call(f'sed -i -e "s/EMAIL_REPLACE/{email}/g"     {rundir}/tmpfile', shell=True)
subprocess.call(f'sed -i -e "s/TPN_REPLACE/{taskpernode}/g" {rundir}/tmpfile', shell=True)
subprocess.call(f'sed -i -e "s/MPN_REPLACE/{mempernode}/g"  {rundir}/tmpfile', shell=True)
subprocess.call(f'sed -i -e "s/EMAIL_REPLACE/{email}/g"     {rundir}/tmpfile', shell=True)
subprocess.call(f'sed -i -e "s:ENVPATH_REPLACE:{env}:g"     {rundir}/tmpfile', shell=True)
subprocess.call(f'sed -i -e "s/NTASK_REPLACE/{Ntasks}/g"    {rundir}/tmpfile', shell=True)
subprocess.call(f'sed -i -e "s/MPIEXE_REPLACE/{mpiexe}/g"   {rundir}/tmpfile', shell=True)
subprocess.call(f'mv {rundir}/tmpfile {rundir}/launch.sh', shell=True)

# compile gadget
if params['drylev'] >= 2:
    print(f"  DRY RUN: cd {srcdir}")
    print(f"  DRY RUN: make clean &> /dev/null")
    print(f"  DRY RUN: make -j 32 &> {srcdir}/build.log")
else:
    print("  compiling Gadget4 ...")
    subprocess.call(f"cd {srcdir} ; rm -f build.log", shell=True)
    subprocess.call(f"cd {srcdir} ; make clean &> /dev/null", shell=True)
    subprocess.call(f"cd {srcdir} ; make -j 32 &> {srcdir}/build.log", shell=True)

# launch job
if params['drylev'] >= 1:
    print(f"  DRY RUN: sbatch {rundir}/launch.sh")
else:
    if not os.path.isfile(f"{srcdir}/Gadget4"): 
        print(f"  executable {srcdir}/Gadget4 not found")
        print(f"    see {srcdir}/build.log for details")
        exit()
    subprocess.call(f"sbatch {rundir}/launch.sh", shell=True)

