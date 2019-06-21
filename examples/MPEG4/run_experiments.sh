#!/bin/bash

FBINARY=forsyde-sadf-exe
CBINARY=/home/rbonna/Documents/mpeg-systemC/sources/a.out
EXP_FILE=experiments.dat
PYTHON_MPEG=~/Documents/python-MoC/examples/MPEG4/MPEG4.py
MBINP_PATH=/home/rbonna/Documents/python-MoC/examples/MPEG4/mbInputs.inp
FTINP_PATH=/home/rbonna/Documents/python-MoC/examples/MPEG4/ft.inp

bss="8"
samps="200"
fss="8 16"     # 32 64 128 256"

echo "" > $EXP_FILE
for bs in $bss; do
    for fs in $fss; do
	      for nSamp in $samps; do
	        echo "Running for fsx=$fs fsy=$fs bs=$bs nsamp=$nSamp..."
          python3 $PYTHON_MPEG $fs $fs $bs $nSamp >> $EXP_FILE
	        $FBINARY $fs $fs $bs $FTINP_PATH $MBINP_PATH >> $EXP_FILE
          $CBINARY $fs $fs $bs $nSamp $FTINP_PATH $MBINP_PATH >> $EXP_FILE
          echo ----------------- >> $EXP_FILE
	      done
    done
done
