#!/bin/bash -l

#SBATCH --job-name=p9Sim{$1}
#SBATCH --output=astroLog{$1}.log
#SBATCH --error=astroLog{$1}.log
#SBATCH --time=30:00:00
#SBATCH --ntasks=1
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

which python
python --version
type python


#python p9MassRun.py -r 2 -d 1 -t 10000 -ts 10000
python p9MassRun.py -r "$2" -d "$3" -t "$4" -ts "$5" -in "$1"

echo "Done!"
