# Description: Script to align folded binders with inital binder structures

import os
from pymol import cmd, stored

# Directory containing folded mutated binder PDB files
binder_dir = "results/fold/494_sample/esm2_rf_ucb/uncertainty_3/rank_001_pdb"

# Directory containing initial binder PDB files
target_dir = "data/NLFR_partial/1000_pdbs_initial_partial"

# Directory to save the output combined structures
output_dir = "results/fold/494_sample/esm2_rf_ucb/uncertainty_3/HLA_A_0201_NLFRRVWEV"

def process_structure(binder_path, target_path, output_dir):
    # Extract binder filename and split into parts
    binder_filename = os.path.basename(binder_path)
    parts = binder_filename.split('_')

    # Determine how many parts to use based on mutation count
    if "unrelaxed" in parts:  # Ensure we don't go past the `unrelaxed` keyword
        unrelaxed_index = parts.index("unrelaxed")
        if unrelaxed_index == 3:  # Single mutation case
            combined_name = "_".join(parts[:3])
        elif unrelaxed_index == 4:  # Double mutation case
            combined_name = "_".join(parts[:4])
        elif unrelaxed_index == 5:  # Triple mutation case
            combined_name = "_".join(parts[:5])
        else:
            raise ValueError("Unexpected filename format for mutations.")
    else:
        raise ValueError("Filename does not contain 'unrelaxed' as expected.")

    # Append the target name to the combined name
    combined_name += "_HLA_A_0201_NLFRRVWEV"

    # Reinitialize PyMOL session to clear old data
    cmd.reinitialize()

    # Load both structures
    cmd.load(binder_path, "structure2")
    cmd.load(target_path, "structure1")

    # Remove water molecules and ligands from both structures
    cmd.remove("resn HOH")  # Remove water molecules
    cmd.remove("hetatm")    # Remove heteroatoms (commonly used to represent ligands)

    # Get the last residue number of chain A in structure 1
    last_resi_structure1 = cmd.get_model("structure1 and chain A").atom[-1].resi

    # Calculate offset for continuous residue numbering
    offset = int(last_resi_structure1) + 1

    # Alter chain ID of all residues in structure 2 to 'B'
    cmd.alter("structure2", "chain='A'")
    cmd.sort()

    # Update residue numbers in structure 2
    cmd.alter("structure1", f'resi=str(int(resi)+{offset}-1)')
    cmd.sort()

    # Additional operations to align and clean structures
    cmd.align("structure2", "structure1 and chain A")
    cmd.remove("structure1 and chain A")
    cmd.sort()

    # Create and save the combined structure with mutation info in the filename
    output_path = os.path.join(output_dir, f"{combined_name}.pdb")
    cmd.create(combined_name, "structure1 or structure2")
    cmd.save(output_path, combined_name)

# Ensure output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Process each binder file and its corresponding complex file
for binder_filename in os.listdir(binder_dir):
    if binder_filename.endswith(".pdb"):
        binder_path = os.path.join(binder_dir, binder_filename)
        
        # Extract the binder number
        binder_number = binder_filename.split('_')[1]

        # Construct the corresponding target file name
        target_filename = f"binder_{binder_number}.pdb"
        target_path = os.path.join(target_dir, target_filename)
        
        # Check if the corresponding complex file exists
        if os.path.exists(target_path):
            process_structure(binder_path, target_path, output_dir)
