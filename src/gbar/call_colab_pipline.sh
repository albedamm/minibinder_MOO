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
#BSUB -W 16:00
# request 5GB of system-memory
#BSUB -R "rusage[mem=10GB]"
### -- set the email address --
# please uncomment the following line and put in your e-mail address,
### -- send notification at start --
#BSUB -B
### -- send notification at completion--
#BSUB -N
### -- Specify the output and error file. %J is the job-id --
### -- -o and -e mean append, -oo and -eo mean overwrite --
#BSUB -o std/job_name_%J.out
#BSUB -e std/job_name_%J.err
# -- end of LSF options --


#!/bin/bash



# Define the path to the Python file
PYTHON_FILE="main.py"

# Check if the Python file exists
if [[ -f "$PYTHON_FILE" ]]; then
    echo "Executing Python script: $PYTHON_FILE"
    # Execute the Python script
    python "$PYTHON_FILE"
    
    # Check the exit status of the python command
    if [[ $? -eq 0 ]]; then
        echo "Script executed successfully."
    else
        echo "Script execution failed with an error."
    fi
else
    echo "Error: Python file does not exist at: $PYTHON_FILE"
fi