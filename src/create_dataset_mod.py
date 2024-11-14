import pandas as pd
import os

# Dictionary to map three-letter amino acid codes to one-letter codes
aa_dict = {
    'ALA': 'A', 'ARG': 'R', 'ASN': 'N', 'ASP': 'D', 'CYS': 'C',
    'GLU': 'E', 'GLN': 'Q', 'GLY': 'G', 'HIS': 'H', 'ILE': 'I',
    'LEU': 'L', 'LYS': 'K', 'MET': 'M', 'PHE': 'F', 'PRO': 'P',
    'SER': 'S', 'THR': 'T', 'TRP': 'W', 'TYR': 'Y', 'VAL': 'V',
    'SEC': 'U'  # Selenocysteine, sometimes present in proteins
}

# Directory paths for the csv and pdb files
csv_dir = 'results/af_init_results/uncertainty/blosum_rf_ucb/round_2'
pdb_dir = 'data/NLFR_moo/blosum_rf_ucb/uncertainty_2/HLA_B_0801_NLFRRVWEL'

# Target order for consistent column ordering
target_order = ['HLA_B_0801_NLFRRVWEL','HLA_B_0801_NLSRRVWEL','HLA_A_2402_NYFRRVWEF','HLA_A_0201_NLFRRVWEV', 'HLA_B_0801' ]

# A function to parse chain A sequence from a PDB file
def parse_pdb(pdb_file):
    chain_A_seq = []
    try:
        with open(pdb_file, 'r') as file:
            for line in file:
                if line.startswith("ATOM") or line.startswith("HETATM"):
                    elements = line.split()
                    if elements[4] == 'A':
                        three_letter_residue = elements[3]
                        residue_number = elements[5]
                        if three_letter_residue in aa_dict:
                            one_letter_aa = aa_dict[three_letter_residue]
                            if residue_number not in [res_num for res_num, _ in chain_A_seq]:
                                chain_A_seq.append((residue_number, one_letter_aa))
    except Exception as e:
        print(f"Error reading PDB file {pdb_file}: {e}")
    return ''.join(aa[1] for aa in chain_A_seq)

# Function to process all files and build the master dataset
def build_master_dataset(csv_dir, pdb_dir):
    master_data = []

    for csv_file in os.listdir(csv_dir):
        if csv_file.endswith('.csv'):
            # Determine target name based on target order
            target_name = "HLA_B_0801_NLFRRVWEL"  # Default
            for target in target_order:
                if target in csv_file:
                    target_name = '_'.join(csv_file.split('_')[2:-1])
                    break

            # Read the CSV file
            csv_data = pd.read_csv(os.path.join(csv_dir, csv_file))
            
            for _, row in csv_data.iterrows():
                description = row['description']
                # For 1. iteration
                #binder_nr = description.split('_')[:3]
                # For 2. iteration
                binder_nr = description.split('_')[:4]
                binder_name = '_'.join(binder_nr)
                pae_interaction = row['pae_interaction']
                plddt_binder = row['plddt_binder']

                # Set up PDB file name with default `pdb_name`
                pdb_name = '_'.join(description.split('_')[:4])
                pdb_file = f"{pdb_name}_HLA_B_0801_NLFRRVWEL.pdb"
                pdb_path = os.path.join(pdb_dir, pdb_file)

                if os.path.exists(pdb_path):
                    chain_A_seq = parse_pdb(pdb_path)
                    existing_entry = next((entry for entry in master_data if entry['binder_seq'] == chain_A_seq), None)

                    if existing_entry:
                        existing_entry[f'pae_interaction_{target_name}'] = pae_interaction
                        existing_entry[f'plddt_binder_{target_name}'] = plddt_binder
                    else:
                        master_data.append({
                            'binder_name': binder_name,
                            'binder_seq': chain_A_seq,
                            f'pae_interaction_{target_name}': pae_interaction,
                            f'plddt_binder_{target_name}': plddt_binder
                        })
                else:
                    print(f"PDB file not found: {pdb_path}")

    # Convert the master data to a DataFrame
    master_df = pd.DataFrame(master_data)

    # Sort the DataFrame by the PAE interaction score for HLA_B_0801_NLFRRVWEL in ascending order
    master_df = master_df.sort_values(by='pae_interaction_HLA_B_0801_NLFRRVWEL', ascending=True)

    # Generate the column order dynamically from target_order
    base_columns = ['binder_name', 'binder_seq']
    target_columns = []
    for target in target_order:
        target_columns.append(f'pae_interaction_{target}')
        target_columns.append(f'plddt_binder_{target}')
    
    # Combine base and target-specific columns to create the desired order
    desired_order = base_columns + target_columns

    # Reorder the columns in master_df to match `desired_order`
    master_df = master_df.reindex(columns=desired_order)

    return master_df

# Build and save the master dataset
master_dataset = build_master_dataset(csv_dir, pdb_dir)
output_csv_path = 'data/NLFR_moo/blosum_rf_ucb/uncertainty_2/blosum_rf_ucb_uncertainty_2_dataset.csv'
master_dataset.to_csv(output_csv_path, index=False)
print(f"Master dataset saved to {output_csv_path}")
