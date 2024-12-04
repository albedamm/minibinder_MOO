#!/bin/sh
### General options
### –- specify queue --
#BSUB -q gpuv100
### -- set the job Name --
#BSUB -J Job_name
### -- ask for number of cores (default: 1) --
#BSUB -n 8
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
#BSUB -o Job_name_gpu_%J.out
#BSUB -e Job_name_gpu_%J.err
# -- end of LSF options --

# Edit the following: BSUB -J -o -e, RUN_ID, inference.input_pdb, contigmap.contigs

# Change RUN_ID to keep track of files/runs
RUN_ID="run_id"

# Will set-up paths for modules 
source /dtu/projects/RFdiffusion/setup.sh

RFdiffusion
module load RFdiffusion
run_inference.py inference.input_pdb=input_pdb.pdb inference.output_prefix=partial_outputs/$RUN_ID inference.num_designs=100 'contigmap.contigs=[116-116/0 B117-501]' diffuser.partial_T=20 denoiser.noise_scale_ca=0 denoiser.noise_scale_frame=0
# traj dir was so far not needed and is removed to save space
rm -rf partial_outputs/traj
module purge

# ProteinMPNN 
module load proteinmpnn 
mkdir -p Binder_design_outputs
# compress pdb files from RFdiffusion into a silent file
silentfrompdbs partial_outputs/${RUN_ID}*.pdb > Binder_design_outputs/$RUN_ID.silent
cd Binder_design_outputs
dl_interface_design.py -silent $RUN_ID.silent -seqs_per_struct 2 -relax_cycles 0 -outsilent ${RUN_ID}_mpnn.silent
module purge


# AF2
module load af2_binder_design
predict.py -silent ${RUN_ID}_mpnn.silent -scorefilename ${RUN_ID}_out.sc -outsilent ${RUN_ID}_af2.silent