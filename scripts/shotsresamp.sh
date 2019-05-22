#!/usr/bin/bash
# Resample shot records

fac=0.5
filenm='Up_file_single.su'
sdir=../obs2ms
mkdir -p $sdir

for shot in `ls -d ????`
do
  odir=$sdir/$shot
  mkdir -p $odir
  echo "Resampling $shot/$filenm  TO  $odir/$filenm"
  suoldtonew < $shot/$filenm  |suresamp rf=$fac \
  |suswapbytes format=0 > $odir/$filenm
done
