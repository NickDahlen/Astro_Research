#!/bin/bash -l
#SBATCH --job-name=xrismDownload
#SBATCH --output=xrismOutput.log
#SBATCH --error=xrismOutput.log
#SBATCH --time=20:00:00
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --export=ALL

set -euo pipefail

cd "$SLURM_SUBMIT_DIR"

echo "Starting job in: $(pwd)"

export CALDB="$HOME/xrism_caldb"
export CALDBCONFIG="$CALDB/caldb.config"
export CALDBALIAS="$CALDB/alias_config.fits"

source ~/miniforge3/etc/profile.d/conda.sh
conda activate henv

source "$HEADAS/headas-init.sh"

unset HEADASPROMPT
export HEADASNOQUERY=1
export HEADASLOGFILE="/tmp/heasoft_${SLURM_JOB_ID}.log"

export PFILES="/tmp/pfiles_${SLURM_JOB_ID}:$HEADAS/syspfiles"
mkdir -p "/tmp/pfiles_${SLURM_JOB_ID}"

#bash XrismDownloadTargeted 9//902001020
bash IronDownloadTargeted 3//300003010
