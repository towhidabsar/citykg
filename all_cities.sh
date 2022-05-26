#!/bin/bash

#many-jobs.sh

# This is an example script that loops over two parameters
# (from 1 to 5 for each) and submits 25 jobs to the slurm
# cluster.
#
# Author:  Ralph Bean

# Just a constant variable used throughout the script to name our jobs
#   in a meaningful way.
#SBATCH --account quality-of-life --partition debug
# basejobname="tweet_kbp"
basejobname="localwiki"

# Another constant variable used to name the slurm submission file that
#   this script is going to submit to slurm.
jobfile="city.sh"

param_limit_alpha=1

# Make an output directory if it doesn't already exist.
mkdir --p output

# Load all the required packages
#  1023  spack load py-pip
# spack load /u64kqpe
## spack load py-numpy
# spack load /qwjltbh
# spack load py-networkx
# spack load py-matplotlib
# Loop and submit all the jobs
echo
echo " * Getting ready to submit a number of jobs:"
echo
for alpha in $(seq 1 $param_limit_alpha); do
        # Give our job a meaningful name
    jobname=$basejobname-$alpha
    echo "Submitting job $jobname"

    # Setup where we want the output from each job to go
    outfile=output/output-$alpha.txt

    # "exporting" variables in bash make them available to your slurm
    # workload.
    export alpha;

    # Actually submit the job.
    sbatch  --job-name $jobname --output $outfile $jobfile
done

echo
echo " * Done submitting all those jobs (whew!)"
echo " * Now you can run the following command to see your jobs in the queue:"
echo
echo " $ squeue"
echo