#!/bin/bash
#SBATCH --job-name=run python
#SBATCH --time=36:00:00
#SBATCH --exclusive
#SBATCH --partition=caslake
#SBATCH --nodes=6
#SBATCH --ntasks-per-node=48
#SBATCH --account=pi-haddadian

module load python
python consec_colvars.py $1 $2 $3 $4 $5 $6 $7 $8 $9 $10 $11 $12