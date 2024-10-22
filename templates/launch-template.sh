#!/bin/bash -l
#SBATCH --partition=PART_REPLACE
#SBATCH --account=ACCT_REPLACE
#SBATCH -t 24:00:00
#SBATCH -C CONST_REPLACE
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=EMAIL_REPLACE
#SBATCH --nodes=NODES_REPLACE
#SBATCH --ntasks-per-node=TPN_REPLACE
#SBATCH -J RUN_REPLACE
#SBATCH --output=DIR_REPLACE/RUN_REPLACE.%j.oe
#SBATCH --mem=MPN_REPLACE

source ENVPATH_REPLACE/load-env.sh

# based on error message "not enough space for /dev/shm/osc_sm/..."
export OMPI_MCA_osc_sm_backing_directory=/tmp

cd DIR_REPLACE

echo '====Gadget4============================================'
date
MPIEXE_REPLACE -n NTASK_REPLACE ./gadget4/Gadget4 param.txt
date
