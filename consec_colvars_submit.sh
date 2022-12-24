#!/bin/bash
# to submit dependent jobs for dynamic harmonic walls
# Polly Ren, Dec 2022

echo $$ > /tmp/consec_colvars_submit.pid
# to check if nohup is done running: ps -p `cat /tmp/consec_colvars_submit.pid`

current_npt=4
prev_npt=$((current_npt-1))

harwall_force=1           # force of harmonicWall 
npt_steps=500000          # number of steps for each npt run (how often wall is recalculated)
total_runs=100
last_npt=$((current_npt+total_runs))

for ((i=0; i<$total_runs; i++));
do
    # python consec_colvars.py $prev_npt create_minmaxtcl 0
    # python consec_colvars.py $prev_npt minmax_sbatch 0
    create_minmaxtcl=$(sbatch --wait run.sh $prev_npt create_minmaxtcl | cut -f 4 -d' ')
    create_minmax_sbatch=$(sbatch --wait --dependency=afterok:$create_minmaxtcl run.sh $prev_npt minmax_sbatch | cut -f 4 -d' ')
    minmax_submit=$(sbatch --wait --dependency=afterok:$create_minmax_sbatch minmax-npt$prev_npt.sh | cut -f 4 -d' ')

    # python consec_colvars.py $prev_npt create_centretcl 0
    # python consec_colvars.py $prev_npt centre_sbatch 0
    create_centretcl=$(sbatch --wait --dependency=afterok:$minmax_submit run.sh $prev_npt create_centretcl | cut -f 4 -d' ')
    create_centre_sbatch=$(sbatch --wait --dependency=afterok:$create_centretcl run.sh $prev_npt centre_sbatch | cut -f 4 -d' ')
    centre_submit=$(sbatch --wait --dependency=afterok:$create_centre_sbatch centre-npt$prev_npt.sh | cut -f 4 -d' ')

    create_colvars=$(sbatch --wait --dependency=afterok:$centre_submit run.sh $current_npt create_colvars $harwall_force | cut -f 4 -d' ')
    create_conf=$(sbatch --wait --dependency=afterok:$create_colvars run.sh $current_npt create_conf $npt_steps | cut -f 4 -d' ')
    create_sh=$(sbatch --wait --dependency=afterok:$create_conf run.sh $current_npt job_submit | cut -f 4 -d' ')
    # python consec_colvars.py $current_npt create_colvars $harwall_force
    # python consec_colvars.py $current_npt create_conf $npt_steps
    # python consec_colvars.py $current_npt job_submit 0
    job_submit=$(sbatch --wait --dependency=afterok:$create_sh npt$current_npt-consec.sh | cut -f 4 -d' ')

    prev_npt=$current_npt
    current_npt=$((current_npt + 1))
done