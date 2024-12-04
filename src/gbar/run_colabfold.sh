# Purpose: Run colabfold on the cluster
# !! Will update automatically, do not edit !!
        
        #!/bin/bash
        source /dtu/projects/RFdiffusion/setup.sh
        module load colabfold
        colabfold_batch esm2_rf_ucb/pareto_3/data/pareto_proteus_esm2_rf_ucb_494_3.fasta esm2_rf_ucb/pareto_3/pareto_proteus_esm2_rf_ucb_494_3
        