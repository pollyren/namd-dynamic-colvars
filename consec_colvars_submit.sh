#!/bin/bash
# to submit dependent jobs for dynamic harmonic walls
# Polly Ren, Dec 2022

current_npt = 3

create_minmaxtcl = $(sbatch run.sh $current_npt create_minmaxtcl | cut -f 4 -d' ')

minmax = $(sbatch minmax-npt$current_npt.sh | cut -f 4 -d' ')
centre = $(sbatch centre-npt$current_npt.sh | cut -f 4 -d' ')
# create_
create_new_colvar = $(sbatch minmax-npt$current_npt.sh | cut -f 4 -d' ')
create_new_conf = 
submit
python

jobID_1=$(sbatch minmax-npt$current_npt.sh | cut -f 4 -d' ')

jobID_2=$(sbatch --dependency=afterok:$jobID_1 npt3.sh | cut -f 4 -d' ')

jobID_3=$(sbatch --dependency=afterok:$jobID_2 npt4.sh | cut -f 4 -d' ')

jobID_4=$(sbatch --dependency=afterok:$jobID_3 npt5.sh | cut -f 4 -d' ')

jobID_5=$(sbatch --dependency=afterok:$jobID_4 npt6.sh | cut -f 4 -d' ')

jobID_6=$(sbatch --dependency=afterok:$jobID_5 npt7.sh | cut -f 4 -d' ')

jobID_7=$(sbatch --dependency=afterok:$jobID_6 npt8.sh | cut -f 4 -d' ')

jobID_8=$(sbatch --dependency=afterok:$jobID_7 npt9.sh | cut -f 4 -d' ')

jobID_9=$(sbatch --dependency=afterok:$jobID_8 npt10.sh | cut -f 4 -d' ')

sbatch --dependency=afterok:$jobID_9 npt11.sh
