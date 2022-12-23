#!/bin/bash
# to submit dependent jobs for dynamic harmonic walls
# Polly Ren, Dec 2022

current_npt = 3

harwall_force = 1           # force of harmonicWall 
npt_steps = 500000          # number of steps for each npt run (how often wall is recalculated)
total_runs = 10
last_npt = $((current_npt + total_runs))

for i in {$current_npt..$last_npt}; 
do
    create_minmaxtcl = $(sbatch run.sh $current_npt create_minmaxtcl | cut -f 4 -d' ')
    create_minmax_sbatch = $(sbatch --dependency=afterok:$create_minmaxtcl run.sh $current_npt minmax_sbatch | cut -f 4 -d' ')
    minmax_submit = $(sbatch --dependency=afterok:$create_minmax_sbatch minmax-npt$current_npt.sh | cut -f 4 -d' ')

    create_centretcl = $(sbatch --dependency=afterok:$minmax_submit run.sh $current_npt create_centretcl | cut -f 4 -d' ')
    create_centre_sbatch = $(sbatch --dependency=afterok:$create_centretcl run.sh $current_npt centre_sbatch | cut -f 4 -d' ')
    centre_submit = $(sbatch --dependency=afterok:$create_centre_sbatch centre-npt$current_npt.sh | cut -f 4 -d' ')

    create_colvars = $(sbatch --dependency=afterok:$centre_submit run.sh $current_npt create_colvars $harwall_force | cut -f 4 -d' ')
    create_conf = $(sbatch --dependency=afterok:$create_colvars run.sh $current_npt create_colvars $npt_steps | cut -f 4 -d' ')
    create_sh = $(sbatch --dependency=afterok:$create_conf run.sh $current_npt job_submit | cut -f 4 -d' ')
    job_submit = $(sbatch --dependency=afterok:$create_sh npt$current_npt-consec.sh | cut -f 4 -d' ')

    current_npt = $((current_npt + 1))
done