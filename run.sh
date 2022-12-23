#!/bin/bash
#SBATCH --job-name=run python
#SBATCH --time=36:00:00
#SBATCH --exclusive
#SBATCH --partition=caslake
#SBATCH --nodes=6
#SBATCH --ntasks-per-node=48
#SBATCH --account=pi-haddadian

ARG1 = ${1:-0}  # current npt
ARG2 = ${2:-0}  # function name
ARG3 = ${3:-0}  # function param (optional)

module load python
python consec_colvars.py $1 $2 $3