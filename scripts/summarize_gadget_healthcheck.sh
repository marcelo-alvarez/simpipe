#!/bin/bash

bench="s3df-2" ; if [ ! -z $1 ] ; then bench=$1 ; fi

if [ $bench == "s3df-2" ] ; then 
    rundir=/sdf/scratch/users/m/malvarez/simpipe/
elif [ $bench == "s3df-1" ] ; then
    rundir=/sdf/home/t/tabel/launchjobs/last/
elif [ $bench == "sherlock-1" ] ; then 
    rundir=/scratch/users/marceloa/simpipe/
fi
outdir=$PWD

summaryfile=$outdir/summary_$bench.txt
tmpfile=$outdir/tmp
header=$outdir/head

cd $rundir
rm -f $tmpfile $header
echo "run Nnodes CPU CPU-var hypercube hypercube-var internode internode-var intranode intranode-var" >> $header
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

cat $header $tmpfile | column -t --table-right 1,2,3,4,5,6,7,8,9      >> $summaryfile
sed -i -e "s/___/   /g" $summaryfile
cat $summaryfile
rm -f $tmpfile $header
