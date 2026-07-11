#!/bin/bash -l
#SBATCH --job-name=planet9Sim
#SBATCH --output=astroLog.log
#SBATCH --error=astroLog.log
#SBATCH --time=10:00:00
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --export=ALL

set -euo pipefail

cd "$SLURM_SUBMIT_DIR"

echo "Starting job in: $(pwd)"

source /cluster/home/ndahle01/miniforge3/etc/profile.d/conda.sh
conda activate astro


echo "Conda env: $CONDA_DEFAULT_ENV"
which python
python --version
python -c "import sys; print(sys.executable)"
python -c "import site; print(site.getsitepackages())"

conda info --envs

echo $PATH

python p9MassRun.py -r 1
