#!/bin/bash

BINARY=forsyde-sadf-exe
EXP_FILE=experiments.dat
PYTHON_MPEG=~/Documents/python-MoC/examples/MPEG4/MPEG4.py
MBINP_PATH=~/Documents/python-MoC/examples/MPEG4/mbInputs.inp
FTINP_PATH=~/Documents/python-MoC/examples/MPEG4/ft.inp

bss="8"
samps="100"
fss="16 32 64 128"

echo "" > $EXP_FILE
for bs in $bss; do
    for fs in $fss; do
	      for nSamp in $samps; do
	        echo "Running for fsx=$fs fsy=$fs bs=$bs nsamp=$nSamp..."
          python3 $PYTHON_MPEG $fs $fs $bs $nSamp >> $EXP_FILE
	        $BINARY $fs $fs $bs $FTINP_PATH $MBINP_PATH >> $EXP_FILE
          echo ----------------- >> $EXP_FILE
	      done
    done
done
