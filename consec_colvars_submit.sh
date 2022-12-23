#!/bin/bash
# to submit dependent jobs from npt2 to npt11
# Polly Ren, 9/27/2022

jobID_1=$(sbatch npt2.sh | cut -f 4 -d' ')

jobID_2=$(sbatch --dependency=afterok:$jobID_1 npt3.sh | cut -f 4 -d' ')

jobID_3=$(sbatch --dependency=afterok:$jobID_2 npt4.sh | cut -f 4 -d' ')

jobID_4=$(sbatch --dependency=afterok:$jobID_3 npt5.sh | cut -f 4 -d' ')

jobID_5=$(sbatch --dependency=afterok:$jobID_4 npt6.sh | cut -f 4 -d' ')

jobID_6=$(sbatch --dependency=afterok:$jobID_5 npt7.sh | cut -f 4 -d' ')

jobID_7=$(sbatch --dependency=afterok:$jobID_6 npt8.sh | cut -f 4 -d' ')

jobID_8=$(sbatch --dependency=afterok:$jobID_7 npt9.sh | cut -f 4 -d' ')

jobID_9=$(sbatch --dependency=afterok:$jobID_8 npt10.sh | cut -f 4 -d' ')

sbatch --dependency=afterok:$jobID_9 npt11.sh
