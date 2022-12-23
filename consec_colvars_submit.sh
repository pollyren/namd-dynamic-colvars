#!/bin/bash
# to submit dependent jobs for dynamic harmonic walls
# Polly Ren, Dec 2022

current_npt = 3

harwall_force = 1           # force of harmonicWall 
npt_steps = 500000          # number of steps for each npt run (how often wall is recalculated)

# centre
midx, midy, midz = 14, 2, -8
# midpoints
minx = -10
maxx = 39
miny = -22
maxy = 32
minz = -22
maxz = 12

deltax = max(midx - minx, maxx - midx)
deltay = max(midy - miny, maxy - midy)
deltaz = max(midz - minz, maxz - midz)

minx, maxx = midx - deltax, midx + deltax
miny, maxy = midy - deltay, midy + deltay
minz, maxz = midz - deltaz, midz + deltaz

# how much to lower the wall by from the starting values
lower = -decrement
minx += lower
miny += lower
minz += lower
maxx -= lower
maxy -= lower
maxz -= lower

function read_minmax_dat() {
    line_number = 0
    while read line
    do 
        case $line_number in
            0) 
                minx = $line
                ;;
            1) 
                miny = $line
                ;;
            2)
                minz = $line
                ;;
            3) 
                maxx = $line
                ;;
            4) 
                maxy = $line
                ;;
            5)
                maxz = $line
                ;;
        esac
        line_number=$((line_number+1))
    done < $1
}

function read_centre_dat() {
    line_number = 0
    while read line
    do 
        case $line_number in
            0) 
                midx = $line
                ;;
            1) 
                midy = $line
                ;;
            2)
                midz = $line
                ;;
        esac
        line_number=$((line_number+1))
    done < $1
}

create_minmaxtcl = $(sbatch run.sh $current_npt create_minmaxtcl | cut -f 4 -d' ')
create_minmax_sbatch = $(sbatch --dependency=afterok:$create_minmaxtcl run.sh $current_npt minmax_sbatch | cut -f 4 -d' ')
minmax_submit = $(sbatch --dependency=afterok:$create_minmax_sbatch minmax-npt$current_npt.sh | cut -f 4 -d' ')

create_centretcl = $(sbatch --dependency=afterok:$minmax_submit run.sh $current_npt create_centretcl | cut -f 4 -d' ')
create_centre_sbatch = $(sbatch --dependency=afterok:$create_centretcl run.sh $current_npt centre_sbatch | cut -f 4 -d' ')
centre_submit = $(sbatch --dependency=afterok:$create_centre_sbatch centre-npt$current_npt.sh | cut -f 4 -d' ')

create_colvars = $(sbatch --dependency=afterok:$centre_submit run.sh $current_npt create_colvars $midx $midy $midz $minx $miny $minz $maxx $maxy $maxz $harwall_force | cut -f 4 -d' ')