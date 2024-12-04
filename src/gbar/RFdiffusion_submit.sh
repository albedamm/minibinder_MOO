#!/bin/sh
### General options
### –- specify queue --
#BSUB -q gpuv100
### -- set the job Name --
#BSUB -J 2dd8_blind_1
### -- ask for number of cores (default: 1) --
#BSUB -n 8
### -- Select the resources: 1 gpu in exclusive process mode --
#BSUB -gpu "num=1:mode=exclusive_process"
### -- set walltime limit: hh:mm --  maximum 24 hours for GPU-queues right now
#BSUB -W 10:00
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
#BSUB -o /path/to/std/directory/gpu_%J.out
#BSUB -e /path/to/std/directory/gpu_%J.err
# -- end of LSF options --

# Edit the following: BSUB -J -o -e, RUN_ID, WORKING_DIR, inference.input_pdb, contigmap.contigs, hotspot

# Change RUN_ID to keep track of files/runs
RUN_ID="2dd8_blind_1"

# Set the working directory
BASE_DIR="/path/to/working/directory"
WORKING_DIR="${BASE_DIR}"
RFDIFFUSION_DIR="${WORKING_DIR}/path/to/RFdiffusion_outputs"
PROTEINMPNN_DIR="${WORKING_DIR}/path/to/ProteinMPNN_outputs"
AF_DIR="${WORKING_DIR}/path/to/AF2_outputs"
TIME_DIR="${WORKING_DIR}/time/$RUN_ID"

mkdir -p ${RFDIFFUSION_DIR}
mkdir -p ${PROTEINMPNN_DIR}
mkdir -p ${AF_DIR}
mkdir -p ${TIME_DIR}

# Set the location of the script
SCRIPT="${BASE_DIR}/path/to/RFdiffusion_submit.sh"
echo "running following script:"
cat $SCRIPT

# Will set-up paths for modules 
source /dtu/projects/RFdiffusion/setup.sh

# Start time
OVERALL_START_TIME=$(date +%s)

# Go to working directory to get the correct paths for RFdiffusion outputfolder 
cd $WORKING_DIR

# RFdiffusion 
START_TIME=$(date +%s)
module load RFdiffusion
run_inference.py inference.input_pdb=${BASE_DIR}/complex.pdb inference.output_prefix=${RFDIFFUSION_DIR}/$RUN_ID inference.num_designs=50 'contigmap.contigs=[A1-276/0 B1-100/0 C1-9/0 100-150]' 'ppi.hotspot_res=[C1,C2,C3,C4,C5,C6,C7,C8,C9]' denoiser.noise_scale_ca=0 denoiser.noise_scale_frame=0

# traj dir was so far not needed and is removed to save space
rm -rf ${RFDIFFUSION_DIR}/traj
module purge
echo "RFdiffusion done"

# RFdiffusion End time
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
# Create overview file
echo "RFdiffusion: $((END_TIME - START_TIME)) seconds" > ${TIME_DIR}/overview.txt

# ProteinMPNN 
START_TIME=$(date +%s)
module load proteinmpnn 
# compress pdb files from RFdiffusion into a silent file
silentfrompdbs ${RFDIFFUSION_DIR}/${RUN_ID}*.pdb > ${PROTEINMPNN_DIR}/$RUN_ID.silent

# Run ProteinMPNN
dl_interface_design.py -silent ${PROTEINMPNN_DIR}/$RUN_ID.silent -seqs_per_struct 2 -relax_cycles 0 -outsilent ${PROTEINMPNN_DIR}/${RUN_ID}_mpnn.silent
module purge
echo "ProteinMPNN done"

# ProteinMPNN End time
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
echo "ProteinMPNN: $((END_TIME - START_TIME)) seconds" >> ${TIME_DIR}/overview.txt

# AF2
START_TIME=$(date +%s)
module load af2_binder_design
predict.py -silent ${PROTEINMPNN_DIR}/${RUN_ID}_mpnn.silent -scorefilename ${AF_DIR}/${RUN_ID}_out.sc -outsilent ${AF_DIR}/${RUN_ID}_af2.silent
echo "AF2 done"

# AF2 End time
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
echo "AF2: $((END_TIME - START_TIME)) seconds" >> ${TIME_DIR}/overview.txt

# Overall time
DURATION=$((END_TIME - OVERALL_START_TIME))
echo "Overall time: $DURATION seconds" >> ${TIME_DIR}/overview.txt
