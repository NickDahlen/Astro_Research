#!/bin/bash
#SBATCH --job-name=hello_job
#SBATCH --output=hello_output.log
#SBATCH --error=hello_error.log
#SBATCH --time=00:02:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1

module load python  # Load Python if required by your system
python helloworld.py
