#!/bin/bash -l
#SBATCH --partition=PART_REPLACE
#SBATCH --account=ACCT_REPLACE
#SBATCH -t 24:00:00
#SBATCH -C CONST_REPLACE
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=EMAIL_REPLACE
#SBATCH --nodes=NODES_REPLACE
#SBATCH --ntasks-per-node=TPN_REPLACE
#SBATCH --cpus-per-task=1
#SBATCH -J RUN_REPLACE
#SBATCH --output=DIR_REPLACE/RUN_REPLACE.%j.oe
#SBATCH --mem=MPN_REPLACE

source ENVPATH_REPLACE/load-env.sh
export OMPI_MCA_osc_sm_backing_directory=/tmp # fix for "not enough space for /dev/shm/osc_sm/..."
ulimit -n 10240
cd DIR_REPLACE

cd gadget4 ; make -j TPN_REPLACE ; cd ..

echo '====Gadget4============================================'
date
MPIEXE_REPLACE -n NTASK_REPLACE ./gadget4/Gadget4 param.txt
date
