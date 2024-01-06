#!/bin/bash
 
#SBATCH --job-name=try
#SBATCH --time=15:20:0
#SBATCH --ntasks=1
#SBATCH --account=d171-s1926539
#SBATCH --partition=standard
#SBATCH --qos=standard
eval "$(/lustre/home/d171/s1926539/miniconda3/bin/conda shell.bash hook)"

conda activate
 
export OMP_NUM_THREADS=1
 
python determineK.py


