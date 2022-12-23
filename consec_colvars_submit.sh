#!/bin/bash
# to submit dependent jobs for dynamic harmonic walls
# Polly Ren, Dec 2022

current_npt = 3

create_minmaxtcl = $(sbatch run.sh $current_npt create_minmaxtcl | cut -f 4 -d' ')
create_minmax_sbatch = $(sbatch --dependency=afterok:$create_minmaxtcl run.sh $current_npt minmax_sbatch | cut -f 4 -d' ')
minmax_submit = $(sbatch --dependency=afterok:$create_minmax_sbatch minmax-npt$current_npt.sh | cut -f 4 -d' ')

create_centretcl = $(sbatch run.sh $current_npt create_centretcl | cut -f 4 -d' ')
create_centre_sbatch = $(sbatch --dependency=afterok:$create_centretcl run.sh $current_npt centre_sbatch | cut -f 4 -d' ')
centre_submit = $(sbatch --dependency=afterok:$create_centre_sbatch centre-npt$current_npt.sh | cut -f 4 -d' ')

