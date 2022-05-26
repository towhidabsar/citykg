#!/bin/bash -l
# NOTE the -l flag!

#payload.sh
 
# This is an example job file for a single core CPU bound program
# Note that all of the following statements below that begin
# with #SBATCH are actually commands to the SLURM scheduler.
# Please copy this file to your home directory and modify it
# to suit your needs.
 
# If you need any help, please email rc-help@rit.edu

# Author:  Ralph Bean
 
# Where to send mail...
#To send emails, set the adcdress below and remove one of the "#" signs.
#SBATCH --mail-user=mac9908@rit.edu
 
# notify on state change: BEGIN, END, FAIL or ALL
##SBATCH --mail-type=FAIL
 
# Request 5 minutes run time MAX, if the job runs over it will be KILLED
#SBATCH --time 0-4:00:0 #Time limit day-hrs:min:sec
##SBATCH --gres=gpu

# Put the job in the partition associated with the account and request one core
#SBATCH --account quality-of-life
#SBATCH --partition tier3
#SBATCH --ntasks=1 #This option advises the Slurm controller that job steps run within the allocation will launch a maximum of number tasks and to provide for sufficient resources.
#SBATCH -c 4
# Job memory requirements in MB=m (default), GB=g, TB=t
#SBATCH --mem=32GB
## SBATCH --output=run-%J.out
## SBATCH --error=run-%J.err
 
echo "I am a job..."
echo "The city I am processing is $alpha"
echo "And now I'm going to simulate doing work based on those parameters..."
python localwiki.py --pages 0
echo "All done with my work.  Exiting."
