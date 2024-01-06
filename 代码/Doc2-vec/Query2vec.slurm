#!/bin/bash

#SBATCH --job-name=s6539
#SBATCH --time=48:20:0
#SBATCH --exclusive
#SBATCH --nodes=1
#SBATCH --account=d171-s1926539

#SBATCH --partition=standard

#SBATCH --qos=standard
eval "$(/lustre/home/d171/s1926539/miniconda3/bin/conda shell.bash hook)"

conda activate


# Enforce threading to 1 in case underlying libraries are threaded
export OMP_NUM_THREADS=1

# Launch the serial job
#   Using 1 thread
python Query2vec.py
