#!/bin/bash

scriptdir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source $scriptdir/load-env.sh
alias python='python3'
shopt -s expand_aliases

run="s3df-2" ; if [ ! -z $1 ] ; then run=$1 ; fi

if [ $run == "s3df-2" ] ; then 
    rundir=/sdf/scratch/users/m/malvarez/simpipe
elif [ $run == "s3df-1" ] ; then
    rundir=/sdf/home/t/tabel/launchjobs/last
elif [ $run == "sherlock-1" ] ; then 
    rundir=/scratch/users/marceloa/simpipe/sherlock-benchmarks
fi

summarize_healthcheck () {
    rundir=$1
    outdir=$2
    cd $rundir
    summaryfile=$outdir/healthcheck_summary_$run.txt
    if [ -e $summaryfile ] ; then rm $summaryfile ; fi
    tmpfile=$outdir/tmp
    header=$outdir/head
    rm -f $tmpfile $header
    echo "run Nnodes CPU CPU-var hcube var inter var intra var" >> $header
    echo "___ ___ [sec] ___ [MB/s] ___ [MB/s] ___ [MB/s] ___" >> $header
    echo "___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ">> $header
    for file in $(ls */*/*out */*/*/*out */*oe 2> /dev/null); do
        dir=$(dirname $file)
        Nnodes=$(grep -E "SBATCH.*nodes" $dir/*.sh | tail -n 1 | awk -F= '{print $2}')
        cperf=$(grep -E "HEALTHTEST.*CPU performance" $file | awk '{print $4" "$6}')
        hyper=$(grep -E "HEALTHTEST.*hypercube"       $file | awk '{print $4" "$8}')
        inter=$(grep -E "HEALTHTEST.*Internode"       $file | awk '{print $4" "$8}')
        intra=$(grep -E "HEALTHTEST.*Intranode"       $file | awk '{print $6" "$10}')

        ncperf=${#cperf}
        nhyper=${#hyper}
        ninter=${#inter}
        nintra=${#intra}

        if [ $ncperf -eq 0 ] ; then cperf="- -" ; fi
        if [ $nhyper -eq 0 ] ; then hyper="- -" ; fi
        if [ $ninter -eq 0 ] ; then inter="- -" ; fi
        if [ $nintra -eq 0 ] ; then intra="- -" ; fi

        if [ $ncperf -gt 0 ] || [ $nhyper -gt 0 ] || [ $ninter -gt 0 ] || [ $nintra -gt 0 ] ; then
            echo "$dir $Nnodes $cperf $hyper $inter $intra" >> $tmpfile
        fi
    done
    sort -rk 2 -g -o $tmpfile $tmpfile

    echo "#" > $summaryfile
    echo "# Gadget-4 healthtest summary for data in $PWD" >> $summaryfile
    echo "#" >> $summaryfile

    cat $header $tmpfile | column -t      >> $summaryfile
    sed -i -e "s/___/   /g" $summaryfile
    echo ; cat $summaryfile
    rm -f $tmpfile $header
    printf "\n  Gadget-4 healthcheck summary written to: %s\n" $summaryfile
}

summarize_cpu () {
    rundir=$1
    outdir=$2
    step=$3
    cd $rundir
    summaryfile=$outdir/cpu_summary_$run.txt
    if [ -e $summaryfile ] ; then rm $summaryfile ; fi
    tmpfile=$outdir/tmp
    header=$outdir/head
    cpureader=$scriptdir/cpu.py
    echo "cpureader is $cpureader"
    rm -f $tmpfile $header
    echo "run Nnodes Ntasks step total tree_grav pm_grav" >> $header
    echo "___ ___ ___ ___ [hr] [hr] [hr]" >> $header
    echo "___ ___ ___ ___ ___ ___ ___">> $header
    for file in $(ls */output/cpu.csv */*/output/cpu.csv */*/*/output/cpu.csv 2> /dev/null); do
        dir=$(dirname $(dirname $file))
        Nnodes=$(grep -E "SBATCH.*nodes" $dir/*.sh    | tail -n 1 | awk -F= '{print $2}')
        Nper=$(grep -E "SBATCH.*ntasks-per" $dir/*.sh | tail -n 1 | awk -F= '{print $2}')
        # cperf=$(grep -E "HEALTHTEST.*CPU performance" $file | awk '{print $4" "$6}')
        # hyper=$(grep -E "HEALTHTEST.*hypercube"       $file | awk '{print $4" "$8}')
        # inter=$(grep -E "HEALTHTEST.*Internode"       $file | awk '{print $4" "$8}')
        # intra=$(grep -E "HEALTHTEST.*Intranode"       $file | awk '{print $6" "$10}')

        Ntasks=$(echo $Nnodes $Nper | awk '{print $1*$2}')
        CPU=$(python $cpureader $file $step "CPU_ALL2,CPU_TREE2,CPU_PM_GRAVITY2")
        rstep=$(   echo $CPU | awk '{print $1}')
        total=$(   echo $CPU $Ntasks| awk '{printf "%.0f", $2*$5/3600.}')
        treegrav=$(echo $CPU $Ntasks| awk '{printf "%.0f", $3*$5/3600.}')
        pmgrav=$(  echo $CPU $Ntasks| awk '{printf "%.0f", $4*$5/3600.}')

        echo "$dir $Nnodes $Ntasks $rstep $total $treegrav $pmgrav" >> $tmpfile
        # ncperf=${#cperf}
        # nhyper=${#hyper}
        # ninter=${#inter}
        # nintra=${#intra}

        # if [ $ncperf -eq 0 ] ; then cperf="- -" ; fi
        # if [ $nhyper -eq 0 ] ; then hyper="- -" ; fi
        # if [ $ninter -eq 0 ] ; then inter="- -" ; fi
        # if [ $nintra -eq 0 ] ; then intra="- -" ; fi

        # if [ $ncperf -gt 0 ] || [ $nhyper -gt 0 ] || [ $ninter -gt 0 ] || [ $nintra -gt 0 ] ; then
        #     echo "$dir $Nnodes $cperf $hyper $inter $intra" >> $tmpfile
        # fi
    done
    sort -rk 2 -g -o $tmpfile $tmpfile

    echo "#" >> $summaryfile
    echo "# Gadget-4 CPU summary for data in $PWD" >> $summaryfile
    echo "#" >> $summaryfile

    cat $header $tmpfile | column -t      >> $summaryfile
    sed -i -e "s/___/   /g" $summaryfile
    rm -f $tmpfile $header
    printf "\n  Gadget-4 CPU summary written to: %s\n" $summaryfile

    echo ; cat $summaryfile | grep -v \#

}

step=-1 ; if [ ! -z $2 ] ; then step=$2 ; fi

summarize_healthcheck $rundir $rundir
summarize_cpu         $rundir $rundir $step

