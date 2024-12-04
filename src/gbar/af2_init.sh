### General options
### –- specify queue -- voltash cabgpu gpuv100 gpua100
#BSUB -q gpuv100
### -- set the job Name --
#BSUB -J Job_name
### -- ask for number of cores (default: 1) --
#BSUB -n 4
### -- Select the resources: 1 gpu in exclusive process mode --
#BSUB -gpu "num=1:mode=exclusive_process"
### -- set walltime limit: hh:mm --  maximum 24 hours for GPU-queues right now
#BSUB -W 24:00
# request 5GB of system-memory
#BSUB -R "rusage[mem=10GB]"
### -- set the email address --
# please uncomment the following line and put in your e-mail address,
# if you want to receive e-mail notifications on a non-default address
##BSUB -u your_email_address
### -- send notification at start --
#BSUB -B
### -- send notification at completion--
#BSUB -N
### -- Specify the output and error file. %J is the job-id --
### -- -o and -e mean append, -oo and -eo mean overwrite --
#BSUB -o std/job_name_gpu_%J.out
#BSUB -e std/job_name_gpu_%J.err
# -- end of LSF options --
 
source /dtu/projects/RFdiffusion/setup.sh
 
RUN_ID="run_id"
 
mkdir -p AF2_init_guess_results_proteus
 
# ProteinMPNN 
module load proteinmpnn
silentfrompdbs path/to/PDB/directory/*.pdb > AF2_init_guess_results/${RUN_ID}.silent
cd AF2_init_guess_results_proteus
module purge
 
# AF2
module load af2_binder_design
predict.py -silent ${RUN_ID}.silent -scorefilename ${RUN_ID}.sc -outsilent ${RUN_ID}_af.silent
module purge