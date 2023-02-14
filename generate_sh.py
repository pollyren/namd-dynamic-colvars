import sys
import os

def sbatch_string(job_name: str) -> str:
    """
    Generates a string for the sbatch file header.

    Inputs:
        job_name (string): name of the job

    Output: a string containing the header of the sbatch file (string)
    """
    if cluster == 1:
        string = "#!/bin/sh\n#SBATCH --job-name={}\n#SBATCH --time=36:00:00\n#SBATCH --exclusive\n#SBATCH --partition=beagle3\n#SBATCH --nodes=1\n#SBATCH --ntasks-per-node=1\n#SBATCH --account=beagle3-exusers\n\n".format(str(job_name))
    elif cluster == 0: 
        string = "#!/bin/sh\n#SBATCH --job-name={}\n#SBATCH --time=36:00:00\n#SBATCH --exclusive\n#SBATCH --partition=caslake\n#SBATCH --nodes=1\n#SBATCH --ntasks-per-node=1\n#SBATCH --account=pi-haddadian\n\n".format(str(job_name))
    elif cluster == 2:
        string = "#!/bin/sh\n#SBATCH --job-name={}\n#SBATCH --time=36:00:00\n#SBATCH --exclusive\n#SBATCH --partition=broadwl\n#SBATCH --nodes=1\n#SBATCH --ntasks-per-node=1\n#SBATCH --account=pi-haddadian\n\n".format(str(job_name))
    return string

def create_individual_sbatch(job_num: int, start_npt: int, distance: float, total_runs_per_distance: int, npt_steps: int, harwall_force: float, option: int) -> str:
    """
    Creates individual bash submit script for each batch of runs (a single batch contains all runs with the same wall distance)

    Inputs:
        job_num (int): the job number within the total number of npt runs
        start_npt (int): the npt at which to begin the current batch
        distance (float): the wall distance from the minmax of the protein for current batch
        total_runs_per_distance (int): the number of times to continue current batch
        npt_steps (int): the number of steps between wall recalculation 
        harwall_force (float): the force of colvars harmonic wall
        option (int): 1 = set wall from edge of protein, 2 = set wall symmetric from COM of protein
        beagle/midway3 (int): 0 = midway3, 1 = beagle, 2 = midway2

    Output: the file name of the bash submit script (string)
    """
    job_name = "run{}".format(job_num)
    sbatch = sbatch_string(job_name)
    file = job_name + ".sh"
    cmd = "module load python\npython consec_colvars.py {} {} {} {} {} {} {}".format(start_npt, distance, total_runs_per_distance, npt_steps, harwall_force, option, cluster)
    with open(file, "w") as f:
        f.write(sbatch)
        f.write(cmd)
    return file

def create_dependency_sh(individual_shs: list) -> None:
    """
    Creates the master bash submit script for all jobs in system.

    Input:
        individual_sh (list): list containing all job submit scripts to be submitted

    Output: None
    """
    length = len(individual_shs)
    f = open("run.sh", "w")
    f.write("#!/bin/bash\n\n")
    for i in range(length):
        if i == 0: 
            s = "job{}=$(sbatch {} | cut -f 4 -d' ')\n".format(i, individual_shs[i])
            f.write(s)
        else:
            s = "job{}=$(sbatch --dependency=afterok:$job{} {} | cut -f 4 -d' ')\n".format(i, i-1, individual_shs[i])
            f.write(s)
    f.close()

if __name__ == "__main__":
    """
    Usage: python consec_colvars.py first_npt num_npts distance total_runs_per_distance decrement_dist npt_steps harwall_force
           first_npt (int): starting npt number, the first npt to be run
                            directory should contain relevant files with prefix ubq-consec-npt{first_npt - 1}
           num_npts (int): total number of npts to be run
           distance (int): beginning wall distance from the minmax of the protein
           total_runs_per_distance (int): number of npts to run at each wall distance
           decrement_dist (int): amount to lower wall by after each npt
           npt_steps (int): number of steps between wall recalculation 
           harwall_force (int): force of colvars harmonic wall
           option (int): 1 = set wall from edge of protein, 2 = set wall symmetric from COM of protein
           beagle/midway3 (int): 0 = midway3, 1 = beagle
    """
    if sys.argv[1] == "-h":
        print(" Usage: python generate_sh.py first_npt num_npts distance total_runs_per_distance decrement_dist npt_steps harwall_force")
        print("        first_npt (int): starting npt number, the first npt to be run")
        print("                         directory should contain relevant files with prefix ubq-consec-npt{first_npt - 1}")
        print("        num_npts (int): total number of npts to be run")
        print("        distance (float): beginning wall distance from the minmax of the protein")
        print("        total_runs_per_distance (int): number of npts to run at each wall distance")
        print("        decrement_dist (float): amount to lower wall by")
        print("        npt_steps (int): number of steps between wall recalculation")
        print("        harwall_force (float): force of colvars harmonic wall")
        print("        option (int): 1 = set wall from edge of protein, 2 = set wall symmetric from COM of protein")
        print("        beagle/midway3 (int): 0 = midway3, 1 = beagle, 2 = midway2")
        sys.exit()

    first = int(sys.argv[1])
    num_npts = int(sys.argv[2])
    distance = float(sys.argv[3])
    total_runs_per_distance = int(sys.argv[4])
    decrement_dist = float(sys.argv[5])
    npt_steps = int(sys.argv[6])
    harwall_force = float(sys.argv[7])
    option = int(sys.argv[8])
    global cluster
    cluster = int(sys.argv[9])

    jobs = []

    for job in range(num_npts):
        start_npt = job * total_runs_per_distance + first
        jobs.append(create_individual_sbatch(job, start_npt, distance, total_runs_per_distance, npt_steps, harwall_force, option))
        distance -= decrement_dist

    create_dependency_sh(jobs)

    cmd = os.popen("sh run.sh")
    cmd.close()