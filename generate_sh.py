import sys
import os

def sbatch_string(job_name):
    """
    Generates a string for the sbatch file header.

    Inputs:
        job_name (string): name of the job

    Output: a string containing the header of the sbatch file
    """
    string = "#!/bin/sh\n#SBATCH --job-name={}\n#SBATCH --time=36:00:00\n#SBATCH --exclusive\n#SBATCH --partition=caslake\n#SBATCH --nodes=6\n#SBATCH --ntasks-per-node=48\n#SBATCH --account=pi-haddadian\n\n".format(str(job_name))
    return string

def create_individual_sbatch(job_num, start_npt, distance, total_runs_per_distance, npt_steps, harwall_force):
    job_name = "run{}".format(job_num)
    sbatch = sbatch_string(job_name)
    file = job_name + ".sh"
    cmd = "module load python\npython consec_colvars.py {} {} {} {} {}".format(start_npt, distance, total_runs_per_distance, npt_steps, harwall_force)
    with open(file, "w") as f:
        f.write(sbatch)
        f.write(cmd)
    return file

def create_dependency_sh(individual_shs):
    length = len(individual_shs)
    f = open("run.sh", "w")
    for i in range(length):
        if i == 0: 
            s = "job{}=$(sbatch {} | cut -f 4 -d' ')".format(i, individual_shs[i])
            f.write(s)
        else:
            s = "job{}=$(sbatch --dependency=afterok:$job{} {} | cut -f 4 -d' ')".format(i, i-1, individual_shs[i])
            f.write(s)
    f.close()

if __name__ == "__main__":
    """
    Usage: python consec_colvars.py first_npt num_npts distance total_runs_per_distance decrement_dist npt_steps harwall_force
           first_npt (int): starting npt number, the first npt to be run
           num_npts (int): total number of npts to be run
           distance (int): beginning wall distance from the minmax of the protein
           total_runs_per_distance (int): number of npts to run at each wall distance
           decrement_dist (int): amount to lower wall by
           npt_steps (int): number of steps between wall recalculation 
           harwall_force (int): force of colvars harmonic wall
    """
    first = int(sys.argv[1])
    num_npts = int(sys.argv[2])
    distance = int(sys.argv[3])
    total_runs_per_distance = int(sys.argv[4])
    decrement_dist = int(sys.argv[5])
    npt_steps = int(sys.argv[6])
    harwall_force = int(sys.argv[7])

    jobs = []

    for job in range(num_npts):
        start_npt = job * total_runs_per_distance + first
        jobs.append(create_individual_sbatch(job, start_npt, distance, total_runs_per_distance, npt_steps, harwall_force))
        distance -= decrement_dist

    create_dependency_sh(jobs)

    cmd = os.popen("sh run.sh")
    cmd.close()