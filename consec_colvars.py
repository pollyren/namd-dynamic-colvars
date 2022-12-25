#!/usr/bin/python
import sys
import os
import time
import re

def sbatch_string(job_name: str) -> str:
    """
    Generates a string for the sbatch file header.

    Inputs:
        job_name (string): name of the job

    Output: a string containing the header of the sbatch file (string)
    """
    string = "#!/bin/sh\n#SBATCH --job-name={}\n#SBATCH --time=36:00:00\n#SBATCH --exclusive\n#SBATCH --partition=caslake\n#SBATCH --nodes=6\n#SBATCH --ntasks-per-node=48\n#SBATCH --account=pi-haddadian\n\n".format(str(job_name))
    return string

def create_colvars(input_npt: int, harwall_force: int, distance: int) -> None:
    """
    Creates the colvars file for a single npt run.

    Inputs:
        input_npt (int): current npt number
        harwall_force (int): force for harmonicWall constraint
        distance (int): distance of wall from backbone of protein

    Output: None
    """
    mid = read_centre("centre_npt{}.dat".format(input_npt-1))
    minmax = read_minmax("minmax_npt{}.dat".format(input_npt-1))
    midx = mid[0]
    midy = mid[1]
    midz = mid[2]
    minx = minmax[0]
    miny = minmax[1]
    minz = minmax[2]
    maxx = minmax[3]
    maxy = minmax[4]
    maxz = minmax[5]
    # # take the larger difference so the protein COM is the centre of the box
    # deltax = max(midx - raw_minx, raw_maxx - midx)
    # deltay = max(midy - raw_miny, raw_maxy - midy)
    # deltaz = max(midz - raw_minz, raw_maxz - midz)
    # # create adjusted min and max values
    # minx, maxx = midx - deltax, midx + deltax
    # miny, maxy = midy - deltay, midy + deltay
    # minz, maxz = midz - deltaz, midz + deltaz
    # reduce by distance of wall from protein
    minx -= distance
    miny -= distance
    minz -= distance
    maxx += distance
    maxy += distance
    maxz += distance

    file = colv_root + str(input_npt) + ".conf"
    with open(file, "w") as f:
        f.write("# colvars for npt{}\n".format(str(input_npt)))
        # x colvars
        f.write("colvar {\n\tname xCOM\n\tdistanceZ {\n\t\tmain {\n\t\t\tatomNumbers {")
        f.write(' '.join(str(ind) for ind in index_list))
        f.write("}}\n\t\t}}\n\t\tref {{\n\t\t\tdummyAtom ({},{},{})\n\t\t}}\n\t\taxis {{\n\t\t\t(1, 0, 0)\n\t\t}}\n\t}}\n}}".format(midx, midy, midz))
        # print("harmonic {\n\tcolvars\txCOM\n\tcenters\t0\n\tforceConstant\t10\n}")
        f.write(
            "\n\nharmonicWalls {\n\tcolvars xCOM" + 
            "\n\tlowerWalls " + str(minx) + 
            "\n\tupperWalls " + str(maxx) + 
            "\n\tforceConstant {}\n}}\n".format(harwall_force))

        # y colvars
        f.write("colvar {\n\tname yCOM\n\tdistanceZ {\n\t\tmain {\n\t\t\tatomNumbers {"),
        f.write(' '.join(str(ind) for ind in index_list))
        f.write("}}\n\t\t}}\n\t\tref {{\n\t\t\tdummyAtom ({},{},{})\n\t\t}}\n\t\taxis {{\n\t\t\t(0, 1, 0)\n\t\t}}\n\t}}\n}}".format(midx, midy, midz))
        # print("harmonic {\n\tcolvars\tyCOM\n\tcenters\t0\n\tforceConstant\t10\n}")
        f.write(
            "\n\nharmonicWalls {\n\tcolvars yCOM" + 
            "\n\tlowerWalls " + str(miny) + 
            "\n\tupperWalls " + str(maxy) + 
            "\n\tforceConstant {}\n}}\n".format(harwall_force))

        # z colvars
        f.write("colvar {\n\tname zCOM\n\tdistanceZ {\n\t\tmain {\n\t\t\tatomNumbers {"),
        f.write(' '.join(str(ind) for ind in index_list))
        f.write("}}\n\t\t}}\n\t\tref {{\n\t\t\tdummyAtom ({},{},{})\n\t\t}}\n\t\taxis {{\n\t\t\t(0, 0, 1)\n\t\t}}\n\t}}\n}}".format(midx, midy, midz))
        # print("harmonic {\n\tcolvars\tzCOM\n\tcenters\t0\n\tforceConstant\t10\n}")
        f.write(
            "\n\nharmonicWalls {\n\tcolvars zCOM" + 
            "\n\tlowerWalls " + str(minz) + 
            "\n\tupperWalls " + str(maxz) + 
            "\n\tforceConstant {}\n}}".format(harwall_force))

def create_conf(input_npt: int, npt_steps: int) -> None: 
    """
    Creates the configuration file for a single npt run.

    Inputs:
        input_npt (int): current npt number
        npt_steps (int): number of steps to run a single npt

    Output: None
    """
    file = conf_root + str(input_npt) + ".conf"
    config = '''#---------------Temperature -----------------------------------------------------------------
set temperature		    300	

#---------------NPT---------------------------------------------------------------------------
Langevin				on
LangevinTemp			$temperature
LangevinDamping			1
LangevinPiston			on
LangevinPistonTarget	1.01325
LangevinPistonPeriod	100
LangevinPistonDecay		50
LangevinPistonTemp		$temperature
useFlexibleCell			no
useConstantRatio		no
margin					1
useGroupPressure		no

#---------------Timestep parameters----------------------------------------------------
timestep			    2
stepspercycle		    10

#---------------Input Files------------------------------------------------------------
coordinates             ubq-denatured-solvate-ionised-LFmini.pdb
structure               ubq-denatured-solvate-ionised.psf
set inputname           ubq-consec-npt{}
bincoordinates	        $inputname.coor
binvelocities	        $inputname.vel
extendedsystem	        $inputname.xsc

#---------------------Output Controls----------------------------------------------------
outputname              ubq-consec-npt{}
restartfreq		        1000
restartname             ubq-consec-npt{}
dcdfreq		            2500
XSTFreq		            1000
OutputEnergies	        1000

#---------------Parameter Files---------------------------------------------------------
paraTypeCharmm          on
parameters		        par_all36m_prot.prm
parameters              toppar_water_ions_esmael.str
parameters		        toppar_water_ions_tip4p_2005_Modified_Shriya.str
waterModel		        tip4

#---------------NonBonded Interactions--------------------------------------------------
exclude			        scaled1-4
1-4scaling		        1
switching		        on
cutoff			        12
switchdist		        10
pairlistdist		    13.5
nonBondedFreq			1
fullElectFrequency		2
rigidBonds		        all

#---------------Wrapping ------------------------------------------------------------------
wrapAll		            on

#---------------Colvars--------------------------------------------------------------------
colvars                 on
colvarsConfig           ubq_colvars_consec_npt{}.conf

#---------------Periodic boundary Conditions ----------------------------------------------
cellBasisVector1   	    123.95     0.00      0.00
cellBasisVector2   	    0.00       81.18     0.00
cellBasisVector3   	    0.00       0.00      81.22
cellOrigin	            0.00       0.00      0.00

#---------------PME Parameters -------------------------------------------------------------
PME		                yes
PMEGridSpacing	        0.6
run {}'''.format(input_npt-1, input_npt, input_npt, input_npt, npt_steps)
    with open(file, "w") as f:
        f.write(config)

def create_minmaxtcl(input_npt: int) -> None:
    """
    Creates the tcl script to measure the boundaries of the protein after a npt run.

    Inputs:
        input_npt (int): current npt number

    Output: None
    """
    file = "minmax-npt" + str(input_npt) + ".tcl"
    minmaxtcl = '''set psf  ubq-denatured-solvate-ionised.psf
set dcd  ubq-consec-npt{}.dcd
mol load psf $psf dcd $dcd

set sel [atomselect top "protein" frame last]
set measure [measure minmax $sel]

set outfile [open ./minmax_npt{}.dat w]
for {{set i 0}} {{$i < 2}} {{incr i}} {{
    for {{set j 0}} {{$j < 3}} {{incr j}} {{
        puts $outfile [lindex $measure $i $j]
    }}
}}
close $outfile
$sel delete
mol delete top'''.format(input_npt, input_npt)
    with open(file, "w") as f:
        f.write(minmaxtcl)

def minmax_sbatch(input_npt: int) -> None:
    """
    Creates the sbatch script to submit minmax job.

    Inputs:
        input_npt (int): current npt number

    Output: None
    """
    file = "minmax-npt" + str(input_npt) + ".sh"
    s = sbatch_string("minmax_npt{}".format(input_npt))
    sh = "module load vmd\nvmd -e minmax-npt{}.tcl".format(input_npt)
    with open(file, "w") as f:
        f.write(s)
        f.write(sh)

def create_centretcl(input_npt: int) -> None:
    """
    Creates the tcl file to identify the centre of the protein after a npt run.

    Inputs:
        input_npt (int): current npt number

    Output: None
    """
    file = "centre-npt" + str(input_npt) + ".tcl"
    centretcl = '''set psf  ubq-denatured-solvate-ionised.psf
set dcd  ubq-consec-npt{}.dcd
mol load psf $psf dcd $dcd

set sel [atomselect top "protein" frame last]
set measure [measure center $sel]

set outfile [open ./centre_npt{}.dat w]
for {{set i 0}} {{$i < 3}} {{incr i}} {{
    puts $outfile [lindex $measure $i]
}}
close $outfile
$sel delete
mol delete top'''.format(input_npt, input_npt)
    with open(file, "w") as f:
        f.write(centretcl)

def centre_sbatch(input_npt: int) -> None:
    """
    Creates the sbatch script to submit centre job.

    Inputs:
        input_npt (int): current npt number

    Output: None
    """
    file = "centre-npt" + str(input_npt) + ".sh"
    s= sbatch_string("centre_npt{}".format(input_npt))
    sh = "module load vmd\nvmd -e centre-npt{}.tcl".format(input_npt)
    with open(file, "w") as f:
        f.write(s)
        f.write(sh)

def read_minmax(input: str) -> list:
    """
    Reads the values after measuring minmax and stores values in an array.

    Inputs:
        input (string): file name to read from

    Output: an array containing the minimum and maximum values (list)
    """
    array = []
    f = open(input, "r")
    line = f.readline()
    while line:
        array.append(float(line))
        line = f.readline()
    f.close()
    return array

def read_centre(input: str) -> list:
    """
    Reads the values after measuring centre and stores values in an array.

    Inputs:
        input (string): file name to read from

    Output: an array containing the centre values (list)
    """
    array = []
    f = open(input, "r")
    line = f.readline()
    while line:
        array.append(float(line))
        line = f.readline()
    f.close()
    return array

def job_submit(input_npt: int) -> None:
    """
    Creates the sbatch script to submit the npt production run.

    Inputs:
        input_npt (int): current npt number

    Output: None
    """
    file = "npt" + str(input_npt) + "-consec.sh"
    s = sbatch_string("npt{}-consec".format(input_npt))
    input = conf_root + str(input_npt)
    sh = "module load namd/2.14\n\nmpiexec.hydra -bootstrap=slurm namd2 \"{}.conf\" > \"{}.log\"".format(input, input)
    with open(file, "w") as f:
        f.write(s)
        f.write(sh)

def smart_submit(job_name: str) -> None:
    """
    Submits a job and checks for the job's completion in the queue.

    Inputs:
        job_name (string): name of the script to be submitted, including file extension

    Output: None
    """
    cmd = os.popen("sbatch " + job_name)
    time.sleep(2)
    jobid = re.search("(\d+)", cmd.readlines()[0]).group(1)
    cmd.close()
    print(jobid)
    while True:
        time.sleep(60)
        squeue = os.popen("squeue -u {}".format(username))
        time.sleep(2)
        queue = "\n".join(squeue.readlines())
        squeue.close()
        if jobid not in queue:
            break

if __name__ == "__main__":
    """
    Usage: python consec_colvars.py start_npt total_runs_per_distance decrement_dist npt_steps harwall_force
           start_npt (int): starting npt number, the first npt to be run in this sequence
           distance (int): wall distance from the minmax of the protein
           total_runs_per_distance (int): number of npts to run at each wall distance
           npt_steps (int): number of steps between wall recalculation 
           harwall_force (int): force of colvars harmonic wall
    """
    start_npt = int(sys.argv[1])
    distance = int(sys.argv[2])
    total_runs_per_distance = int(sys.argv[3])
    npt_steps = int(sys.argv[4])
    harwall_force = int(sys.argv[5])

    global username
    name = os.popen("whoami")
    time.sleep(1)
    username = name.readlines()[0].strip()
    name.close()

    global conf_root, colv_root
    conf_root = "ubq-consec-npt" 
    colv_root = "ubq_colvars_consec_npt"

    index = "0 4 17 18 19 21 34 35 36 38 53 54 55 57 73 74 75 77 89 90 91 93 111 112 113 115 125 126 127 129 144 145 146 148 158 159 160 162 165 166 167 169 187 188 189 191 201 202 203 205 220 221 222 224 234 235 236 238 253 254 255 257 268 269 270 272 284 285 286 288 299 300 301 305 313 314 315 317 324 325 326 328 336 337 338 340 350 351 352 354 369 370 371 373 384 385 386 388 398 399 400 402 414 415 416 418 436 437 438 440 446 447 448 450 468 469 470 472 487 488 489 491 504 505 506 508 516 517 518 520 538 539 540 542 553 554 555 557 560 561 562 564 579 580 581 585 593 594 595 599 607 608 609 611 619 620 621 623 636 637 638 640 653 654 655 657 677 678 679 681 696 697 698 700 715 716 717 719 735 736 737 739 745 746 747 749 752 753 754 756 774 775 776 778 791 792 793 795 810 811 812 814 825 826 827 829 837 838 839 841 844 845 846 848 868 869 870 872 882 883 884 886 901 902 903 905 912 913 914 916 924 925 926 928 945 946 947 949 959 960 961 963 978 979 980 982 995 996 997 999 1017 1018 1019 1021 1032 1033 1034 1036 1043 1044 1045 1047 1057 1058 1059 1061 1076 1077 1078 1080 1093 1094 1095 1097 1112 1113 1114 1116 1128 1129 1130 1132 1147 1148 1149 1151 1171 1172 1173"
    index_list = index.split()
    index_list = [int(i) + 1 for i in index_list]   # increment indices by 1 for colvars because colvar indexing is 1-based

    # for npt_runs in range(num_npts):
    for run in range(total_runs_per_distance):
        npt = run + start_npt
        create_minmaxtcl(npt-1)
        minmax_sbatch(npt-1)
        create_centretcl(npt-1)
        centre_sbatch(npt-1)
        smart_submit("minmax-npt{}.sh".format(str(npt-1)))  # edit sbatch functions so that file name is returned?
        smart_submit("centre-npt{}.sh".format(str(npt-1)))
        create_colvars(npt, harwall_force, distance)
        create_conf(npt, npt_steps)
        job_submit(npt)
        smart_submit("npt{}-consec.sh".format(str(npt)))
        # start_distance -= decrement_dist