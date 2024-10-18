#!/bin/bash

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $SCRIPTPATH/load-env.sh

ncompile_threads=32

gsl=1
gsl_version=gsl-2.8

fftw3=1
fftw3_version=fftw-3.3.10

hdf5=1
hdf5_version=hdf5-1.14.4-3

locallib=$simpipedir/lib/
localinc=$simpipedir/include/

mkdir -p $locallib
mkdir -p $localinc

rm -rf $locallib/*
rm -rf $localinc/*

# GSL
if [ $simpipesys == "sherlock" ] ; then
    ln -s /share/software/user/open/gsl/2.7/lib/*     $locallib
    ln -s /share/software/user/open/gsl/2.7/include/* $localinc
elif [ $gsl -gt 0 ] ; then
    cd $SCRATCH
    rm -rf $gsl_version
    wget https://mirror.fcix.net/gnu/gsl/$gsl_version.tar.gz
    tar -zxvf $gsl_version.tar.gz; rm -f $gsl_version.tar.gz
    cd $gsl_version
    ./configure --prefix=$PWD
    make -j$ncompile_threads
    make install -j$ncompile_threads

    cp -r $SCRATCH/$fftw3_version/include/gsl $localinc/
    cp $SCRATCH/$fftw3_version/lib/*     $locallib
fi

# FFTW3
if [ $fftw3 -gt 0 ] ; then
    cd $SCRATCH ; rm -rf $fftw3_version
    wget https://www.fftw.org/$fftw3_version.tar.gz
    tar -zxvf $fftw3_version.tar.gz; rm -f $fftw3_version.tar.gz
    cd $fftw3_version

    export cc=gcc
    export CC=gcc
    export F77=gfortran
    export CFLAGS=-O3
    #export I_MPI_CC=icc

    # float
    ./configure --enable-mpi --prefix=$PWD --enable-float
    make -j$ncompile_threads
    make install -j$ncompile_threads

    # double
    make clean
    ./configure --enable-mpi --prefix=$PWD
    make -j$ncompile_threads
    make install -j$ncompile_threads

    cp $SCRATCH/$fftw3_version/include/* $localinc
    cp $SCRATCH/$fftw3_version/lib/lib*  $locallib
fi

# HDF5
if [ $hdf5 -gt 0 ] ; then
    cd $SCRATCH ; rm -rf $hdf5_version
    wget https://github.com/HDFGroup/hdf5/releases/download/hdf5_1.14.4.3/$hdf5_version.tar.gz
    tar -zxvf $hdf5_version.tar.gz; rm -f $hdf5_version.tar.gz
    cd $hdf5_version

    export cc=gcc
    export CC=gcc
    export F77=gfortran
    export CFLAGS=-O3

    ./configure --prefix=$PWD  --enable-cxx
    make -j$ncompile_threads
    make install -j$ncompile_threads

    cp $SCRATCH/$hdf5_version/include/* $localinc
    cp $SCRATCH/$hdf5_version/lib/*     $locallib
fi
