# File to convert a csv file to a fasta file
# Convert mutated binders made using the predict script as 
# fold scripts (gbar) need a fasta file as input

import pandas as pd

# Load the CSV file
input_file = 'results/pareto_results/NLFR_100/esm2_ridge_ucb/pareto_proteus_esm2_ridge_ucb_100_2.csv'  # Update the file path if needed
# Path for the output FASTA file
output_fasta = 'results/pareto_results/NLFR_100/esm2_ridge_ucb/pareto_proteus_esm2_ridge_ucb_100_2.fasta'  # Path to save the FASTA file

# Read the CSV file
df = pd.read_csv(input_file)

# Specify the column names for sequence names and sequences
# Replace 'name' and 'binder_seq' with the actual column names from your CSV
name_column = 'name'
sequence_column = 'sequence'

# Ensure the necessary columns exist
if name_column not in df.columns or sequence_column not in df.columns:
    raise ValueError(f"Columns '{name_column}' and/or '{sequence_column}' not found in the file.")

# Write to FASTA format
with open(output_fasta, 'w') as fasta_file:
    for _, row in df.iterrows():
        fasta_file.write(f">{row[name_column]}\n{row[sequence_column]}\n")

print(f"FASTA file successfully created at: {output_fasta}")
