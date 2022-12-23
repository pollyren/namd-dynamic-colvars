# consec_colvars.py:

starting_wall_dist = 0      # starting wall distance from the backbone of the protein
decrement = 0               # decrement wall_dist interval
freq = 0                    # frequency that the wall distance from edge of the protein is decremented
harwall_force = 1           # force of harmonicWall 
npt_steps = 500000          # number of steps for each npt run (how often wall is recalculated)

conf_root = "ubq-consec-npt" 
colv_root = "ubq_colvars_consec_npt"

index = "0 4 17 18 19 21 34 35 36 38 53 54 55 57 73 74 75 77 89 90 91 93 111 112 113 115 125 126 127 129 144 145 146 148 158 159 160 162 165 166 167 169 187 188 189 191 201 202 203 205 220 221 222 224 234 235 236 238 253 254 255 257 268 269 270 272 284 285 286 288 299 300 301 305 313 314 315 317 324 325 326 328 336 337 338 340 350 351 352 354 369 370 371 373 384 385 386 388 398 399 400 402 414 415 416 418 436 437 438 440 446 447 448 450 468 469 470 472 487 488 489 491 504 505 506 508 516 517 518 520 538 539 540 542 553 554 555 557 560 561 562 564 579 580 581 585 593 594 595 599 607 608 609 611 619 620 621 623 636 637 638 640 653 654 655 657 677 678 679 681 696 697 698 700 715 716 717 719 735 736 737 739 745 746 747 749 752 753 754 756 774 775 776 778 791 792 793 795 810 811 812 814 825 826 827 829 837 838 839 841 844 845 846 848 868 869 870 872 882 883 884 886 901 902 903 905 912 913 914 916 924 925 926 928 945 946 947 949 959 960 961 963 978 979 980 982 995 996 997 999 1017 1018 1019 1021 1032 1033 1034 1036 1043 1044 1045 1047 1057 1058 1059 1061 1076 1077 1078 1080 1093 1094 1095 1097 1112 1113 1114 1116 1128 1129 1130 1132 1147 1148 1149 1151 1171 1172 1173"
index_list = index.split()
index_list = [int(i) + 1 for i in index_list]   # increment indices by 1 for colvars because colvar indexing is 1-based

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

def sbatch_string(job_name):
    """
    Generates a string for the sbatch file header.

    Inputs:
        job_name (string): name of the job

    Output: a string containing the header of the sbatch file
    """
    string = "#!/bin/sh\n#SBATCH --job-name={}\n#SBATCH --time=36:00:00\n#SBATCH --exclusive\n#SBATCH --partition=caslake\n#SBATCH --nodes=6\n#SBATCH --ntasks-per-node=48\n#SBATCH --account=pi-haddadian\n".format(str(job_name))
    return string

def create_colvars(file):
    """
    Creates the colvars file for a single npt run.

    Inputs:
        file (string): file name to write to

    Output: None
    """
    with open(file, "w") as f:
    # x colvars
        f.write("colvar {\n\tname xCOM\n\tdistanceZ {\n\t\tmain {\n\t\t\tatomNumbers {")
        f.write(' '.join(index_list))
        f.write("}\n\t\t}\n\t\tref {\n\t\t\tdummyAtom ({},{},{}})\n\t\t}\n\t\taxis {\n\t\t\t(1, 0, 0)\n\t\t}\n\t}\n}".format(midx, midy, midz))
        # print("harmonic {\n\tcolvars\txCOM\n\tcenters\t0\n\tforceConstant\t10\n}")
        f.write(
            "harmonicWalls {\n\tcolvars xCOM" + 
            "\n\tlowerWalls " + str(minz) + 
            "\n\tupperWalls " + str(maxz) + 
            "\n\tforceConstant {}\n}\n".format(harwall_force))

        # y colvars
        f.write("colvar {\n\tname yCOM\n\tdistanceZ {\n\t\tmain {\n\t\t\tatomNumbers {"),
        f.write(' '.join(index_list))
        f.write("}\n\t\t}\n\t\tref {\n\t\t\tdummyAtom ({},{},{})\n\t\t}\n\t\taxis {\n\t\t\t(0, 1, 0)\n\t\t}\n\t}\n}".format(midx, midy, midz))
        # print("harmonic {\n\tcolvars\tyCOM\n\tcenters\t0\n\tforceConstant\t10\n}")
        f.write(
            "harmonicWalls {\n\tcolvars yCOM" + 
            "\n\tlowerWalls " + str(minz) + 
            "\n\tupperWalls " + str(maxz) + 
            "\n\tforceConstant {}\n}\n".format(harwall_force))

        # z colvars
        f.write("colvar {\n\tname zCOM\n\tdistanceZ {\n\t\tmain {\n\t\t\tatomNumbers {"),
        f.write(' '.join(index_list))
        f.write("}\n\t\t}\n\t\tref {\n\t\t\tdummyAtom ({},{},{})\n\t\t}\n\t\taxis {\n\t\t\t(0, 0, 1)\n\t\t}\n\t}\n}".format(midx, midy, midz))
        # print("harmonic {\n\tcolvars\tzCOM\n\tcenters\t0\n\tforceConstant\t10\n}")
        f.write(
            "harmonicWalls {\n\tcolvars zCOM" + 
            "\n\tlowerWalls " + str(minz) + 
            "\n\tupperWalls " + str(maxz) + 
            "\n\tforceConstant {}\n}".format(harwall_force))

def create_conf(file, current_npt):
    """
    Creates the configuration file for a single npt run.

    Inputs:
        file (string): file name to write to
        current_npt (int): current npt number

    Output: None
    """
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
run {}'''.format(current_npt, current_npt+1, current_npt+1, current_npt, npt_steps)
    with open(file, "w") as f:
        f.write(config)

def create_minmaxtcl(file, current_npt):
    """
    Creates the tcl file to measure the boundaries of the protein after a npt run.

    Inputs:
        file (string): file name to write to
        current_npt (int): current npt number

    Output: None
    """
    minmaxtcl = '''set psf  ubq-denatured-solvate-ionised.psf
set dcd  ubq-consec-npt{}.dcd
mol load psf $psf dcd $dcd

set sel [atomselect top "protein" frame last]
set measure [measure minmax $sel]

set outfile [open ./minmax_npt{}.dat w]
for {{set i 0}} {{$i < 2}} {{incr i}} {{
    for {{set j 0}} {{$j < 3}} {{incr j}} {{
        puts $outfile {{lindex $measure $i $j}}
    }}
}}
close $outfile
$sel delete
mol delete top'''.format(current_npt, current_npt)
    with open(file, "w") as f:
        f.write(minmaxtcl)

def create_centretcl(file, current_npt):
    """
    Creates the tcl file to identify the centre of the protein after a npt run.

    Inputs:
        file (string): file name to write to
        current_npt (int): current npt number

    Output: None
    """
    centretcl = '''set psf  ubq-denatured-solvate-ionised.psf
set dcd  ubq-consec-npt{}.dcd
mol load psf $psf dcd $dcd

set sel [atomselect top "protein" frame last]
set measure [measure center $sel]

set outfile [open ./centre_npt{}.dat w]
for {{set i 0}} {{$i < 3}} {{incr i}} {{
    puts $outfile {{lindex $measure $i}}
}}
close $outfile
$sel delete
mol delete top'''.format(current_npt, current_npt)
    with open(file, "w") as f:
        f.write(centretcl)

def measure_minmax(file, current_npt):
#     minmax_sbatch = sbatch_string("minmax_npt{}".format(current_npt))
#     wait = '''# Wait for vmd to start
# until pids=$(pidof vmd)
# do   
#     sleep 1
# done'''
#     with open(file, "w") as f:
#         f.write(minmax_sbatch)
#         f.write("\nmodule load vmd\nvmd -e minmax.tcl\n\n")
#         f.write(wait)
#         f.write("\n\nmeasure_minmax {}".format(current_npt))
    pass

def read_minmax(input):
    """
    Reads the values after measuring minmax and changes respective global variables.

    Inputs:
        input (string): file name to read from

    Output: None
    """
    array = []
    f = open(input, "r")
    line = f.readline()
    while line:
        array.append(float(line))
        line = f.readline()
    f.close()
    minx = array[0]
    miny = array[1]
    minz = array[2]
    maxx = array[3]
    maxy = array[4]
    maxz = array[5]

def read_centre(input):
    """
    Reads the values after measuring centre and changes respective global variables.

    Inputs:
        input (string): file name to read from

    Output: None
    """
    array = []
    f = open(input, "r")
    line = f.readline()
    while line:
        array.append(float(line))
    f.close()
    midx = array[0]
    midy = array[1]
    midz = array[2]

def create_sh(file):
    submit = sbatch_string()